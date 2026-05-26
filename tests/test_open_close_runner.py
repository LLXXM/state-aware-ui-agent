import unittest
from unittest.mock import patch

from run_open_close_test import minimize_active_vscode_window


class OpenCloseRunnerTests(unittest.TestCase):
    @patch("run_open_close_test.time.sleep")
    @patch("run_open_close_test.pyautogui.press")
    @patch("run_open_close_test.pyautogui.hotkey")
    def test_minimizes_active_window_without_model_coordinates(
        self, hotkey, press, sleep
    ):
        minimize_active_vscode_window()

        hotkey.assert_called_once_with("alt", "space")
        press.assert_called_once_with("n")
        sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
