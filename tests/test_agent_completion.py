import logging
import unittest
from unittest.mock import Mock, patch

from see_think_act_agent import SeeThinkActAgent
from utils.agent_function_call import ComputerUse


class AgentCompletionTests(unittest.TestCase):
    def setUp(self):
        self.agent = SeeThinkActAgent.__new__(SeeThinkActAgent)
        self.agent.logger = logging.getLogger(__name__)
        self.agent.ollama_client = Mock()
        self.agent.action_executor = Mock()
        self.agent.computer_use = ComputerUse()
        self.agent.task_completed = False
        self.agent.task_status = None
        self.agent.task_answer = None
        self.agent.iteration_count = 1
        self.agent.action_history = []
        self.agent.iteration_delay = 0.5
        self.agent.post_action_delay = 1.0
        self.agent.dry_run = False
        self.agent.dry_run_action = None

    def test_text_saying_complete_does_not_end_task(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = None

        result = self.agent._execute_action({
            "message": {"content": "The task is not complete yet."},
        })

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)

    def test_invalid_mouse_action_is_not_sent_to_executor(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "left_click"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_unexpected_tool_cannot_terminate_task(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "other_tool",
            "arguments": {"action": "terminate", "status": "success"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_missing_tool_name_cannot_execute_action(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "arguments": {"action": "terminate", "status": "success"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)

    def test_structured_success_termination_completes_task(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "terminate", "status": "success"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "success")

    def test_structured_failure_termination_completes_task_as_failure(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "terminate", "status": "failure"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "failure")

    def test_answer_completes_task_and_stores_text(self):
        self.agent.dry_run = True
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "answer", "text": "42"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "answered")
        self.assertEqual(self.agent.task_answer, "42")
        self.assertEqual(self.agent.action_history[0]["outcome"], "answered")
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_checkpoint_records_observation_without_completing_task(self):
        self.agent.dry_run = True
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {
                "action": "checkpoint",
                "text": "Recording indicator is green",
            },
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)
        self.assertEqual(self.agent.action_history, [{
            "iteration": 1,
            "arguments": {
                "action": "checkpoint",
                "text": "Recording indicator is green",
            },
            "outcome": "observed",
        }])
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    @patch("see_think_act_agent.time.sleep")
    def test_executed_action_is_added_to_history(self, sleep):
        self.agent.post_action_delay = 0.2
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "type", "text": "hello"},
        }
        self.agent.action_executor.execute_computer_use_action.return_value = True

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertEqual(self.agent.action_history, [{
            "iteration": 1,
            "arguments": {"action": "type", "text": "hello"},
            "outcome": "executed",
        }])
        sleep.assert_called_once_with(0.2)

    def test_dry_run_records_action_without_executing_it(self):
        self.agent.dry_run = True
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "left_click", "coordinate": [100, 200]},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "dry_run")
        self.assertEqual(
            self.agent.dry_run_action,
            {"action": "left_click", "coordinate": [100, 200]},
        )
        self.assertEqual(self.agent.action_history[0]["outcome"], "dry_run")
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_run_returns_proposed_dry_run_action(self):
        self.agent.dry_run = True
        self.agent.max_iterations = 3
        self.agent.iteration_delay = 0.1
        self.agent.iteration_count = 0
        self.agent.conversation_history = []
        self.agent._capture_current_state = Mock(return_value=object())
        self.agent._think_and_decide = Mock(return_value={"message": {}})
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "type", "text": "hello"},
        }

        with patch("see_think_act_agent.time.sleep"):
            result = self.agent.run("Write text")

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["proposed_action"], {"action": "type", "text": "hello"})
        self.assertEqual(result["iterations"], 1)
        self.agent._capture_current_state.assert_called_once_with()
        self.agent._think_and_decide.assert_called_once()
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_run_returns_terminal_answer(self):
        self.agent.max_iterations = 3
        self.agent.iteration_delay = 0.1
        self.agent.iteration_count = 0
        self.agent.conversation_history = []
        self.agent._capture_current_state = Mock(return_value=object())
        self.agent._think_and_decide = Mock(return_value={"message": {}})
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "answer", "text": "Visible value"},
        }

        with patch("see_think_act_agent.time.sleep") as sleep:
            result = self.agent.run("Read the value on screen")

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["answer"], "Visible value")
        self.assertEqual(result["iterations"], 1)
        sleep.assert_called_once_with(0.1)

    def test_termination_without_status_is_rejected(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "terminate"},
        }

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)


if __name__ == "__main__":
    unittest.main()
