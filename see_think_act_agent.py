"""
See-Think-Act Agent for Windows 11
Autonomous agent that captures screenshots, analyzes with LLM, and performs actions
"""

import time
import json
import logging
import copy
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from PIL import ImageDraw

import config
from utils.screenshot_capture import ScreenshotCapture
from utils.ollama_client import OllamaVisionClient
from utils.action_executor import ActionExecutor
from utils.agent_function_call import ActionValidationError, ComputerUse
from utils.html_report import HtmlRunReport
from utils.llm_providers import create_provider, LLMProviderType
from utils.agent_graph import build_agent_graph, create_initial_state, finalize_state


class SeeThinkActAgent:
    """
    Autonomous AI Agent that can See, Think, and Act
    - See: Captures screenshots of the desktop
    - Think: Analyzes with Qwen3.5 model via Ollama
    - Act: Executes actions based on model's decisions
    """

    def __init__(
        self,
        provider_type: str = "ollama",
        model: Optional[str] = None,
        max_iterations: int = config.MAX_ITERATIONS,
        save_screenshots: bool = config.SAVE_SCREENSHOTS,
        screenshot_dir: str = config.SCREENSHOT_DIR,
        log_level: str = config.LOG_LEVEL,
        max_task_duration: float = config.MAX_TASK_DURATION,
        max_repeated_actions: int = config.MAX_REPEATED_ACTIONS,
        max_consecutive_failures: int = config.MAX_CONSECUTIVE_FAILURES,
        iteration_delay: float = config.ITERATION_DELAY,
        post_action_delay: float = config.POST_ACTION_DELAY,
        dry_run: bool = config.DRY_RUN,
        save_action_overlays: bool = config.SAVE_ACTION_OVERLAYS,
        verify_mouse_targets: bool = config.VERIFY_MOUSE_TARGETS,
        abort_on_mouse_verification_failure: bool = config.ABORT_ON_MOUSE_VERIFICATION_FAILURE,
        allowed_actions: Optional[set] = config.ALLOWED_ACTIONS,
        max_executed_mouse_actions: Optional[int] = config.MAX_EXECUTED_MOUSE_ACTIONS,
        model_options: Optional[Dict[str, Any]] = None,
        report_dir: Optional[str] = config.REPORT_DIR,
        additional_system_prompt: Optional[str] = None,
        checkpoint_dir: Optional[str] = None,  # Phase 3.2: Checkpointing
    ):
        """
        Initialize the See-Think-Act Agent

        Args:
            provider_type: LLM provider ("ollama", "openrouter", "openai")
            model: Model name (defaults to provider's default)
            max_iterations: Maximum number of iterations before stopping
            save_screenshots: Whether to save screenshots
            screenshot_dir: Directory to save screenshots
            log_level: Logging level
            max_task_duration: Maximum runtime in seconds; 0 disables this limit
            max_repeated_actions: Maximum identical executable actions in a row
            max_consecutive_failures: Maximum failed executable actions in a row
            iteration_delay: Pause between agent iterations in seconds
            post_action_delay: Pause after successful UI-changing actions in seconds
            dry_run: Stop before executing the first proposed desktop action
            save_action_overlays: Whether to save planned mouse targets on screenshots
            verify_mouse_targets: Require model approval of marked mouse targets
            abort_on_mouse_verification_failure: Abort when verification rejects
                a mouse target; when False, record the rejection and continue
            allowed_actions: Optional set of permitted actions; None permits the schema
            max_executed_mouse_actions: Mouse actions permitted before pausing for approval
            model_options: Optional LLM generation options
            report_dir: Directory for the incremental HTML report; None disables reporting
            additional_system_prompt: Optional application-specific UI knowledge
        """
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.screenshot_capture = ScreenshotCapture()

        # Create LLM provider
        if model is None:
            model = config.DEFAULT_MODEL_BY_PROVIDER.get(provider_type.lower(), config.MODEL_NAME)

        self.llm_provider = create_provider(
            LLMProviderType(provider_type.lower()),
            model=model,
            options=model_options,
        )

        # Get actual screen size
        screen_width, screen_height = self.screenshot_capture.get_screen_size()
        self.action_executor = ActionExecutor(
            screen_width=screen_width, screen_height=screen_height
        )

        # Configuration
        self.max_iterations = max_iterations
        self.max_task_duration = max_task_duration
        self.max_repeated_actions = max_repeated_actions
        self.max_consecutive_failures = max_consecutive_failures
        self.iteration_delay = iteration_delay
        self.post_action_delay = post_action_delay
        self.dry_run = dry_run
        self.save_screenshots = save_screenshots
        self.save_action_overlays = save_action_overlays
        self.verify_mouse_targets = verify_mouse_targets
        self.abort_on_mouse_verification_failure = abort_on_mouse_verification_failure
        self.allowed_actions = None if allowed_actions is None else set(allowed_actions)
        if max_executed_mouse_actions is not None and max_executed_mouse_actions < 0:
            raise ValueError("max_executed_mouse_actions must be zero or greater")
        self.max_executed_mouse_actions = max_executed_mouse_actions
        self.additional_system_prompt = additional_system_prompt
        self.report_dir = report_dir
        self.report = None
        self.screenshot_dir = Path(screenshot_dir)
        self.checkpoint_dir = checkpoint_dir  # Phase 3.2: Checkpointing

        # Create screenshot directory
        if self.save_screenshots:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Initialize computer use tool
        self.computer_use = ComputerUse(
            cfg={"display_width_px": 1000, "display_height_px": 1000}  # Normalized coordinates
        )
        if self.allowed_actions is not None:
            unknown_actions = self.allowed_actions - self.computer_use.ACTIONS
            if unknown_actions:
                raise ValueError(f"Unsupported allowed actions: {sorted(unknown_actions)}")

        # Build LangGraph with checkpointing
        self.graph = build_agent_graph(checkpoint_dir=self.checkpoint_dir)

        self.logger.info(f"Agent initialized with provider: {provider_type}, model: {model}")
        self.logger.info(f"Screen size: {screen_width}x{screen_height}")

    def _get_system_prompt(self) -> str:
        """Get the general behavior prompt for the agent."""
        return config.SYSTEM_PROMPT

    def _with_additional_system_prompt(self, base_prompt: str) -> str:
        """Append optional application UI context to a system instruction."""
        additional_prompt = getattr(self, "additional_system_prompt", None)
        if not additional_prompt:
            return base_prompt
        return (
            f"{base_prompt.rstrip()}\n\n"
            "Application-specific UI context:\n"
            f"{additional_prompt.strip()}"
        )

    def _prepare_tools(self) -> List[Dict[str, Any]]:
        """Prepare tool definitions for Ollama"""
        # Convert ComputerUse function to Ollama tool format
        computer_function = self.computer_use.function
        parameters = copy.deepcopy(computer_function["parameters"])
        if self.allowed_actions is not None:
            action_schema = parameters["properties"]["action"]
            action_schema["enum"] = [
                action for action in action_schema.get("enum", []) if action in self.allowed_actions
            ]
            allowed_list = ", ".join(action_schema["enum"])
            action_schema["description"] = (
                f"{action_schema.get('description', '').rstrip()}\n\n"
                f"For this task, only these actions are allowed: {allowed_list}."
            )

        tool = {
            "type": "function",
            "function": {
                "name": computer_function["name"],
                "description": computer_function["description"],
                "parameters": parameters,
            },
        }

        return [tool]

    def _save_screenshot(self, image, prefix: str = "screenshot") -> str:
        """Save screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{self.iteration_count:03d}_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        image.save(filepath)
        self.logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)

    def _capture_current_state(self):
        """Capture current screenshot"""
        self.logger.info("Capturing screenshot...")
        screenshot = self.screenshot_capture.capture_screen()
        self.current_screenshot = screenshot
        self.current_screenshot_path = None

        if self.save_screenshots:
            self.current_screenshot_path = self._save_screenshot(screenshot)

        return screenshot

    def _render_action_overlay(self, arguments: Dict[str, Any]):
        """Render the planned mouse position on the screenshot used for the decision."""
        if arguments.get("action") not in self.computer_use.MOUSE_ACTIONS:
            return None

        screenshot = getattr(self, "current_screenshot", None)
        coordinate = arguments.get("coordinate")
        if screenshot is None or not coordinate:
            return None

        overlay = screenshot.copy()
        x = int((coordinate[0] / 1000.0) * overlay.width)
        y = int((coordinate[1] / 1000.0) * overlay.height)
        radius = max(5, int(min(overlay.size) * 0.005))
        gap = radius
        arm = radius + 3
        draw = ImageDraw.Draw(overlay)

        def draw_crosshair(cx: int, cy: int, color):
            draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=color)
            draw.line((cx - arm, cy, cx - gap, cy), fill=color, width=2)
            draw.line((cx + gap, cy, cx + arm, cy), fill=color, width=2)
            draw.line((cx, cy - arm, cx, cy - gap), fill=color, width=2)
            draw.line((cx, cy + gap, cx, cy + arm), fill=color, width=2)

        if arguments.get("action") == "left_click_drag" and arguments.get("start_coordinate"):
            start_coordinate = arguments["start_coordinate"]
            start_x = int((start_coordinate[0] / 1000.0) * overlay.width)
            start_y = int((start_coordinate[1] / 1000.0) * overlay.height)
            draw_crosshair(start_x, start_y, (0, 80, 255))

        draw_crosshair(x, y, (255, 0, 0))

        return overlay

    def _save_action_overlay(self, arguments: Dict[str, Any]) -> Optional[str]:
        """Save the marked planned mouse position for review and debugging."""
        if not getattr(self, "save_screenshots", False):
            return None
        if not getattr(self, "save_action_overlays", False):
            return None

        overlay = self._render_action_overlay(arguments)
        if overlay is None:
            return None

        overlay_path = self._save_screenshot(overlay, prefix="planned_action")
        self.last_action_overlay = overlay_path
        self.logger.info(f"Planned mouse target overlay saved: {overlay_path}")
        return overlay_path

    @staticmethod
    def _prepare_mouse_verification_tools() -> List[Dict[str, Any]]:
        """Prepare the tool that records approval of one marked mouse target."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "verify_mouse_target",
                    "description": "Approve or reject the marked target of a proposed mouse action.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "decision": {
                                "type": "string",
                                "enum": ["approve", "reject"],
                                "description": "Approve only if the marker is on the requested target.",
                            },
                            "reason": {
                                "type": "string",
                                "description": "Short visual reason for the decision.",
                            },
                        },
                        "required": ["decision", "reason"],
                    },
                },
            }
        ]

    @staticmethod
    def _extract_action_intent(response: Dict[str, Any]) -> str:
        """Extract the planning model's explanation for target verification."""
        if isinstance(response, dict):
            message = response.get("message", {})
        else:
            message = getattr(response, "message", {})

        if isinstance(message, dict):
            return message.get("thinking") or message.get("content") or ""
        return getattr(message, "thinking", None) or getattr(message, "content", None) or ""

    @staticmethod
    def _action_intent_from_arguments(arguments: Dict[str, Any]) -> Optional[str]:
        """Return a short model-supplied action intent for history/reporting."""
        intent = arguments.get("intent")
        if isinstance(intent, str) and intent.strip():
            return intent.strip()
        return None

    def _run_mouse_target_verification(self, prompt: str, overlay) -> Dict[str, Any]:
        """Run the structured verifier for one marked screenshot."""
        response = self.llm_provider.chat_with_image(
            user_query=prompt,
            image=overlay,
            system_prompt=self._with_additional_system_prompt(
                "Verify only the marked mouse target. Do not propose another action."
            ),
            tools=self._prepare_mouse_verification_tools(),
        )
        tool_call = self.llm_provider.parse_computer_use_action(response)
        if not tool_call:
            return {
                "decision": "reject",
                "reason": "No structured target verification was returned.",
            }

        if "function" in tool_call:
            details = tool_call["function"]
            name = details.get("name")
            verification = details.get("arguments", {})
        else:
            name = tool_call.get("name")
            verification = tool_call.get("arguments", {})

        if isinstance(verification, str):
            try:
                verification = json.loads(verification)
            except json.JSONDecodeError:
                verification = {}

        if name != "verify_mouse_target" or not isinstance(verification, dict):
            return {
                "decision": "reject",
                "reason": "Unexpected target verification response.",
            }
        if verification.get("decision") not in {"approve", "reject"}:
            return {
                "decision": "reject",
                "reason": "Target verification omitted a valid decision.",
            }
        if not isinstance(verification.get("reason"), str):
            verification["reason"] = "No verification reason supplied."
        return verification

    def _mouse_verification_prompt(
        self,
        arguments: Dict[str, Any],
        action_intent: str,
        extra_instruction: str = "",
    ) -> str:
        """Build the prompt for one marked mouse-target verification image."""
        prompt = (
            "You are verifying a proposed desktop mouse action before it is executed. "
            f"The user's task is: {getattr(self, 'current_task', '')!r}. "
            f"The requested action is {arguments['action']!r}. "
            f"The planning model's intended target is described as: {action_intent or 'not supplied'!r}. "
            "The red center dot of the crosshair in the image is the exact click, "
            "pointer, or drag endpoint being verified; the short red arms are "
            "only visual guides and are not the target. "
            "A crosshair may cover a small part of underlying UI text or controls; "
            "account for that possible occlusion when judging the target. "
            f"Prior action history is: {self._format_action_history() or 'none'}. "
            "Verify the marked target against the planning model's intended target; "
            "do not choose a different next action. Use verify_mouse_target with "
            "decision='approve' only if the red center dot is clearly "
            "on that intended UI element. "
            "If it is misplaced, ambiguous, or unsafe, use decision='reject'."
        )
        if extra_instruction:
            prompt += " " + extra_instruction
        return prompt

    def _verify_mouse_target(self, arguments: Dict[str, Any], action_intent: str = "") -> bool:
        """Ask the model to verify a marked target before a real mouse action."""
        if arguments.get("action") == "left_click_drag" and arguments.get("start_coordinate"):
            source_arguments = dict(arguments)
            source_arguments["action"] = "mouse_move"
            source_arguments["coordinate"] = arguments["start_coordinate"]
            source_overlay = self._render_action_overlay(source_arguments)
            target_arguments = dict(arguments)
            target_arguments["action"] = "mouse_move"
            target_overlay = self._render_action_overlay(target_arguments)

            if source_overlay is None or target_overlay is None:
                self.last_mouse_verification = {
                    "decision": "reject",
                    "reason": "No marked drag verification screenshot could be rendered.",
                }
                return False

            source_prompt = self._mouse_verification_prompt(
                arguments,
                action_intent,
                (
                    "This is drag verification step 1 of 2: verify only the drag "
                    "start/source point from start_coordinate. Approve only if the "
                    "red center dot is on the intended source item, source row, or "
                    "source text described by the action intent."
                ),
            )
            source_verification = self._run_mouse_target_verification(source_prompt, source_overlay)
            if source_verification["decision"] != "approve":
                self.last_mouse_verification = {
                    "decision": "reject",
                    "reason": (
                        "Drag source rejected: "
                        f"{source_verification.get('reason', 'No reason supplied.')}"
                    ),
                    "source": source_verification,
                }
                self.logger.info(f"Mouse target verification: {self.last_mouse_verification}")
                return False

            target_prompt = self._mouse_verification_prompt(
                arguments,
                action_intent,
                (
                    "This is drag verification step 2 of 2: verify only the final "
                    "drop target from coordinate. Approve only if the red center "
                    "dot is on the intended destination/drop area described by the "
                    "action intent. If it is still on the source item, source tree, "
                    "or source list, reject it."
                ),
            )
            target_verification = self._run_mouse_target_verification(target_prompt, target_overlay)
            if target_verification["decision"] != "approve":
                self.last_mouse_verification = {
                    "decision": "reject",
                    "reason": (
                        "Drag target rejected: "
                        f"{target_verification.get('reason', 'No reason supplied.')}"
                    ),
                    "source": source_verification,
                    "target": target_verification,
                }
                self.logger.info(f"Mouse target verification: {self.last_mouse_verification}")
                return False

            self.last_mouse_verification = {
                "decision": "approve",
                "reason": "Drag source and target approved.",
                "source": source_verification,
                "target": target_verification,
            }
            self.logger.info(f"Mouse target verification: {self.last_mouse_verification}")
            return True

        overlay = self._render_action_overlay(arguments)
        if overlay is None:
            self.last_mouse_verification = {
                "decision": "reject",
                "reason": "No marked screenshot could be rendered.",
            }
            return False

        extra_instruction = ""
        if arguments.get("action") == "mouse_move":
            extra_instruction = (
                " This is a hover/mouse_move verification. Existing hover highlights "
                "or tooltips in the screenshot may still belong to the previous mouse "
                "position and may not match the red crosshair yet. Do not reject a "
                "mouse_move solely because a different nearby button is still highlighted; "
                "verify whether the red center dot itself is on the intended future "
                "hover target. If the mouse_move prepares a later drag from a tree "
                "row or text item, approve only when the red center dot is vertically "
                "centered on the intended source row/text, not on its upper edge, "
                "neighbor row, or pane title."
            )
        prompt = self._mouse_verification_prompt(arguments, action_intent, extra_instruction)
        verification = self._run_mouse_target_verification(prompt, overlay)

        self.last_mouse_verification = verification
        self.logger.info(f"Mouse target verification: {verification}")
        return verification["decision"] == "approve"

    def _format_action_history(self) -> str:
        """Summarize recent actions for the next model decision."""
        if not self.action_history:
            return ""

        history_lines = []
        for entry in self.action_history[-10:]:
            arguments = json.dumps(entry["arguments"], ensure_ascii=True, sort_keys=True)
            timestamp = entry.get("timestamp", "unknown time")
            intent = entry.get("intent")
            intent_text = f" intent={intent!r}" if intent else ""
            reason = entry.get("reason")
            reason_text = f" reason={reason!r}" if reason else ""
            history_lines.append(
                f"- {timestamp} iteration {entry['iteration']}: "
                f"{arguments}{intent_text} -> {entry['outcome']}{reason_text}"
            )

        return (
            "\n\nExecution history from this task:\n"
            + "\n".join(history_lines)
            + "\nUse the current screenshot to verify effects and do not repeat successful steps unnecessarily."
            + "\nIf a mouse action was blocked as repetition, do not retry the exact same action "
            "with the exact same coordinate and intent after only waiting; adjust the target "
            "or choose a different action based on the current screenshot."
        )

    def _record_action(
        self,
        arguments: Dict[str, Any],
        outcome: str,
        overlay_path: Optional[str] = None,
        intent: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Store a compact outcome record for later decisions."""
        entry = {
            "iteration": self.iteration_count,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "arguments": dict(arguments),
            "outcome": outcome,
        }
        if intent:
            entry["intent"] = intent
        if reason:
            entry["reason"] = reason
        if overlay_path is not None:
            entry["overlay_path"] = overlay_path
        self.action_history.append(entry)
        self.last_action_record = entry

    def _abort_task(self, reason: str) -> None:
        """Stop the task for a safety or progress reason."""
        self.task_completed = True
        self.task_status = "aborted"
        self.abort_reason = reason
        self.logger.warning(f"Task aborted: {reason}")

    def _is_action_allowed(self, arguments: Dict[str, Any]) -> bool:
        """Return whether the active task policy permits an action."""
        allowed_actions = getattr(self, "allowed_actions", None)
        return allowed_actions is None or arguments.get("action") in allowed_actions

    def _mouse_action_budget_reached(self, arguments: Dict[str, Any]) -> bool:
        """Return whether another planned mouse action needs external approval."""
        limit = getattr(self, "max_executed_mouse_actions", None)
        if limit is None or arguments.get("action") not in self.computer_use.MOUSE_ACTIONS:
            return False
        return getattr(self, "executed_mouse_actions", 0) >= limit

    @staticmethod
    def _is_executable_action(arguments: Dict[str, Any]) -> bool:
        """Return whether the action can modify or navigate the desktop."""
        return arguments.get("action") not in {"wait", "checkpoint", "answer", "terminate"}

    def _would_repeat_action_excessively(self, arguments: Dict[str, Any]) -> bool:
        """Detect an identical executable action proposed too many times in succession."""
        max_repeats = getattr(self, "max_repeated_actions", 0)
        if max_repeats <= 0 or not self._is_executable_action(arguments):
            return False

        previous_matches = 0
        for entry in reversed(self.action_history):
            if not self._is_executable_action(entry["arguments"]):
                break
            if entry["arguments"] != arguments:
                break
            previous_matches += 1

        return previous_matches >= max_repeats

    def _would_repeat_same_mouse_target_after_wait(
        self, arguments: Dict[str, Any]
    ) -> Optional[str]:
        """Detect an unchanged mouse target retried after only passive observations."""
        if arguments.get("action") not in self.computer_use.MOUSE_ACTIONS:
            return None

        coordinate = arguments.get("coordinate")
        intent = self._action_intent_from_arguments(arguments)
        if coordinate is None or intent is None:
            return None

        passive_actions = {"wait", "checkpoint"}
        for entry in reversed(self.action_history):
            previous = entry.get("arguments", {})
            previous_action = previous.get("action")
            if previous_action in passive_actions:
                continue
            if previous_action not in self.computer_use.MOUSE_ACTIONS:
                return None

            previous_intent = self._action_intent_from_arguments(previous)
            if (
                previous_action == arguments.get("action")
                and previous.get("coordinate") == coordinate
                and previous_intent == intent
            ):
                return (
                    "Same mouse action, same coordinate, and same intent were already "
                    "attempted with only wait/checkpoint observations since then. "
                    "Choose a slightly adjusted target or a different action based on "
                    "the current screenshot instead of repeating it 1:1."
                )
            return None

        return None

    def _has_too_many_failures(self) -> bool:
        """Detect consecutive failed executable actions."""
        max_failures = getattr(self, "max_consecutive_failures", 0)
        if max_failures <= 0:
            return False

        failures = 0
        for entry in reversed(self.action_history):
            if not self._is_executable_action(entry["arguments"]):
                break
            if entry["outcome"] != "failed":
                break
            failures += 1

        return failures >= max_failures

    def _runtime_limit_reached(self, start_time: float) -> bool:
        """Check and apply the configured runtime safety limit."""
        max_duration = getattr(self, "max_task_duration", 0)
        if max_duration > 0 and time.time() - start_time >= max_duration:
            self._abort_task(f"maximum task duration of {max_duration} seconds exceeded")
            return True
        return False

    def _think_and_decide(self, task: str, screenshot) -> Dict[str, Any]:
        """
        Send screenshot to model and get decision

        Args:
            task: The user's task
            screenshot: PIL Image of current screen

        Returns:
            Response from the model
        """
        self.logger.info("Thinking and deciding next action...")

        # Build the prompt
        if self.iteration_count == 1:
            user_prompt = f"Task: {task}\n\nThis is the current state of the desktop. What should I do first to accomplish this task?"
        else:
            user_prompt = f"Task: {task}\n\nThis is the current state after the previous action. What should I do next?"

        user_prompt += self._format_action_history()
        system_prompt = self._with_additional_system_prompt(self._get_system_prompt())
        self.last_user_prompt = user_prompt
        self.last_system_prompt = system_prompt

        # Prepare tools
        tools = self._prepare_tools()

        # Get response from model
        try:
            response = self.ollama_client.chat_with_image(
                user_query=user_prompt, image=screenshot, system_prompt=system_prompt, tools=tools
            )

            self.logger.info(f"Model response: {response}")
            return response

        except Exception as e:
            self.logger.error(f"Error in model inference: {e}")
            raise

    def _execute_action(self, response: Dict[str, Any]) -> bool:
        """
        Execute the action decided by the model

        Args:
            response: Response from the model

        Returns:
            True if action executed successfully
        """
        # Parse the action from response
        self.last_tool_call = None
        self.last_action_record = None
        self.last_action_overlay = None
        self.last_mouse_verification = None
        action_intent = self._extract_action_intent(response)
        action = self.llm_provider.parse_computer_use_action(response)
        self.last_tool_call = action

        if not action:
            self.logger.warning("No action found in response")
            if "message" in response and "content" in response["message"]:
                content = response["message"]["content"]
                self.logger.info(f"Model response: {content}")

            return False

        # Extract action details
        if "function" in action:
            action_details = action["function"]
            action_name = action_details.get("name")

            if isinstance(action_details.get("arguments"), str):
                arguments = json.loads(action_details["arguments"])
            else:
                arguments = action_details.get("arguments", {})
        else:
            arguments = action.get("arguments", {})
            action_name = action.get("name")

        if action_name != self.computer_use.name:
            self.logger.warning(f"Rejected unexpected tool call: {action_name!r}")
            return False

        try:
            arguments = self.computer_use.validate_arguments(arguments)
        except ActionValidationError as error:
            self.logger.warning(f"Rejected invalid model action: {error}")
            return False
        report_intent = self._action_intent_from_arguments(arguments)
        verification_intent = report_intent or action_intent

        if not self._is_action_allowed(arguments):
            self._record_action(arguments, "blocked_policy", intent=report_intent)
            self._abort_task(f"action not permitted by active policy: {arguments.get('action')}")
            return False

        # Check for termination
        if arguments.get("action") == "terminate":
            status = arguments.get("status")
            self._record_action(arguments, status, intent=report_intent)
            self.task_completed = True
            self.task_status = status
            self.logger.info(f"Task terminated with status: {self.task_status}")
            return True

        # Check for answer action (just observation)
        if arguments.get("action") == "answer":
            answer_text = arguments.get("text", "")
            self._record_action(arguments, "answered", intent=report_intent)
            self.task_completed = True
            self.task_status = "answered"
            self.task_answer = answer_text
            self.logger.info(f"Model's answer: {answer_text}")
            return True

        # Record an intermediate visual confirmation without ending the task
        if arguments.get("action") == "checkpoint":
            checkpoint_text = arguments.get("text", "")
            self._record_action(arguments, "observed", intent=report_intent)
            self.logger.info(f"Checkpoint recorded: {checkpoint_text}")
            return True

        overlay_path = self._save_action_overlay(arguments)

        if self.dry_run and self._is_executable_action(arguments):
            self._record_action(arguments, "dry_run", overlay_path, report_intent)
            self.task_completed = True
            self.task_status = "dry_run"
            self.dry_run_action = dict(arguments)
            self.logger.info(f"Dry run: would execute action: {arguments}")
            return True

        if self._would_repeat_action_excessively(arguments):
            self._record_action(arguments, "blocked_repetition", overlay_path, report_intent)
            self._abort_task(
                f"action repeated more than {self.max_repeated_actions} times: "
                f"{arguments.get('action')}"
            )
            return False

        mouse_repeat_reason = self._would_repeat_same_mouse_target_after_wait(arguments)
        if mouse_repeat_reason:
            self._record_action(
                arguments,
                "blocked_repetition",
                overlay_path,
                report_intent,
                mouse_repeat_reason,
            )
            return False

        if (
            arguments.get("action") in self.computer_use.MOUSE_ACTIONS
            and getattr(self, "verify_mouse_targets", False)
            and not self._verify_mouse_target(arguments, verification_intent)
        ):
            verification_reason = self.last_mouse_verification.get(
                "reason",
                "Mouse target verification rejected the proposed action.",
            )
            self._record_action(
                arguments,
                "blocked_verification",
                overlay_path,
                report_intent,
                verification_reason,
            )
            if getattr(self, "abort_on_mouse_verification_failure", False):
                self._abort_task(
                    "mouse target verification rejected the proposed action: "
                    f"{verification_reason}"
                )
            return False

        if self._mouse_action_budget_reached(arguments):
            self._record_action(arguments, "approval_required", overlay_path, report_intent)
            self.task_completed = True
            self.task_status = "approval_required"
            self.approval_required_action = dict(arguments)
            self.logger.info(f"Approval required before mouse action: {arguments}")
            return True

        # Execute the action
        self.logger.info(f"Executing action: {arguments}")
        if arguments.get("action") in self.computer_use.MOUSE_ACTIONS:
            self.executed_mouse_actions = getattr(self, "executed_mouse_actions", 0) + 1
        success = self.action_executor.execute_computer_use_action(
            {"name": action_name, "arguments": arguments}
        )
        self._record_action(
            arguments,
            "executed" if success else "failed",
            overlay_path,
            report_intent,
        )

        if not success and self._has_too_many_failures():
            self._abort_task(
                f"{self.max_consecutive_failures} consecutive action executions failed"
            )

        # Wait a bit after action for UI to update
        if success and arguments.get("action") != "wait":
            time.sleep(self.post_action_delay)

        return success

    def _start_report(self, task: str) -> None:
        """Create a per-run HTML report when reporting is configured."""
        report_dir = getattr(self, "report_dir", None)
        if report_dir is None:
            self.report = None
            return

        self.report = HtmlRunReport(
            report_dir=report_dir,
            title=f"Computer Use Agent Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )
        self.report.start(
            task,
            metadata={
                "model": getattr(self.ollama_client, "model", None),
                "model_options": getattr(self.ollama_client, "options", None),
                "max_iterations": self.max_iterations,
                "screenshot_dir": str(self.screenshot_dir),
                "allowed_actions": sorted(self.allowed_actions) if self.allowed_actions else None,
                "verify_mouse_targets": self.verify_mouse_targets,
                "abort_on_mouse_verification_failure": (self.abort_on_mouse_verification_failure),
            },
        )

    def _record_iteration_report(self, response: Dict[str, Any], action_success: bool) -> None:
        """Append one iteration snapshot to the HTML report."""
        report = getattr(self, "report", None)
        if report is None:
            return

        action_record = getattr(self, "last_action_record", None)
        report.add_iteration(
            {
                "iteration": self.iteration_count,
                "timestamp": getattr(
                    self,
                    "current_iteration_started_at",
                    datetime.now().isoformat(timespec="seconds"),
                ),
                "screenshot_path": getattr(self, "current_screenshot_path", None),
                "overlay_path": (action_record or {}).get("overlay_path"),
                "user_prompt": getattr(self, "last_user_prompt", None),
                "system_prompt": getattr(self, "last_system_prompt", None),
                "response": response,
                "tool_call": getattr(self, "last_tool_call", None),
                "action_record": action_record,
                "mouse_verification": getattr(self, "last_mouse_verification", None),
                "action_success": action_success,
            }
        )

    def _finish_report(self, result: Dict[str, Any]) -> None:
        """Write final result and expose the report path in the run result."""
        report = getattr(self, "report", None)
        if report is None:
            return

        result["report_path"] = str(report.report_path)
        report.finish(result)

    def run(self, task: str) -> Dict[str, Any]:
        """
        Run the agent to complete the given task using LangGraph.

        Args:
            task: The task to complete

        Returns:
            Dictionary with results including success status and message
        """
        self.logger.info(f"=" * 80)
        self.logger.info(f"Starting task: {task}")
        self.logger.info(f"=" * 80)

        # Build config dict for the graph
        graph_config = {
            "max_iterations": self.max_iterations,
            "max_task_duration": self.max_task_duration,
            "max_repeated_actions": self.max_repeated_actions,
            "max_consecutive_failures": self.max_consecutive_failures,
            "iteration_delay": self.iteration_delay,
            "post_action_delay": self.post_action_delay,
            "dry_run": self.dry_run,
            "save_screenshots": self.save_screenshots,
            "save_action_overlays": self.save_action_overlays,
            "verify_mouse_targets": self.verify_mouse_targets,
            "abort_on_mouse_verification_failure": self.abort_on_mouse_verification_failure,
            "allowed_actions": self.allowed_actions,
            "max_executed_mouse_actions": self.max_executed_mouse_actions,
            "screenshot_dir": str(self.screenshot_dir),
            "system_prompt": config.SYSTEM_PROMPT,
            "additional_system_prompt": self.additional_system_prompt,
        }

        # Create initial state
        initial_state = create_initial_state(
            task=task,
            config=graph_config,
            llm_provider=self.llm_provider,
            action_executor=self.action_executor,
            screenshot_capture=self.screenshot_capture,
            report_dir=self.report_dir,
        )

        # Run the graph
        try:
            # Generate thread_id for checkpointing (unique per task run)
            thread_id = (
                f"task-{abs(hash(task)) % 1000000:06d}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            graph_config = (
                {"configurable": {"thread_id": thread_id}} if self.checkpoint_dir else None
            )

            final_state = self.graph.invoke(initial_state, config=graph_config)
            result = finalize_state(final_state)

            self.logger.info(f"\n{'=' * 80}")
            self.logger.info(f"TASK COMPLETED: {result['message']}")
            self.logger.info(f"Status: {result['status']}")
            self.logger.info(f"Time: {result['elapsed_time']:.2f} seconds")
            self.logger.info(f"{'=' * 80}\n")

            return result

        except KeyboardInterrupt:
            self.logger.info("\nTask interrupted by user")
            result = {
                "success": False,
                "status": "interrupted",
                "message": "Task interrupted by user",
                "iterations": 0,
                "elapsed_time": 0,
            }
            return result

        except Exception as e:
            self.logger.error(f"Error during task execution: {e}", exc_info=True)
            result = {
                "success": False,
                "status": "error",
                "message": f"Error: {str(e)}",
                "iterations": 0,
                "elapsed_time": 0,
            }
            return result


def main():
    """Example usage of the agent"""
    # Initialize agent
    agent = SeeThinkActAgent()

    # Test connection
    if not agent.ollama_client.test_connection():
        print("\nWARNING: Could not connect to Ollama or model not found")
        print("Make sure Ollama is running and the model is pulled:")
        print(f"  ollama run {config.MODEL_NAME}")
        return

    # Example task
    task = "Open Notepad and type 'Hello from AI Agent!'"

    print(f"\nTask: {task}")
    print("Starting agent... (Press Ctrl+C to stop)\n")

    # Run the agent
    result = agent.run(task)

    # Print results
    print("\n" + "=" * 80)
    print("FINAL RESULT:")
    print(json.dumps(result, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    main()
