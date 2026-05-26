import logging
import unittest
from unittest.mock import Mock, patch

from PIL import Image

from see_think_act_agent import SeeThinkActAgent
from utils.agent_function_call import ComputerUse


class AgentMouseVerificationTests(unittest.TestCase):
    def setUp(self):
        self.agent = SeeThinkActAgent.__new__(SeeThinkActAgent)
        self.agent.logger = logging.getLogger(__name__)
        self.agent.ollama_client = Mock()
        self.agent.action_executor = Mock()
        self.agent.action_executor.execute_computer_use_action.return_value = True
        self.agent.computer_use = ComputerUse()
        self.agent.task_completed = False
        self.agent.task_status = None
        self.agent.abort_reason = None
        self.agent.iteration_count = 1
        self.agent.action_history = []
        self.agent.dry_run = False
        self.agent.verify_mouse_targets = True
        self.agent.save_screenshots = False
        self.agent.save_action_overlays = False
        self.agent.current_screenshot = Image.new("RGB", (1000, 1000), "white")
        self.agent.current_task = "Minimize Visual Studio Code."
        self.agent.last_mouse_verification = None
        self.agent.post_action_delay = 0.1

    def _proposed_click(self):
        return {
            "name": "computer_use",
            "arguments": {"action": "left_click", "coordinate": [900, 20]},
        }

    def _verification(self, decision, reason):
        return {
            "name": "verify_mouse_target",
            "arguments": {"decision": decision, "reason": reason},
        }

    @patch("see_think_act_agent.time.sleep")
    def test_approved_mouse_target_is_executed(self, sleep):
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            self._proposed_click(),
            self._verification("approve", "Crosshair is on the minimize button."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertEqual(self.agent.last_mouse_verification["decision"], "approve")
        self.agent.action_executor.execute_computer_use_action.assert_called_once()
        sleep.assert_called_once_with(0.1)
        verification_prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs[
            "user_query"
        ]
        self.assertIn("Minimize Visual Studio Code", verification_prompt)

    def test_rejected_mouse_target_aborts_before_execution(self):
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            self._proposed_click(),
            self._verification("reject", "Crosshair is not on a window control."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "aborted")
        self.assertIn("Crosshair is not on", self.agent.abort_reason)
        self.assertEqual(self.agent.action_history[-1]["outcome"], "blocked_verification")
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_dry_run_does_not_request_target_approval(self):
        self.agent.dry_run = True
        self.agent.ollama_client.parse_computer_use_action.return_value = self._proposed_click()

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertEqual(self.agent.task_status, "dry_run")
        self.agent.ollama_client.chat_with_image.assert_not_called()
        self.agent.action_executor.execute_computer_use_action.assert_not_called()


if __name__ == "__main__":
    unittest.main()
