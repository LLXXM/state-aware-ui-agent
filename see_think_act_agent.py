"""
See-Think-Act Agent for Windows 11
Autonomous agent that captures screenshots, analyzes with Qwen3-VL via Ollama, and performs actions
"""
import time
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

import config
from utils.screenshot_capture import ScreenshotCapture
from utils.ollama_client import OllamaVisionClient
from utils.action_executor import ActionExecutor
from utils.agent_function_call import ActionValidationError, ComputerUse


class SeeThinkActAgent:
    """
    Autonomous AI Agent that can See, Think, and Act
    - See: Captures screenshots of the desktop
    - Think: Analyzes with Qwen3-VL model via Ollama
    - Act: Executes actions based on model's decisions
    """
    
    def __init__(self,
                 model: str = config.MODEL_NAME,
                 max_iterations: int = config.MAX_ITERATIONS,
                 save_screenshots: bool = config.SAVE_SCREENSHOTS,
                 screenshot_dir: str = config.SCREENSHOT_DIR,
                 log_level: str = config.LOG_LEVEL,
                 max_task_duration: float = config.MAX_TASK_DURATION,
                 max_repeated_actions: int = config.MAX_REPEATED_ACTIONS,
                 max_consecutive_failures: int = config.MAX_CONSECUTIVE_FAILURES,
                 iteration_delay: float = config.ITERATION_DELAY,
                 post_action_delay: float = config.POST_ACTION_DELAY):
        """
        Initialize the See-Think-Act Agent
        
        Args:
            model: Ollama model name
            max_iterations: Maximum number of iterations before stopping
            save_screenshots: Whether to save screenshots
            screenshot_dir: Directory to save screenshots
            log_level: Logging level
            max_task_duration: Maximum runtime in seconds; 0 disables this limit
            max_repeated_actions: Maximum identical executable actions in a row
            max_consecutive_failures: Maximum failed executable actions in a row
            iteration_delay: Pause between agent iterations in seconds
            post_action_delay: Pause after successful UI-changing actions in seconds
        """
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.screenshot_capture = ScreenshotCapture()
        self.ollama_client = OllamaVisionClient(model=model)
        
        # Get actual screen size
        screen_width, screen_height = self.screenshot_capture.get_screen_size()
        self.action_executor = ActionExecutor(
            screen_width=screen_width,
            screen_height=screen_height
        )
        
        # Configuration
        self.max_iterations = max_iterations
        self.max_task_duration = max_task_duration
        self.max_repeated_actions = max_repeated_actions
        self.max_consecutive_failures = max_consecutive_failures
        self.iteration_delay = iteration_delay
        self.post_action_delay = post_action_delay
        self.save_screenshots = save_screenshots
        self.screenshot_dir = Path(screenshot_dir)
        
        # Create screenshot directory
        if self.save_screenshots:
            self.screenshot_dir.mkdir(exist_ok=True)
        
        # Initialize computer use tool
        self.computer_use = ComputerUse(
            cfg={
                "display_width_px": 1000,  # Normalized coordinates
                "display_height_px": 1000
            }
        )
        
        # State tracking
        self.iteration_count = 0
        self.task_completed = False
        self.task_status = None
        self.task_answer = None
        self.abort_reason = None
        self.conversation_history = []
        self.action_history = []
        
        self.logger.info(f"Agent initialized with model: {model}")
        self.logger.info(f"Screen size: {screen_width}x{screen_height}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return config.SYSTEM_PROMPT
    
    def _prepare_tools(self) -> List[Dict[str, Any]]:
        """Prepare tool definitions for Ollama"""
        # Convert ComputerUse function to Ollama tool format
        computer_function = self.computer_use.function
        
        tool = {
            "type": "function",
            "function": {
                "name": computer_function["name"],
                "description": computer_function["description"],
                "parameters": computer_function["parameters"]
            }
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
        
        if self.save_screenshots:
            self._save_screenshot(screenshot)
        
        return screenshot

    def _format_action_history(self) -> str:
        """Summarize recent actions for the next model decision."""
        if not self.action_history:
            return ""

        history_lines = []
        for entry in self.action_history[-10:]:
            arguments = json.dumps(entry["arguments"], ensure_ascii=True, sort_keys=True)
            history_lines.append(
                f"- Iteration {entry['iteration']}: {arguments} -> {entry['outcome']}"
            )

        return (
            "\n\nExecution history from this task:\n"
            + "\n".join(history_lines)
            + "\nUse the current screenshot to verify effects and do not repeat successful steps unnecessarily."
        )

    def _record_action(self, arguments: Dict[str, Any], outcome: str) -> None:
        """Store a compact outcome record for later decisions."""
        self.action_history.append({
            "iteration": self.iteration_count,
            "arguments": dict(arguments),
            "outcome": outcome,
        })

    def _abort_task(self, reason: str) -> None:
        """Stop the task for a safety or progress reason."""
        self.task_completed = True
        self.task_status = 'aborted'
        self.abort_reason = reason
        self.logger.warning(f"Task aborted: {reason}")

    @staticmethod
    def _is_executable_action(arguments: Dict[str, Any]) -> bool:
        """Return whether the action can modify or navigate the desktop."""
        return arguments.get('action') not in {'wait', 'checkpoint', 'answer', 'terminate'}

    def _would_repeat_action_excessively(self, arguments: Dict[str, Any]) -> bool:
        """Detect an identical executable action proposed too many times in succession."""
        max_repeats = getattr(self, 'max_repeated_actions', 0)
        if max_repeats <= 0 or not self._is_executable_action(arguments):
            return False

        previous_matches = 0
        for entry in reversed(self.action_history):
            if not self._is_executable_action(entry['arguments']):
                break
            if entry['arguments'] != arguments:
                break
            previous_matches += 1

        return previous_matches >= max_repeats

    def _has_too_many_failures(self) -> bool:
        """Detect consecutive failed executable actions."""
        max_failures = getattr(self, 'max_consecutive_failures', 0)
        if max_failures <= 0:
            return False

        failures = 0
        for entry in reversed(self.action_history):
            if not self._is_executable_action(entry['arguments']):
                break
            if entry['outcome'] != 'failed':
                break
            failures += 1

        return failures >= max_failures

    def _runtime_limit_reached(self, start_time: float) -> bool:
        """Check and apply the configured runtime safety limit."""
        max_duration = getattr(self, 'max_task_duration', 0)
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
        
        # Prepare tools
        tools = self._prepare_tools()
        
        # Get response from model
        try:
            response = self.ollama_client.chat_with_image(
                user_query=user_prompt,
                image=screenshot,
                system_prompt=self._get_system_prompt(),
                tools=tools
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
        action = self.ollama_client.parse_computer_use_action(response)
        
        if not action:
            self.logger.warning("No action found in response")
            if 'message' in response and 'content' in response['message']:
                content = response['message']['content']
                self.logger.info(f"Model response: {content}")

            return False
        
        # Extract action details
        if 'function' in action:
            action_details = action['function']
            action_name = action_details.get('name')
            
            if isinstance(action_details.get('arguments'), str):
                arguments = json.loads(action_details['arguments'])
            else:
                arguments = action_details.get('arguments', {})
        else:
            arguments = action.get('arguments', {})
            action_name = action.get('name')

        if action_name != self.computer_use.name:
            self.logger.warning(f"Rejected unexpected tool call: {action_name!r}")
            return False

        try:
            arguments = self.computer_use.validate_arguments(arguments)
        except ActionValidationError as error:
            self.logger.warning(f"Rejected invalid model action: {error}")
            return False
        
        # Check for termination
        if arguments.get('action') == 'terminate':
            status = arguments.get('status')
            self._record_action(arguments, status)
            self.task_completed = True
            self.task_status = status
            self.logger.info(f"Task terminated with status: {self.task_status}")
            return True
        
        # Check for answer action (just observation)
        if arguments.get('action') == 'answer':
            answer_text = arguments.get('text', '')
            self._record_action(arguments, 'answered')
            self.task_completed = True
            self.task_status = 'answered'
            self.task_answer = answer_text
            self.logger.info(f"Model's answer: {answer_text}")
            return True

        # Record an intermediate visual confirmation without ending the task
        if arguments.get('action') == 'checkpoint':
            checkpoint_text = arguments.get('text', '')
            self._record_action(arguments, 'observed')
            self.logger.info(f"Checkpoint recorded: {checkpoint_text}")
            return True

        if self._would_repeat_action_excessively(arguments):
            self._record_action(arguments, 'blocked_repetition')
            self._abort_task(
                f"action repeated more than {self.max_repeated_actions} times: "
                f"{arguments.get('action')}"
            )
            return False
        
        # Execute the action
        self.logger.info(f"Executing action: {arguments}")
        success = self.action_executor.execute_computer_use_action({
            'name': action_name,
            'arguments': arguments
        })
        self._record_action(arguments, 'executed' if success else 'failed')

        if not success and self._has_too_many_failures():
            self._abort_task(
                f"{self.max_consecutive_failures} consecutive action executions failed"
            )
        
        # Wait a bit after action for UI to update
        if success and arguments.get('action') != 'wait':
            time.sleep(self.post_action_delay)
        
        return success
    
    def run(self, task: str) -> Dict[str, Any]:
        """
        Run the agent to complete the given task
        
        Args:
            task: The task to complete
            
        Returns:
            Dictionary with results including success status and message
        """
        self.logger.info(f"=" * 80)
        self.logger.info(f"Starting task: {task}")
        self.logger.info(f"=" * 80)
        
        # Reset state
        self.iteration_count = 0
        self.task_completed = False
        self.task_status = None
        self.task_answer = None
        self.abort_reason = None
        self.conversation_history = []
        self.action_history = []
        
        start_time = time.time()
        
        try:
            while self.iteration_count < self.max_iterations and not self.task_completed:
                if self._runtime_limit_reached(start_time):
                    break

                self.iteration_count += 1
                self.logger.info(f"\n{'=' * 80}")
                self.logger.info(f"Iteration {self.iteration_count}/{self.max_iterations}")
                self.logger.info(f"{'=' * 80}")
                
                # Step 1: SEE - Capture screenshot
                screenshot = self._capture_current_state()
                
                # Step 2: THINK - Analyze and decide
                response = self._think_and_decide(task, screenshot)
                
                # Store in conversation history
                self.conversation_history.append({
                    'iteration': self.iteration_count,
                    'response': response
                })
                
                # Step 3: ACT - Execute action
                success = self._execute_action(response)
                
                if not success and not self.task_completed:
                    self.logger.warning("Action execution failed, but continuing...")
                
                # Small delay between iterations
                time.sleep(self.iteration_delay)

                if not self.task_completed:
                    self._runtime_limit_reached(start_time)
            
            # Task completion
            elapsed_time = time.time() - start_time
            
            if self.task_completed:
                message = f'Task completed in {self.iteration_count} iterations'
                if self.task_status == 'aborted':
                    message = f'Task aborted: {self.abort_reason}'
                result = {
                    'success': self.task_status in {'success', 'answered'},
                    'status': self.task_status,
                    'message': message,
                    'iterations': self.iteration_count,
                    'elapsed_time': elapsed_time
                }
                if self.abort_reason is not None:
                    result['reason'] = self.abort_reason
                if self.task_answer is not None:
                    result['answer'] = self.task_answer
                self.logger.info(f"\n{'=' * 80}")
                self.logger.info(f"TASK COMPLETED: {result['message']}")
                self.logger.info(f"Status: {self.task_status}")
                self.logger.info(f"Time: {elapsed_time:.2f} seconds")
                self.logger.info(f"{'=' * 80}\n")
            else:
                result = {
                    'success': False,
                    'status': 'timeout',
                    'message': f'Task did not complete within {self.max_iterations} iterations',
                    'iterations': self.iteration_count,
                    'elapsed_time': elapsed_time
                }
                self.logger.warning(f"\n{'=' * 80}")
                self.logger.warning(f"TASK TIMEOUT: {result['message']}")
                self.logger.warning(f"{'=' * 80}\n")
            
            return result
            
        except KeyboardInterrupt:
            self.logger.info("\nTask interrupted by user")
            return {
                'success': False,
                'status': 'interrupted',
                'message': 'Task interrupted by user',
                'iterations': self.iteration_count,
                'elapsed_time': time.time() - start_time
            }
        
        except Exception as e:
            self.logger.error(f"Error during task execution: {e}", exc_info=True)
            return {
                'success': False,
                'status': 'error',
                'message': f'Error: {str(e)}',
                'iterations': self.iteration_count,
                'elapsed_time': time.time() - start_time
            }


def main():
    """Example usage of the agent"""
    # Initialize agent
    agent = SeeThinkActAgent()
    
    # Test connection
    if not agent.ollama_client.test_connection():
        print("\nWARNING: Could not connect to Ollama or model not found")
        print("Make sure Ollama is running and the model is pulled:")
        print("  ollama run qwen3-vl:235b-cloud")
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
