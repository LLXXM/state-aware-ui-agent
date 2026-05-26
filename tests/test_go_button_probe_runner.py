import unittest
from unittest.mock import Mock, patch

from ui_tests.run_go_button_probe import main
from ui_contexts import IBAPDA_UI_CONTEXT


class GoButtonProbeRunnerTests(unittest.TestCase):
    @patch("ui_tests.run_go_button_probe.print")
    @patch("ui_tests.run_go_button_probe.restore_minimized_windows_after_test")
    @patch("ui_tests.run_go_button_probe.minimize_all_windows_for_test")
    @patch("ui_tests.run_go_button_probe.SeeThinkActAgent")
    @patch("ui_tests.run_go_button_probe.ensure_no_existing_ibapda_window_before_launch", return_value=True)
    def test_allows_only_one_real_mouse_action_before_probe_stops(
        self, ensure_no_existing, agent_class, minimize, restore, _print
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "approval_required"}
        agent_class.return_value = agent

        main()

        ensure_no_existing.assert_called_once_with()
        kwargs = agent_class.call_args.kwargs
        self.assertEqual(kwargs["max_executed_mouse_actions"], 1)
        self.assertEqual(
            kwargs["allowed_actions"],
            {"double_click", "left_click", "wait", "terminate"},
        )
        self.assertEqual(kwargs["additional_system_prompt"], IBAPDA_UI_CONTEXT)
        self.assertEqual(kwargs["screenshot_dir"], "artifacts/ui_tests/go_button_probe")
        minimize.assert_called_once_with()
        agent.run.assert_called_once()
        restore.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
