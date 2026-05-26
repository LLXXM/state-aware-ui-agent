import unittest
from unittest.mock import Mock, patch

from run_go_button_probe import main
from ui_contexts import IBAPDA_UI_CONTEXT


class GoButtonProbeRunnerTests(unittest.TestCase):
    @patch("run_go_button_probe.print")
    @patch("run_go_button_probe.restore_minimized_windows_after_test")
    @patch("run_go_button_probe.minimize_all_windows_for_test")
    @patch("run_go_button_probe.SeeThinkActAgent")
    def test_allows_only_one_real_mouse_action_before_probe_stops(
        self, agent_class, minimize, restore, _print
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "approval_required"}
        agent_class.return_value = agent

        main()

        kwargs = agent_class.call_args.kwargs
        self.assertEqual(kwargs["max_executed_mouse_actions"], 1)
        self.assertEqual(
            kwargs["allowed_actions"],
            {"double_click", "left_click", "wait", "terminate"},
        )
        self.assertEqual(kwargs["additional_system_prompt"], IBAPDA_UI_CONTEXT)
        minimize.assert_called_once_with()
        agent.run.assert_called_once()
        restore.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
