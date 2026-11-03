import logging
import unittest
from unittest.mock import Mock, patch

from PIL import Image

from see_think_act_agent import SeeThinkActAgent
from utils.agent_function_call import ComputerUse
from utils.llm_providers import create_provider, LLMProviderType


class AgentMouseVerificationTests(unittest.TestCase):
    @patch("see_think_act_agent.create_provider")
    @patch("see_think_act_agent.ActionExecutor")
    @patch("see_think_act_agent.ScreenshotCapture")
    def setUp(self, mock_screenshot_capture, mock_action_executor, mock_create_provider):
        mock_screenshot_capture.return_value.get_screen_size.return_value = (1280, 720)
        mock_action_executor.return_value = Mock()
        mock_action_executor.return_value.execute_computer_use_action.return_value = True
        mock_create_provider.return_value = Mock()

        self.agent = SeeThinkActAgent(
            provider_type="ollama",
            model="test-model",
            dry_run=False,
            verify_mouse_targets=True,
            abort_on_mouse_verification_failure=True,
            save_screenshots=False,
            save_action_overlays=False,
        )
        self.agent.llm_provider = Mock()
        self.agent.action_executor = Mock()
        self.agent.action_executor.execute_computer_use_action.return_value = True
        self.agent.computer_use = ComputerUse()
        self.agent.task_completed = False
        self.agent.task_status = None
        self.agent.abort_reason = None
        self.agent.iteration_count = 1
        self.agent.action_history = []
        self.agent.dry_run = False
        self.agent.allowed_actions = None
        self.agent.max_executed_mouse_actions = None
        self.agent.executed_mouse_actions = 0
        self.agent.approval_required_action = None
        self.agent.verify_mouse_targets = True
        self.agent.abort_on_mouse_verification_failure = True
        self.agent.save_screenshots = False
        self.agent.save_action_overlays = False
        self.agent.current_screenshot = Image.new("RGB", (1000, 1000), "white")
        self.agent.current_task = "Minimize the application window."
        self.agent.last_mouse_verification = None
        self.agent.post_action_delay = 0.1

    def _proposed_click(self):
        return {
            "name": "computer_use",
            "arguments": {"action": "left_click", "coordinate": [900, 20]},
        }

    def _proposed_click_with_intent(self, intent):
        return {
            "name": "computer_use",
            "arguments": {
                "action": "left_click",
                "coordinate": [900, 20],
                "intent": intent,
            },
        }

    def _proposed_mouse_move_with_intent(self, intent):
        return {
            "name": "computer_use",
            "arguments": {
                "action": "mouse_move",
                "coordinate": [120, 110],
                "intent": intent,
            },
        }

    def _verification(self, decision, reason):
        return {
            "name": "verify_mouse_target",
            "arguments": {"decision": decision, "reason": reason},
        }

    @patch("see_think_act_agent.time.sleep")
    def test_drag_target_is_verified_before_execution(self, sleep):
        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            {
                "name": "computer_use",
                "arguments": {
                    "action": "left_click_drag",
                    "start_coordinate": [300, 600],
                    "coordinate": [600, 600],
                },
            },
            self._verification("approve", "Source is on item"),
            self._verification("approve", "Destination is drop zone"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertEqual(self.agent.last_mouse_verification["source"]["decision"], "approve")
        self.assertEqual(self.agent.last_mouse_verification["target"]["decision"], "approve")

    @patch("see_think_act_agent.time.sleep")
    def test_drag_verification_requires_destination_not_source(self, sleep):
        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            {
                "name": "computer_use",
                "arguments": {
                    "action": "left_click_drag",
                    "start_coordinate": [300, 600],
                    "coordinate": [300, 600],
                },
            },
            self._verification("approve", "Source is on item"),
            self._verification("reject", "Destination is same as source"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertEqual(self.agent.last_mouse_verification["target"]["decision"], "reject")
        self.assertTrue(self.agent.task_completed)

    @patch("see_think_act_agent.time.sleep")
    def test_approved_mouse_target_is_executed(self, sleep):
        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click minimize button"),
            self._verification("approve", "Red crosshair is on minimize button"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.agent.action_executor.execute_computer_use_action.assert_called_once()

    @patch("see_think_act_agent.time.sleep")
    def test_approved_mouse_target_is_held_after_budget_is_spent(self, sleep):
        self.agent.max_executed_mouse_actions = 1
        self.agent.executed_mouse_actions = 1

        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click minimize button"),
            self._verification("approve", "Red crosshair is on minimize button"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        # When budget is exceeded, action is not executed but held for approval
        self.agent.action_executor.execute_computer_use_action.assert_not_called()
        self.assertEqual(self.agent.task_status, "approval_required")
        self.assertIsNotNone(self.agent.approval_required_action)

    @patch("see_think_act_agent.time.sleep")
    def test_rejected_mouse_target_aborts_before_execution(self, sleep):
        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click minimize button"),
            self._verification("reject", "Red crosshair is on title bar"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertTrue(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, "aborted")

    @patch("see_think_act_agent.time.sleep")
    def test_rejected_mouse_target_can_continue_with_history_feedback(self, sleep):
        self.agent.abort_on_mouse_verification_failure = False

        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click minimize button"),
            self._verification("reject", "Red crosshair is on title bar"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertEqual(self.agent.task_status, None)

    @patch("see_think_act_agent.time.sleep")
    def test_mouse_move_verification_mentions_stale_hover_highlights(self, sleep):
        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            self._proposed_mouse_move_with_intent("Hover over menu"),
            self._verification("approve", "Red crosshair is on menu item"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        verification_prompt = self.agent.llm_provider.chat_with_image.call_args[1]["user_query"]
        self.assertIn("existing hover highlights", verification_prompt.lower())

    @patch("see_think_act_agent.time.sleep")
    def test_mouse_verification_mentions_overlay_occlusion(self, sleep):
        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click button"),
            self._verification("approve", "Red crosshair is on button"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        verification_prompt = self.agent.llm_provider.chat_with_image.call_args[1]["user_query"]
        self.assertIn("occlusion", verification_prompt.lower())

    @patch("see_think_act_agent.time.sleep")
    def test_verification_prefers_tool_intent_for_planned_stop_target(self, sleep):
        self.agent.llm_provider.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click STOP to stop recording"),
            self._verification("approve", "Red crosshair is on STOP button"),
        ]

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertIn("STOP", self.agent.last_mouse_verification["reason"])

    @patch("see_think_act_agent.time.sleep")
    def test_dry_run_does_not_request_target_approval(self, sleep):
        self.agent.dry_run = True

        self.agent.llm_provider.parse_computer_use_action.return_value = self._proposed_click()

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.agent.llm_provider.chat_with_image.assert_not_called()


if __name__ == "__main__":
    unittest.main()
