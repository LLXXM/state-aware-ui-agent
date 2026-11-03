import logging
import unittest
from unittest.mock import Mock, patch

from see_think_act_agent import SeeThinkActAgent
from utils.agent_function_call import ComputerUse


class AgentCompletionTests(unittest.TestCase):
    @patch("see_think_act_agent.create_provider")
    @patch("see_think_act_agent.ActionExecutor")
    @patch("see_think_act_agent.ScreenshotCapture")
    def setUp(self, mock_screenshot_capture, mock_action_executor, mock_create_provider):
        mock_screenshot_capture.return_value.get_screen_size.return_value = (1280, 720)
        mock_action_executor.return_value = Mock()
        mock_create_provider.return_value = Mock()

        self.agent = SeeThinkActAgent(
            provider_type="ollama",
            model="test-model",
            dry_run=True,
            max_iterations=3,
        )
        # Set up mocks for testing internal methods
        self.agent.action_executor = Mock()
        self.agent.llm_provider = Mock()
        self.agent.screenshot_capture = Mock()
        self.agent.computer_use = ComputerUse()
        self.agent.task_completed = False
        self.agent.task_status = None
        self.agent.task_answer = None
        self.agent.iteration_count = 1
        self.agent.action_history = []
        self.agent.iteration_delay = 0.5
        self.agent.post_action_delay = 1.0
        self.agent.dry_run = True
        self.agent.dry_run_action = None
        self.agent.approval_required_action = None
        self.agent.executed_mouse_actions = 0
        self.agent.max_executed_mouse_actions = None
        self.agent.allowed_actions = None
        self.agent.max_repeated_actions = 3
        self.agent.max_consecutive_failures = 3
        self.agent.max_task_duration = 600
        self.agent.save_screenshots = False
        self.agent.save_action_overlays = True
        self.agent.verify_mouse_targets = True
        self.agent.abort_on_mouse_verification_failure = False
        self.agent.additional_system_prompt = None
        self.agent.report_dir = None
        self.agent.screenshot_dir = "agent_screenshots"
        self.agent.graph = Mock()

    def test_text_saying_complete_does_not_end_task(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = None

        result = self.agent._execute_action(
            {
                "message": {"content": "The task is not complete yet."},
            }
        )

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)

    def test_invalid_mouse_action_is_not_sent_to_executor(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "left_click"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_unexpected_tool_cannot_terminate_task(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "other_tool",
            "arguments": {"action": "terminate", "status": "success"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_missing_tool_name_cannot_execute_action(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "arguments": {"action": "terminate", "status": "success"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)

    def test_structured_success_termination_completes_task(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "terminate", "status": "success"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "success")

    def test_structured_failure_termination_completes_task_as_failure(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "terminate", "status": "failure"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "failure")

    def test_termination_without_status_is_rejected(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "terminate"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)

    def test_answer_completes_task_and_stores_text(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "answer", "text": "Visible value"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "answered")
        self.assertEqual(self.agent.task_answer, "Visible value")

    def test_checkpoint_records_observation_without_completing_task(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "checkpoint", "text": "Observed state"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertFalse(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, None)

    def test_action_history_uses_tool_intent_not_full_reasoning(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {
                "action": "left_click",
                "intent": "Click submit button",
                "coordinate": [500, 500],
            },
        }

        self.agent._execute_action({"message": {}})

        self.assertEqual(len(self.agent.action_history), 1)
        self.assertEqual(self.agent.action_history[0]["intent"], "Click submit button")

    def test_executed_action_is_added_to_history(self):
        self.agent.dry_run = False
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "type", "text": "hello", "intent": "Type greeting"},
        }
        self.agent.action_executor.execute_computer_use_action.return_value = True

        self.agent._execute_action({"message": {}})

        self.assertEqual(len(self.agent.action_history), 1)
        self.assertEqual(self.agent.action_history[0]["outcome"], "executed")

    def test_disallowed_action_aborts_before_execution(self):
        self.agent.allowed_actions = {"type"}
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {
                "action": "left_click",
                "intent": "Click button",
                "coordinate": [500, 500],
            },
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "aborted")
        self.assertIn("not permitted", self.agent.abort_reason)

    def test_run_returns_proposed_dry_run_action(self):
        self.agent.dry_run = True
        self.agent.iteration_delay = 0.1
        self.agent.max_iterations = 3
        self.agent.iteration_count = 0
        self.agent.conversation_history = []
        self.agent._capture_current_state = Mock(return_value=object())
        self.agent._think_and_decide = Mock(return_value={"message": {}})
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "type", "text": "hello"},
        }

        with patch("see_think_act_agent.time.sleep"):
            # Mock graph.invoke to return a final state for dry run
            final_state = {
                "task_completed": True,
                "task_status": "dry_run",
                "dry_run_action": {"action": "type", "text": "hello"},
                "iteration": 1,
                "start_time": 0,
                "report": None,
                "abort_reason": None,
                "task_answer": None,
                "approval_required_action": None,
                "last_action_overlay": None,
                "last_mouse_verification": None,
                "max_iterations": 3,
            }
            self.agent.graph.invoke = Mock(return_value=final_state)

            result = self.agent.run("Write text")

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["proposed_action"], {"action": "type", "text": "hello"})
        self.assertEqual(result["iterations"], 1)

    def test_run_returns_terminal_answer(self):
        self.agent.dry_run = False
        self.agent.max_iterations = 3
        self.agent.iteration_delay = 0.1
        self.agent.iteration_count = 0
        self.agent.conversation_history = []
        self.agent._capture_current_state = Mock(return_value=object())
        self.agent._think_and_decide = Mock(return_value={"message": {}})
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "answer", "text": "Visible value"},
        }

        with patch("see_think_act_agent.time.sleep") as sleep:
            final_state = {
                "task_completed": True,
                "task_status": "answered",
                "task_answer": "Visible value",
                "iteration": 1,
                "start_time": 0,
                "report": None,
                "abort_reason": None,
                "dry_run_action": None,
                "approval_required_action": None,
                "last_action_overlay": None,
                "last_mouse_verification": None,
                "max_iterations": 3,
            }
            self.agent.graph.invoke = Mock(return_value=final_state)

            result = self.agent.run("Read the value on screen")

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["answer"], "Visible value")
        self.assertEqual(result["iterations"], 1)
        # Note: graph doesn't currently implement iteration_delay sleep


if __name__ == "__main__":
    unittest.main()
