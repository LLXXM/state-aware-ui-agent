import unittest
from unittest.mock import Mock, patch

from run_open_close_test import (
    main,
    minimize_all_windows_for_test,
    restore_minimized_windows_after_test,
)


class OpenCloseRunnerTests(unittest.TestCase):
    @patch("run_open_close_test.time.sleep")
    @patch("run_open_close_test.pyautogui.hotkey")
    def test_minimizes_all_windows_without_model_coordinates(self, hotkey, sleep):
        minimize_all_windows_for_test()

        hotkey.assert_called_once_with("win", "m")
        sleep.assert_called_once_with(1)

    @patch("run_open_close_test.time.sleep")
    @patch("run_open_close_test.pyautogui.hotkey")
    def test_restores_windows_minimized_for_test(self, hotkey, sleep):
        restore_minimized_windows_after_test()

        hotkey.assert_called_once_with("win", "shift", "m")
        sleep.assert_called_once_with(1)

    @patch("run_open_close_test.print")
    @patch("run_open_close_test.restore_minimized_windows_after_test")
    @patch("run_open_close_test.minimize_all_windows_for_test")
    @patch("run_open_close_test.SeeThinkActAgent")
    def test_restores_vscode_after_agent_run(
        self, agent_class, minimize, restore, _print
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "success"}
        agent_class.return_value = agent

        main()

        minimize.assert_called_once_with()
        agent.run.assert_called_once()
        restore.assert_called_once_with()

    @patch("run_open_close_test.print")
    @patch("run_open_close_test.restore_minimized_windows_after_test")
    @patch("run_open_close_test.minimize_all_windows_for_test")
    @patch("run_open_close_test.SeeThinkActAgent")
    def test_restores_vscode_if_agent_run_raises(
        self, agent_class, minimize, restore, _print
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.side_effect = RuntimeError("failure")
        agent_class.return_value = agent

        with self.assertRaises(RuntimeError):
            main()

        minimize.assert_called_once_with()
        restore.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
