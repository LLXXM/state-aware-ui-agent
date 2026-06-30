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
        self.agent.allowed_actions = None
        self.agent.max_executed_mouse_actions = None
        self.agent.executed_mouse_actions = 0
        self.agent.approval_required_action = None
        self.agent.verify_mouse_targets = True
        self.agent.abort_on_mouse_verification_failure = True
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
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            {
                "name": "computer_use",
                "arguments": {
                    "action": "left_click_drag",
                    "start_coordinate": [300, 600],
                    "coordinate": [600, 600],
                },
            },
            self._verification("approve", "Crosshair is on the drag target."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertEqual(self.agent.last_mouse_verification["decision"], "approve")
        self.agent.ollama_client.chat_with_image.assert_called_once()
        self.agent.action_executor.execute_computer_use_action.assert_called_once()
        sleep.assert_called_once_with(0.1)

    @patch("see_think_act_agent.time.sleep")
    def test_drag_verification_requires_destination_not_source(self, sleep):
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            {
                "name": "computer_use",
                "arguments": {
                    "action": "left_click_drag",
                    "start_coordinate": [300, 600],
                    "coordinate": [600, 600],
                    "intent": "Drag GenerateSignal from the signal tree onto the trend curve.",
                },
            },
            self._verification("approve", "Crosshair is on the trend curve."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs[
            "user_query"
        ]
        self.assertIn("final drop target", prompt)
        self.assertIn("not the source item", prompt)
        self.assertIn("source tree", prompt)
        self.assertIn("wrong end of the drag", prompt)

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

    def test_approved_mouse_target_is_held_after_budget_is_spent(self):
        self.agent.max_executed_mouse_actions = 1
        self.agent.executed_mouse_actions = 1
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            self._proposed_click(),
            self._verification("approve", "Crosshair is on the requested button."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        self.assertEqual(self.agent.task_status, "approval_required")
        self.assertEqual(self.agent.approval_required_action["action"], "left_click")
        self.assertEqual(self.agent.action_history[-1]["outcome"], "approval_required")
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

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
        self.assertIn("Crosshair is not on", self.agent.action_history[-1]["reason"])
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_rejected_mouse_target_can_continue_with_history_feedback(self):
        self.agent.abort_on_mouse_verification_failure = False
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click the minimize button."),
            self._verification("reject", "Crosshair is on the close button."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertFalse(result)
        self.assertFalse(self.agent.task_completed)
        self.assertIsNone(self.agent.task_status)
        self.assertEqual(self.agent.action_history[-1]["outcome"], "blocked_verification")
        self.assertEqual(
            self.agent.action_history[-1]["reason"],
            "Crosshair is on the close button.",
        )
        history = self.agent._format_action_history()
        self.assertIn("blocked_verification", history)
        self.assertIn("Crosshair is on the close button.", history)
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    @patch("see_think_act_agent.time.sleep")
    def test_verification_prefers_tool_intent_for_planned_stop_target(self, sleep):
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent(
                "Click the center of the red STOP button."
            ),
            self._verification("approve", "Crosshair is on STOP."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}
        response = {
            "message": {
                "thinking": "Long planning text with broader workflow details."
            }
        }

        result = self.agent._execute_action(response)

        self.assertTrue(result)
        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs[
            "user_query"
        ]
        self.assertIn("Click the center of the red STOP button.", prompt)
        self.assertNotIn("Long planning text", prompt)
        self.assertIn("do not choose a different next action", prompt)

    @patch("see_think_act_agent.time.sleep")
    def test_mouse_verification_mentions_overlay_occlusion(self, sleep):
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            self._proposed_click_with_intent("Click the centered button."),
            self._verification("approve", "Crosshair is centered."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs[
            "user_query"
        ]
        self.assertIn("white action label may cover", prompt)
        self.assertIn("possible occlusion", prompt)
        self.assertIn("red center dot", prompt)
        self.assertIn("short red arms are only visual guides", prompt)

    @patch("see_think_act_agent.time.sleep")
    def test_mouse_move_verification_mentions_stale_hover_highlights(self, sleep):
        self.agent.ollama_client.parse_computer_use_action.side_effect = [
            self._proposed_mouse_move_with_intent(
                "Hover over the second design toolbar icon."
            ),
            self._verification("approve", "Crosshair is on the hover target."),
        ]
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}

        result = self.agent._execute_action({"message": {}})

        self.assertTrue(result)
        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs[
            "user_query"
        ]
        self.assertIn("hover/mouse_move verification", prompt)
        self.assertIn("previous mouse position", prompt)
        self.assertIn("Do not reject a mouse_move solely", prompt)
        self.assertIn("vertically centered on the intended source row/text", prompt)
        self.assertIn("not on its upper edge", prompt)

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
