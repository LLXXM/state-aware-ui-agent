import logging
import unittest
from unittest.mock import Mock, patch

from see_think_act_agent import SeeThinkActAgent
from utils.agent_function_call import ComputerUse


class AgentSafetyTests(unittest.TestCase):
    def setUp(self):
        self.agent = SeeThinkActAgent.__new__(SeeThinkActAgent)
        self.agent.logger = logging.getLogger(__name__)
        self.agent.ollama_client = Mock()
        self.agent.action_executor = Mock()
        self.agent.computer_use = ComputerUse()
        self.agent.iteration_count = 3
        self.agent.task_completed = False
        self.agent.task_status = None
        self.agent.task_answer = None
        self.agent.abort_reason = None
        self.agent.action_history = []
        self.agent.max_repeated_actions = 3
        self.agent.max_consecutive_failures = 3
        self.agent.max_task_duration = 600

    def _model_action(self, arguments):
        self.agent.ollama_client.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": arguments,
        }

    def test_fourth_identical_executable_action_is_blocked(self):
        repeated = {"action": "double_click", "coordinate": [200, 300]}
        self.agent.action_history = [
            {"iteration": 1, "arguments": repeated, "outcome": "executed"},
            {"iteration": 2, "arguments": repeated, "outcome": "executed"},
            {"iteration": 3, "arguments": repeated, "outcome": "executed"},
        ]
        self.agent.iteration_count = 4
        self._model_action(repeated)

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertEqual(self.agent.task_status, "aborted")
        self.assertIn("repeated", self.agent.abort_reason)
        self.assertEqual(self.agent.action_history[-1]["outcome"], "blocked_repetition")
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_checkpoint_breaks_consecutive_repeat_sequence(self):
        repeated = {"action": "left_click", "coordinate": [200, 300]}
        self.agent.action_history = [
            {"iteration": 1, "arguments": repeated, "outcome": "executed"},
            {"iteration": 2, "arguments": repeated, "outcome": "executed"},
            {
                "iteration": 3,
                "arguments": {"action": "checkpoint", "text": "Window changed"},
                "outcome": "observed",
            },
        ]
        self.agent.action_executor.execute_computer_use_action.return_value = True
        self._model_action(repeated)

        with patch("see_think_act_agent.time.sleep"):
            result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertFalse(self.agent.task_completed)

    def test_consecutive_failed_executions_abort_task(self):
        self.agent.max_repeated_actions = 0
        self.agent.action_executor.execute_computer_use_action.return_value = False
        self._model_action({"action": "key", "keys": ["enter"]})

        for iteration in range(1, 4):
            self.agent.iteration_count = iteration
            result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertEqual(self.agent.task_status, "aborted")
        self.assertIn("3 consecutive", self.agent.abort_reason)

    @patch("see_think_act_agent.time.sleep")
    @patch("see_think_act_agent.time.time", side_effect=[0, 2, 2])
    def test_runtime_limit_aborts_before_first_iteration(self, _time, _sleep):
        self.agent.max_iterations = 3
        self.agent.max_task_duration = 1
        self.agent.iteration_count = 0
        self.agent.conversation_history = []
        self.agent._capture_current_state = Mock()

        result = self.agent.run("Do work")

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "aborted")
        self.assertIn("maximum task duration", result["reason"])
        self.assertEqual(result["iterations"], 0)
        self.agent._capture_current_state.assert_not_called()


if __name__ == "__main__":
    unittest.main()
