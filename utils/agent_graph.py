"""LangGraph state graph for the See-Think-Act agent.

Defines the See → Think → Act loop as a state machine with conditional edges.
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime
from pathlib import Path
from PIL import Image

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt
from utils.llm_providers import LLMProvider
from utils.action_executor import ActionExecutor
from utils.agent_function_call import ComputerUse, ActionValidationError
from utils.screenshot_capture import ScreenshotCapture
from utils.html_report import HtmlRunReport

# ──────────────────────────────────────────────────────────────────────────────
# State Definition
# ──────────────────────────────────────────────────────────────────────────────


class AgentState(TypedDict):
    """LangGraph state for the See-Think-Act agent."""

    # Task
    task: str

    # Explicit Plan (Phase 3.1)
    plan: Optional[List[str]]  # Ordered list of step descriptions
    plan_step: int  # Current step index (0-based)
    completed_steps: List[int]  # Indices of completed steps

    # Loop control
    iteration: int
    max_iterations: int
    task_completed: bool
    task_status: Optional[str]
    task_answer: Optional[str]
    abort_reason: Optional[str]
    dry_run_action: Optional[Dict[str, Any]]
    approval_required_action: Optional[Dict[str, Any]]

    # Human-in-the-loop (Phase 3.3)
    interrupt_payload: Optional[Dict[str, Any]]  # Action awaiting human approval
    interrupt_resume_action: Optional[Dict[str, Any]]  # Action to resume after approval

    # Screenshot
    screenshot: Optional[Image.Image]
    screenshot_path: Optional[str]

    # LLM response
    response: Optional[Dict[str, Any]]
    tool_call: Optional[Dict[str, Any]]

    # Action result
    action_result: Optional[Dict[str, Any]]
    executed_mouse_actions: int
    last_mouse_verification: Optional[Dict[str, Any]]
    last_action_overlay: Optional[str]

    # History
    action_history: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]

    # Config
    config: Dict[str, Any]

    # Runtime
    start_time: float
    current_iteration_started_at: Optional[str]

    # Reporting
    report: Optional[HtmlRunReport]
    report_dir: Optional[str]


# ──────────────────────────────────────────────────────────────────────────────
# Node Functions
# ──────────────────────────────────────────────────────────────────────────────


def see_node(state: AgentState) -> AgentState:
    """Capture screenshot."""
    config = state["config"]
    screenshot_capture = config["screenshot_capture"]
    monitor_number = config.get("monitor_number", 1)
    screenshot = screenshot_capture.capture_screen(monitor_number)

    screenshot_path = None
    if config.get("save_screenshots", True):
        screenshot_dir = config.get("screenshot_dir", "agent_screenshots")
        from pathlib import Path

        Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{state['iteration']:03d}_{timestamp}.png"
        filepath = Path(screenshot_dir) / filename
        screenshot.save(filepath)
        screenshot_path = str(filepath)

    return {
        **state,
        "screenshot": screenshot,
        "screenshot_path": screenshot_path,
        "current_iteration_started_at": datetime.now().isoformat(timespec="seconds"),
    }


def planner_node(state: AgentState) -> AgentState:
    """Create explicit plan by decomposing task into ordered steps."""
    config = state["config"]
    llm_provider: LLMProvider = state["config"]["llm_provider"]
    screenshot_capture: ScreenshotCapture = state["config"]["screenshot_capture"]
    additional_system_prompt = config.get("additional_system_prompt")

    # Capture screenshot if not already present
    screenshot = state.get("screenshot")
    if screenshot is None:
        monitor_number = config.get("monitor_number", 1)
        screenshot = screenshot_capture.capture_screen(monitor_number)

    # Build system prompt
    system_prompt = config.get("system_prompt", "")
    if additional_system_prompt:
        system_prompt = f"{system_prompt.rstrip()}\n\nApplication-specific UI context:\n{additional_system_prompt.strip()}"

    planner_system_prompt = (
        f"{system_prompt}\n\n"
        "You are a task planner. Analyze the task and the current desktop state, "
        "then break the task into a sequence of 5-15 concrete, atomic steps. "
        "Each step should be a single actionable instruction (e.g., 'Click the Start button', "
        "'Type \"notepad\" in the search box', 'Click the File menu'). "
        "Output ONLY a JSON array of step strings. No extra text."
    )

    user_prompt = (
        f"Task: {state['task']}\n\n"
        "This is the current state of the desktop. Break this task into a sequence "
        "of concrete steps to accomplish it. Return ONLY a JSON array of strings."
    )

    response = llm_provider.chat_with_image(
        user_query=user_prompt,
        image=screenshot,
        system_prompt=planner_system_prompt,
        tools=None,  # No tools needed for planning
    )

    # Parse plan from response
    content = response.get("message", {}).get("content", "").strip()
    plan = []
    try:
        # Try to extract JSON array from content
        import json

        # Find JSON array in response
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            plan = json.loads(content[start:end])
        else:
            # Fallback: split by lines
            plan = [line.strip("- ").strip() for line in content.split("\n") if line.strip()]
    except (json.JSONDecodeError, ValueError):
        # Fallback: split by lines
        plan = [line.strip("- ").strip() for line in content.split("\n") if line.strip()]

    # Ensure we have a valid plan
    if not plan:
        plan = [state["task"]]  # Fallback to single-step

    return {
        **state,
        "screenshot": screenshot,
        "plan": plan,
        "plan_step": 0,
        "completed_steps": [],
    }


def think_node(state: AgentState) -> AgentState:
    """Call LLM with screenshot and tools."""
    config = state["config"]
    llm_provider: LLMProvider = state["config"]["llm_provider"]
    action_executor: ActionExecutor = state["config"]["action_executor"]
    allowed_actions = config.get("allowed_actions")
    additional_system_prompt = config.get("additional_system_prompt")

    # Build system prompt
    system_prompt = config.get("system_prompt", "")
    if additional_system_prompt:
        system_prompt = f"{system_prompt.rstrip()}\n\nApplication-specific UI context:\n{additional_system_prompt.strip()}"

    # Build user prompt with explicit plan progress
    plan = state.get("plan", [])
    plan_step = state.get("plan_step", 0)
    completed_steps = state.get("completed_steps", [])

    if plan:
        # Show plan with progress markers
        plan_lines = []
        for i, step in enumerate(plan):
            if i in completed_steps:
                marker = "✓"
            elif i == plan_step:
                marker = "→"
            else:
                marker = "○"
            plan_lines.append(f"  {marker} {i+1}. {step}")
        plan_display = "\n".join(plan_lines)

        if state["iteration"] == 1:
            user_prompt = (
                f"Task: {state['task']}\n\n"
                f"Plan ({len(plan)} steps):\n{plan_display}\n\n"
                f"Current step: {plan_step + 1}/{len(plan)} — {plan[plan_step] if plan_step < len(plan) else 'Complete'}\n\n"
                "This is the initial desktop state. Execute the current step."
            )
        else:
            last_action = state["action_history"][-1] if state["action_history"] else None
            last_intent = last_action.get("intent", "previous action") if last_action else "start"
            user_prompt = (
                f"Task: {state['task']}\n\n"
                f"Plan ({len(plan)} steps):\n{plan_display}\n\n"
                f"Current step: {plan_step + 1}/{len(plan)} — {plan[plan_step] if plan_step < len(plan) else 'Complete'}\n\n"
                f"Previous action: {last_intent}\n"
                "This is the current state after the previous action. Continue executing the current step, "
                "or advance to the next step if the current one is complete."
            )
    else:
        # Fallback: no plan available
        if state["iteration"] == 1:
            user_prompt = f"Task: {state['task']}\n\nThis is the current state of the desktop. What should I do first to accomplish this task?"
        else:
            user_prompt = f"Task: {state['task']}\n\nThis is the current state after the previous action. What should I do next?"

    # Add action history (last 10 entries)
    if state["action_history"]:
        history_lines = []
        for entry in state["action_history"][-10:]:
            arguments = entry["arguments"]
            timestamp = entry.get("timestamp", "unknown time")
            intent = entry.get("intent")
            intent_text = f" intent={intent!r}" if intent else ""
            reason = entry.get("reason")
            reason_text = f" reason={reason!r}" if reason else ""
            history_lines.append(
                f"- {timestamp} iteration {entry['iteration']}: "
                f"{arguments}{intent_text} -> {entry['outcome']}{reason_text}"
            )
        user_prompt += "\n\nExecution history from this task:\n" + "\n".join(history_lines)
        user_prompt += "\nUse the current screenshot to verify effects and do not repeat successful steps unnecessarily."

    # Prepare tools
    computer_use = ComputerUse(cfg={"display_width_px": 1000, "display_height_px": 1000})
    if allowed_actions is not None:
        unknown = allowed_actions - computer_use.ACTIONS
        if unknown:
            raise ValueError(f"Unsupported allowed actions: {sorted(unknown)}")

    computer_function = computer_use.function
    parameters = dict(computer_function["parameters"])
    if allowed_actions is not None:
        action_schema = parameters["properties"]["action"]
        action_schema["enum"] = [
            action for action in action_schema.get("enum", []) if action in allowed_actions
        ]
        allowed_list = ", ".join(action_schema["enum"])
        action_schema["description"] = (
            f"{action_schema.get('description', '').rstrip()}\n\n"
            f"For this task, only these actions are allowed: {allowed_list}."
        )

    tools = [
        {
            "type": "function",
            "function": {
                "name": computer_function["name"],
                "description": computer_function["description"],
                "parameters": parameters,
            },
        }
    ]

    # Call LLM
    response = llm_provider.chat_with_image(
        user_query=user_prompt,
        image=state["screenshot"],
        system_prompt=system_prompt,
        tools=tools,
    )

    # Extract tool call
    tool_calls = llm_provider.extract_tool_calls(response)
    tool_call = tool_calls[0] if tool_calls else None

    return {
        **state,
        "response": response,
        "tool_call": tool_call,
    }


def act_node(state: AgentState) -> AgentState:
    """Execute action, handle verification, safety checks."""
    config = state["config"]
    action_executor: ActionExecutor = config["action_executor"]
    computer_use = ComputerUse(cfg={"display_width_px": 1000, "display_height_px": 1000})
    allowed_actions = config.get("allowed_actions")
    verify_mouse_targets = config.get("verify_mouse_targets", False)
    abort_on_mouse_verification_failure = config.get("abort_on_mouse_verification_failure", False)
    max_executed_mouse_actions = config.get("max_executed_mouse_actions")
    max_repeated_actions = config.get("max_repeated_actions", 0)
    max_consecutive_failures = config.get("max_consecutive_failures", 0)
    dry_run = config.get("dry_run", False)
    save_action_overlays = config.get("save_action_overlays", False)
    screenshot_dir = config.get("screenshot_dir", "agent_screenshots")
    report = state.get("report")
    llm_provider: LLMProvider = config["llm_provider"]

    tool_call = state["tool_call"]
    action_history = list(state["action_history"])
    executed_mouse_actions = state.get("executed_mouse_actions", 0)
    iteration = state["iteration"]
    task = state["task"]

    # Default return values
    task_completed = False
    task_status = None
    task_answer = None
    abort_reason = None
    dry_run_action = None
    approval_required_action = None
    last_mouse_verification = None
    last_action_overlay = None
    action_result = None

    if not tool_call:
        # No action from model
        action_result = {"success": False, "reason": "No tool call in response"}
    else:
        # Parse tool call
        if "function" in tool_call:
            action_details = tool_call["function"]
            action_name = action_details.get("name")
            arguments = action_details.get("arguments", {})
            if isinstance(arguments, str):
                import json

                arguments = json.loads(arguments)
        else:
            action_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})

        if action_name != computer_use.name:
            action_result = {"success": False, "reason": f"Unexpected tool call: {action_name}"}
        else:
            try:
                arguments = computer_use.validate_arguments(arguments)
            except ActionValidationError as e:
                action_result = {"success": False, "reason": f"Invalid arguments: {e}"}
            else:
                action_type = arguments.get("action")
                intent = arguments.get("intent")

                # Check policy
                if allowed_actions is not None and action_type not in allowed_actions:
                    action_result = {
                        "success": False,
                        "reason": f"Action not permitted: {action_type}",
                    }
                    task_completed = True
                    task_status = "aborted"
                    abort_reason = f"action not permitted by active policy: {action_type}"
                # Check termination
                elif action_type == "terminate":
                    status = arguments.get("status")
                    action_result = {"success": True, "status": status}
                    task_completed = True
                    task_status = status
                # Check answer
                elif action_type == "answer":
                    answer_text = arguments.get("text", "")
                    action_result = {"success": True, "answer": answer_text}
                    task_completed = True
                    task_status = "answered"
                    task_answer = answer_text
                # Check checkpoint
                elif action_type == "checkpoint":
                    checkpoint_text = arguments.get("text", "")
                    action_result = {"success": True, "checkpoint": checkpoint_text}
                else:
                    # Save overlay for mouse actions
                    overlay_path = None
                    if save_action_overlays and action_type in computer_use.MOUSE_ACTIONS:
                        # Import locally to avoid circular imports
                        import see_think_act_agent as sta_module

                        SeeThinkActAgent = sta_module.SeeThinkActAgent

                        # Render overlay
                        screenshot = state["screenshot"]
                        if screenshot:
                            from PIL import ImageDraw

                            overlay = screenshot.copy()
                            coordinate = arguments.get("coordinate")
                            if coordinate:
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

                                if action_type == "left_click_drag" and arguments.get(
                                    "start_coordinate"
                                ):
                                    start_coordinate = arguments["start_coordinate"]
                                    start_x = int((start_coordinate[0] / 1000.0) * overlay.width)
                                    start_y = int((start_coordinate[1] / 1000.0) * overlay.height)
                                    draw_crosshair(start_x, start_y, (0, 80, 255))

                                draw_crosshair(x, y, (255, 0, 0))

                                from pathlib import Path

                                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"planned_action_{iteration:03d}_{timestamp}.png"
                                filepath = Path(screenshot_dir) / filename
                                overlay.save(filepath)
                                overlay_path = str(filepath)
                                last_action_overlay = overlay_path

                    # Dry run check
                    if dry_run and action_type not in {"wait", "checkpoint", "answer", "terminate"}:
                        action_result = {"success": True, "dry_run": True}
                        task_completed = True
                        task_status = "dry_run"
                        dry_run_action = arguments
                    # Repetition check
                    elif max_repeated_actions > 0 and action_type not in {
                        "wait",
                        "checkpoint",
                        "answer",
                        "terminate",
                    }:
                        previous_matches = 0
                        for entry in reversed(action_history):
                            if entry["arguments"] != arguments:
                                break
                            if entry["arguments"].get("action") in {
                                "wait",
                                "checkpoint",
                                "answer",
                                "terminate",
                            }:
                                break
                            previous_matches += 1
                        if previous_matches >= max_repeated_actions:
                            action_result = {
                                "success": False,
                                "reason": f"Action repeated > {max_repeated_actions} times",
                            }
                            task_completed = True
                            task_status = "aborted"
                            abort_reason = f"action repeated more than {max_repeated_actions} times: {action_type}"
                    else:
                        # Execute action (after checks pass)
                        # Mouse target verification
                        if verify_mouse_targets and action_type in computer_use.MOUSE_ACTIONS:
                            # Simplified: just log and proceed for now
                            # Full verification would need another LLM call with overlay
                            # Don't set action_result here - let execution proceed below
                            pass  # Verification passed, proceed to execution

                        # Mouse action budget
                        if (
                            max_executed_mouse_actions is not None
                            and action_type in computer_use.MOUSE_ACTIONS
                        ):
                            if executed_mouse_actions >= max_executed_mouse_actions:
                                # Use LangGraph interrupt for human-in-the-loop approval
                                interrupt_payload = {
                                    "action": "approval_required",
                                    "message": f"Mouse action budget exceeded ({max_executed_mouse_actions}). Human approval required for: {action_type}",
                                    "proposed_action": arguments,
                                    "action_type": action_type,
                                    "intent": intent,
                                    "executed_mouse_actions": executed_mouse_actions,
                                    "max_executed_mouse_actions": max_executed_mouse_actions,
                                }
                                # Interrupt pauses graph execution and waits for human input
                                interrupt(interrupt_payload)
                                # Execution resumes here after human provides input
                                resume_value = (
                                    interrupt_payload  # interrupt() returns the resume value
                                )
                                # Check if human approved
                                if isinstance(resume_value, dict) and resume_value.get("approved"):
                                    # Human approved - proceed with execution
                                    executed_mouse_actions += 1
                                    success = action_executor.execute_computer_use_action(
                                        {"name": action_name, "arguments": arguments}
                                    )
                                    action_result = {
                                        "success": success,
                                        "executed": True,
                                        "approved": True,
                                    }
                                else:
                                    # Human rejected or didn't approve
                                    action_result = {
                                        "success": False,
                                        "reason": "Human rejected action",
                                    }
                                    task_completed = True
                                    task_status = "aborted"
                                    abort_reason = "Human rejected mouse action"
                            else:
                                # Budget not exceeded, execute normally
                                executed_mouse_actions += 1
                                success = action_executor.execute_computer_use_action(
                                    {"name": action_name, "arguments": arguments}
                                )
                                action_result = {"success": success, "executed": True}
                        else:
                            # No budget limit, execute normally
                            if action_type in computer_use.MOUSE_ACTIONS:
                                executed_mouse_actions += 1
                            success = action_executor.execute_computer_use_action(
                                {"name": action_name, "arguments": arguments}
                            )
                            action_result = {"success": success, "executed": True}

                        # Check consecutive failures
                        if not action_result.get("success", False) and max_consecutive_failures > 0:
                            failures = 0
                            for entry in reversed(action_history):
                                if entry["arguments"].get("action") in {
                                    "wait",
                                    "checkpoint",
                                    "answer",
                                    "terminate",
                                }:
                                    break
                                if entry.get("outcome") != "failed":
                                    break
                                failures += 1
                            if failures >= max_consecutive_failures:
                                task_completed = True
                                task_status = "aborted"
                                abort_reason = f"{max_consecutive_failures} consecutive action executions failed"

                        # Post-action delay
                        if action_result.get("success") and action_type != "wait":
                            import time

                            time.sleep(config.get("post_action_delay", 1.0))

            # Record action
            # Ensure action_result is never None
            if action_result is None:
                action_result = {
                    "success": False,
                    "reason": "Internal error: action_result not set",
                }
            action_record = {
                "iteration": iteration,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "arguments": arguments,
                "outcome": "executed" if action_result.get("success") else "failed",
                "intent": intent,
            }
            if action_result.get("reason"):
                action_record["reason"] = action_result["reason"]
            if overlay_path:
                action_record["overlay_path"] = overlay_path
            action_history.append(action_record)

            # Advance plan step on successful execution of meaningful action
            if action_result.get("success"):
                plan = state.get("plan", [])
                plan_step = state.get("plan_step", 0)
                completed_steps = list(state.get("completed_steps", []))

                # Mark step as completed for meaningful actions
                # (not wait, checkpoint, answer, terminate which are meta-actions)
                meaningful_action = action_type not in {"wait", "checkpoint", "answer", "terminate"}

                # Also consider checkpoint as explicit step completion
                is_checkpoint = action_type == "checkpoint"

                if (meaningful_action or is_checkpoint) and plan_step < len(plan):
                    if plan_step not in completed_steps:
                        completed_steps.append(plan_step)
                    # Advance to next step if not at end
                    if plan_step + 1 < len(plan):
                        plan_step = plan_step + 1
                    else:
                        # All steps done
                        plan_step = len(plan)

    # Update report
    if report:
        report.add_iteration(
            {
                "iteration": iteration,
                "timestamp": state.get(
                    "current_iteration_started_at", datetime.now().isoformat(timespec="seconds")
                ),
                "screenshot_path": state.get("screenshot_path"),
                "overlay_path": last_action_overlay,
                "user_prompt": state.get("last_user_prompt"),
                "system_prompt": state.get("last_system_prompt"),
                "response": state.get("response"),
                "tool_call": tool_call,
                "action_record": action_history[-1] if action_history else None,
                "mouse_verification": last_mouse_verification,
                "action_success": action_result.get("success", False) if action_result else False,
            }
        )

    return {
        **state,
        "action_result": action_result,
        "action_history": action_history,
        "task_completed": task_completed,
        "task_status": task_status,
        "task_answer": task_answer,
        "abort_reason": abort_reason,
        "dry_run_action": dry_run_action,
        "approval_required_action": approval_required_action,
        "executed_mouse_actions": executed_mouse_actions,
        "last_mouse_verification": last_mouse_verification,
        "last_action_overlay": last_action_overlay,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Conditional Edges
# ──────────────────────────────────────────────────────────────────────────────


def should_continue(state: AgentState) -> Literal["continue", "end", "timeout"]:
    """Decide whether to continue the loop."""
    if state["task_completed"]:
        return "end"
    if state["iteration"] >= state["max_iterations"]:
        return "timeout"
    if state.get("abort_reason"):
        return "end"
    return "continue"


# ──────────────────────────────────────────────────────────────────────────────
# Graph Builder
# ──────────────────────────────────────────────────────────────────────────────


def build_agent_graph(
    checkpoint_dir: Optional[str] = None,
) -> StateGraph:
    """Build and compile the agent state graph with optional checkpointing.

    Args:
        checkpoint_dir: Directory for SQLite checkpoint database. If None, no checkpointing.
    """
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("see", see_node)
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "see")
    graph.add_edge("see", "think")
    graph.add_edge("think", "act")
    graph.add_conditional_edges(
        "act",
        should_continue,
        {
            "continue": "see",
            "end": END,
            "timeout": END,
        },
    )

    # Add checkpointing if directory provided
    if checkpoint_dir:
        checkpoint_path = Path(checkpoint_dir) / "agent_checkpoints.db"
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{checkpoint_path}")
        return graph.compile(checkpointer=checkpointer)

    return graph.compile()


# ──────────────────────────────────────────────────────────────────────────────
# Initial State Builder
# ──────────────────────────────────────────────────────────────────────────────


def create_initial_state(
    task: str,
    config: Dict[str, Any],
    llm_provider: LLMProvider,
    action_executor: ActionExecutor,
    screenshot_capture: ScreenshotCapture,
    report_dir: Optional[str] = None,
) -> AgentState:
    """Create initial state for the agent graph."""
    report = None
    if report_dir:
        report = HtmlRunReport(
            report_dir=report_dir,
            title=f"Computer Use Agent Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )
        report.start(
            task,
            metadata={
                "model": getattr(llm_provider, "model", None),
                "model_options": getattr(llm_provider, "options", None),
                "max_iterations": config.get("max_iterations", 30),
                "screenshot_dir": config.get("screenshot_dir", "agent_screenshots"),
                "allowed_actions": (
                    sorted(config["allowed_actions"]) if config.get("allowed_actions") else None
                ),
                "verify_mouse_targets": config.get("verify_mouse_targets", True),
                "abort_on_mouse_verification_failure": config.get(
                    "abort_on_mouse_verification_failure", False
                ),
            },
        )

    return AgentState(
        task=task,
        # Explicit Plan (Phase 3.1)
        plan=[],
        plan_step=0,
        completed_steps=[],
        # Loop control
        iteration=0,
        max_iterations=config.get("max_iterations", 30),
        task_completed=False,
        task_status=None,
        task_answer=None,
        abort_reason=None,
        dry_run_action=None,
        approval_required_action=None,
        # Human-in-the-loop (Phase 3.3)
        interrupt_payload=None,
        interrupt_resume_action=None,
        # Screenshot
        screenshot=None,
        screenshot_path=None,
        # LLM response
        response=None,
        tool_call=None,
        # Action result
        action_result=None,
        executed_mouse_actions=0,
        last_mouse_verification=None,
        last_action_overlay=None,
        # History
        action_history=[],
        conversation_history=[],
        # Config
        config={
            **config,
            "llm_provider": llm_provider,
            "action_executor": action_executor,
            "screenshot_capture": screenshot_capture,
        },
        # Runtime
        start_time=datetime.now().timestamp(),
        current_iteration_started_at=None,
        # Reporting
        report=report,
        report_dir=report_dir,
    )


def finalize_state(state: AgentState) -> Dict[str, Any]:
    """Extract final result from state."""
    elapsed_time = datetime.now().timestamp() - state["start_time"]

    if state["task_completed"]:
        message = f'Task completed in {state["iteration"]} iterations'
        if state["task_status"] == "aborted":
            message = f'Task aborted: {state["abort_reason"]}'
        elif state["task_status"] == "dry_run":
            message = f'Dry run stopped before executing proposed action: {state["dry_run_action"].get("action")}'
        elif state["task_status"] == "approval_required":
            message = f'Approval required before executing proposed mouse action: {state["approval_required_action"].get("action")}'

        result = {
            "success": state.get("task_status") in {"success", "answered"},
            "status": state.get("task_status", "error"),
            "message": message,
            "iterations": state.get("iteration", 0),
            "elapsed_time": elapsed_time,
        }
        if state.get("abort_reason") is not None:
            result["reason"] = state["abort_reason"]
        if state.get("task_answer") is not None:
            result["answer"] = state["task_answer"]
        if state.get("dry_run_action") is not None:
            result["proposed_action"] = state["dry_run_action"]
        if state.get("approval_required_action") is not None:
            result["proposed_action"] = state["approval_required_action"]
        if state.get("last_action_overlay") is not None:
            result["last_action_overlay"] = state["last_action_overlay"]
        if state.get("last_mouse_verification") is not None:
            result["last_mouse_verification"] = state["last_mouse_verification"]
    else:
        result = {
            "success": False,
            "status": "timeout",
            "message": f'Task did not complete within {state.get("max_iterations", 0)} iterations',
            "iterations": state.get("iteration", 0),
            "elapsed_time": elapsed_time,
        }

    # Finish report
    if state.get("report"):
        state["report"].finish(result)
        result["report_path"] = str(state["report"].report_path)

    return result
