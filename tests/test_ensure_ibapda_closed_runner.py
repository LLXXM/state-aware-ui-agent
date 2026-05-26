import json
import unittest
from unittest.mock import Mock, patch

from ui_contexts import IBAPDA_UI_CONTEXT
from ui_tests.run_ensure_ibapda_closed import main


class EnsureIbapdaClosedRunnerTests(unittest.TestCase):
    @patch("ui_tests.run_ensure_ibapda_closed.print")
    @patch("ui_tests.run_ensure_ibapda_closed.close_existing_ibapda_window_and_confirm")
    @patch("ui_tests.run_ensure_ibapda_closed.SeeThinkActAgent")
    @patch("ui_tests.run_ensure_ibapda_closed.focus_existing_ibapda_window_for_recovery")
    @patch("ui_tests.run_ensure_ibapda_closed.find_ibapda_window_handle", return_value=None)
    def test_returns_without_agent_when_no_existing_window_is_found(
        self, find_window, focus_window, agent_class, close_window, output
    ):
        main()

        find_window.assert_called_once_with()
        focus_window.assert_not_called()
        agent_class.assert_not_called()
        close_window.assert_not_called()
        result = json.loads(output.call_args.args[0])
        self.assertEqual(result["status"], "already_closed")

    @patch("ui_tests.run_ensure_ibapda_closed.print")
    @patch("ui_tests.run_ensure_ibapda_closed.close_existing_ibapda_window_and_confirm", return_value=True)
    @patch("ui_tests.run_ensure_ibapda_closed.SeeThinkActAgent")
    @patch("ui_tests.run_ensure_ibapda_closed.focus_existing_ibapda_window_for_recovery", return_value=True)
    @patch("ui_tests.run_ensure_ibapda_closed.find_ibapda_window_handle", return_value=123)
    def test_existing_window_is_stopped_and_closed_without_launch_action(
        self, find_window, focus_window, agent_class, close_window, output
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "success"}
        agent_class.return_value = agent

        main()

        find_window.assert_called_once_with()
        focus_window.assert_called_once_with()
        kwargs = agent_class.call_args.kwargs
        self.assertEqual(
            kwargs["allowed_actions"], {"left_click", "wait", "checkpoint", "terminate"}
        )
        self.assertEqual(kwargs["max_executed_mouse_actions"], 2)
        self.assertEqual(kwargs["additional_system_prompt"], IBAPDA_UI_CONTEXT)
        self.assertEqual(
            kwargs["screenshot_dir"], "artifacts/ui_tests/ensure_ibapda_closed"
        )
        task = agent.run.call_args.args[0]
        self.assertIn("Never click GO", task)
        self.assertIn("Never launch a new ibaPDA instance", task)
        self.assertIn("Never close the ibaPDA window yourself", task)
        close_window.assert_called_once_with()
        result = json.loads(output.call_args.args[0])
        self.assertTrue(result["window_closed"])

    @patch("ui_tests.run_ensure_ibapda_closed.print")
    @patch("ui_tests.run_ensure_ibapda_closed.close_existing_ibapda_window_and_confirm", return_value=False)
    @patch("ui_tests.run_ensure_ibapda_closed.SeeThinkActAgent")
    @patch("ui_tests.run_ensure_ibapda_closed.focus_existing_ibapda_window_for_recovery", return_value=True)
    @patch("ui_tests.run_ensure_ibapda_closed.find_ibapda_window_handle", return_value=123)
    def test_failed_deterministic_window_close_is_reported(
        self, _find_window, _focus_window, agent_class, close_window, output
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"success": True, "status": "success", "message": "done"}
        agent_class.return_value = agent

        main()

        close_window.assert_called_once_with()
        result = json.loads(output.call_args.args[0])
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "window_close_failed")

    @patch("ui_tests.run_ensure_ibapda_closed.print")
    @patch("ui_tests.run_ensure_ibapda_closed.close_existing_ibapda_window_and_confirm")
    @patch("ui_tests.run_ensure_ibapda_closed.SeeThinkActAgent")
    @patch("ui_tests.run_ensure_ibapda_closed.focus_existing_ibapda_window_for_recovery", return_value=False)
    @patch("ui_tests.run_ensure_ibapda_closed.find_ibapda_window_handle", return_value=123)
    def test_unfocused_detected_window_does_not_start_agent(
        self, _find_window, _focus_window, agent_class, close_window, output
    ):
        main()

        agent_class.assert_not_called()
        close_window.assert_not_called()
        result = json.loads(output.call_args.args[0])
        self.assertEqual(result["status"], "window_focus_failed")


if __name__ == "__main__":
    unittest.main()
