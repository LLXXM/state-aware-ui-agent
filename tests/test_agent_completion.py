import logging
import unittest
from unittest.mock import Mock

from see_think_act_agent import SeeThinkActAgent


class AgentCompletionTests(unittest.TestCase):
    def setUp(self):
        self.agent = SeeThinkActAgent.__new__(SeeThinkActAgent)
        self.agent.logger = logging.getLogger(__name__)
        self.agent.ollama_client = Mock()
        self.agent.action_executor = Mock()
        self.agent.task_completed = False
        self.agent.task_status = None

    def test_text_saying_complete_does_not_end_task(self):
        self.agent.ollama_client.parse_computer_use_action.return_value = None

        result = self.agent._execute_action({
            "message": {"content": "The task is not complete yet."},
        })

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)

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
