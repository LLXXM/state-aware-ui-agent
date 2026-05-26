import unittest
from unittest.mock import Mock, patch

from ui_tests.run_open_close_test import main
from ui_tests.window_setup import (
    minimize_all_windows_for_test,
    restore_minimized_windows_after_test,
)
from ui_contexts import IBAPDA_UI_CONTEXT


class OpenCloseRunnerTests(unittest.TestCase):
    @patch("ui_tests.window_setup.time.sleep")
    @patch("ui_tests.window_setup.pyautogui.hotkey")
    def test_minimizes_all_windows_without_model_coordinates(self, hotkey, sleep):
        minimize_all_windows_for_test()

        hotkey.assert_called_once_with("win", "m")
        sleep.assert_called_once_with(1)

    @patch("ui_tests.window_setup.time.sleep")
    @patch("ui_tests.window_setup.pyautogui.hotkey")
    def test_restores_windows_minimized_for_test(self, hotkey, sleep):
        restore_minimized_windows_after_test()

        hotkey.assert_called_once_with("win", "shift", "m")
        sleep.assert_called_once_with(1)

    @patch("ui_tests.run_open_close_test.print")
    @patch("ui_tests.run_open_close_test.restore_minimized_windows_after_test")
    @patch("ui_tests.run_open_close_test.minimize_all_windows_for_test")
    @patch("ui_tests.run_open_close_test.SeeThinkActAgent")
    @patch("ui_tests.run_open_close_test.ensure_no_existing_ibapda_window_before_launch", return_value=True)
    def test_restores_vscode_after_agent_run(
        self, ensure_no_existing, agent_class, minimize, restore, _print
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "success"}
        agent_class.return_value = agent

        main()

        ensure_no_existing.assert_called_once_with()
        self.assertEqual(
            agent_class.call_args.kwargs["allowed_actions"],
            {"double_click", "left_click", "wait", "terminate"},
        )
        self.assertEqual(
            agent_class.call_args.kwargs["additional_system_prompt"],
            IBAPDA_UI_CONTEXT,
        )
        self.assertEqual(
            agent_class.call_args.kwargs["screenshot_dir"],
            "artifacts/ui_tests/open_close_test",
        )
        minimize.assert_called_once_with()
        agent.run.assert_called_once()
        restore.assert_called_once_with()

    @patch("ui_tests.run_open_close_test.print")
    @patch("ui_tests.run_open_close_test.restore_minimized_windows_after_test")
    @patch("ui_tests.run_open_close_test.minimize_all_windows_for_test")
    @patch("ui_tests.run_open_close_test.SeeThinkActAgent")
    @patch("ui_tests.run_open_close_test.ensure_no_existing_ibapda_window_before_launch", return_value=True)
    def test_restores_vscode_if_agent_run_raises(
        self, ensure_no_existing, agent_class, minimize, restore, _print
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.side_effect = RuntimeError("failure")
        agent_class.return_value = agent

        with self.assertRaises(RuntimeError):
            main()

        minimize.assert_called_once_with()
        restore.assert_called_once_with()

    @patch("ui_tests.run_open_close_test.SeeThinkActAgent")
    @patch("ui_tests.run_open_close_test.ensure_no_existing_ibapda_window_before_launch", return_value=False)
    def test_existing_ibapda_window_blocks_new_launch(self, ensure_no_existing, agent_class):
        main()

        ensure_no_existing.assert_called_once_with()
        agent_class.assert_not_called()


if __name__ == "__main__":
    unittest.main()
