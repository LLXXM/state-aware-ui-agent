import unittest
from unittest.mock import Mock, patch

from run_start_stop_test import main
from ui_contexts import IBAPDA_UI_CONTEXT


class StartStopRunnerTests(unittest.TestCase):
    @patch("run_start_stop_test.print")
    @patch("run_start_stop_test.restore_minimized_windows_after_test")
    @patch("run_start_stop_test.minimize_all_windows_for_test")
    @patch("run_start_stop_test.SeeThinkActAgent")
    def test_allows_start_stop_and_two_confirmation_dialogs_with_ui_context(
        self, agent_class, minimize, restore, _print
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "success"}
        agent_class.return_value = agent

        main()

        kwargs = agent_class.call_args.kwargs
        self.assertEqual(kwargs["max_executed_mouse_actions"], 5)
        self.assertEqual(kwargs["additional_system_prompt"], IBAPDA_UI_CONTEXT)
        self.assertEqual(
            kwargs["allowed_actions"],
            {"double_click", "left_click", "wait", "checkpoint", "terminate"},
        )
        minimize.assert_called_once_with()
        agent.run.assert_called_once()
        restore.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
