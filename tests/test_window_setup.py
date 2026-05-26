import unittest
from unittest.mock import Mock, patch

import ui_tests.support.window_setup as window_setup
from ui_tests.support.window_setup import (
    close_existing_ibapda_window_and_confirm,
    focus_existing_ibapda_window_for_recovery,
)


class WindowSetupTests(unittest.TestCase):
    @patch("ui_tests.support.window_setup.ctypes.WINFUNCTYPE", side_effect=lambda *_args: lambda func: func)
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_hidden_titled_window_is_not_treated_as_existing_instance(
        self, windll, _function_type
    ):
        user32 = Mock()
        windll.user32 = user32
        user32.IsWindowVisible.return_value = False
        user32.IsIconic.return_value = False
        user32.EnumWindows.side_effect = lambda callback, _lparam: callback(123, 0)

        self.assertIsNone(window_setup.find_ibapda_window_handle())

        user32.GetWindowTextLengthW.assert_not_called()

    @patch("ui_tests.support.window_setup.ctypes.WINFUNCTYPE", side_effect=lambda *_args: lambda func: func)
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_minimized_titled_window_is_detected_for_launch_protection(
        self, windll, _function_type
    ):
        user32 = Mock()
        windll.user32 = user32
        user32.IsWindowVisible.return_value = False
        user32.IsIconic.return_value = True
        user32.GetWindowTextLengthW.return_value = len(
            "ibaPDA v8.12.0 - PM-TESTSYSTEM-A - test_layout_textanzeige"
        )
        user32.GetWindowTextW.side_effect = (
            lambda _hwnd, buffer, _length: setattr(
                buffer,
                "value",
                "ibaPDA v8.12.0 - PM-TESTSYSTEM-A - test_layout_textanzeige",
            )
        )
        user32.EnumWindows.side_effect = lambda callback, _lparam: callback(123, 0)

        self.assertEqual(window_setup.find_ibapda_window_handle(), 123)

    @patch("ui_tests.support.window_setup.ctypes.WINFUNCTYPE", side_effect=lambda *_args: lambda func: func)
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_visible_server_status_window_is_not_treated_as_client(
        self, windll, _function_type
    ):
        user32 = Mock()
        windll.user32 = user32
        user32.IsWindowVisible.return_value = True
        user32.IsIconic.return_value = False
        user32.GetWindowTextLengthW.return_value = len(
            "ibaPDA server status v8.12.0 (Acquisition is running)"
        )
        user32.GetWindowTextW.side_effect = (
            lambda _hwnd, buffer, _length: setattr(
                buffer, "value", "ibaPDA server status v8.12.0 (Acquisition is running)"
            )
        )
        user32.EnumWindows.side_effect = lambda callback, _lparam: callback(123, 0)

        self.assertIsNone(window_setup.find_ibapda_window_handle())

    @patch("ui_tests.support.window_setup.ctypes.WINFUNCTYPE", side_effect=lambda *_args: lambda func: func)
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_visible_gdi_window_is_not_treated_as_client(
        self, windll, _function_type
    ):
        user32 = Mock()
        windll.user32 = user32
        user32.IsWindowVisible.return_value = True
        user32.IsIconic.return_value = False
        user32.GetWindowTextLengthW.return_value = len("GDI+ Window (ibaPDA.exe)")
        user32.GetWindowTextW.side_effect = (
            lambda _hwnd, buffer, _length: setattr(
                buffer, "value", "GDI+ Window (ibaPDA.exe)"
            )
        )
        user32.EnumWindows.side_effect = lambda callback, _lparam: callback(123, 0)

        self.assertIsNone(window_setup.find_ibapda_window_handle())

    @patch("ui_tests.support.window_setup.time.sleep")
    @patch("ui_tests.support.window_setup.find_ibapda_window_handle", return_value=123)
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_recovery_restores_existing_window(self, windll, find_window, sleep):
        windll.user32 = Mock()
        windll.user32.IsIconic.return_value = True
        windll.user32.GetForegroundWindow.return_value = 123

        self.assertTrue(focus_existing_ibapda_window_for_recovery())

        windll.user32.ShowWindow.assert_called_once_with(123, 9)
        windll.user32.SetForegroundWindow.assert_called_once_with(123)
        sleep.assert_called_once_with(1)

    @patch("ui_tests.support.window_setup.time.sleep")
    @patch("ui_tests.support.window_setup.find_ibapda_window_handle", return_value=123)
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_recovery_does_not_restore_already_visible_window(
        self, windll, _find_window, sleep
    ):
        windll.user32 = Mock()
        windll.user32.IsIconic.return_value = False
        windll.user32.GetForegroundWindow.return_value = 123

        self.assertTrue(focus_existing_ibapda_window_for_recovery())

        windll.user32.ShowWindow.assert_not_called()
        windll.user32.SetForegroundWindow.assert_called_once_with(123)
        sleep.assert_called_once_with(1)

    @patch("ui_tests.support.window_setup.time.sleep")
    @patch("ui_tests.support.window_setup.find_ibapda_window_handle", return_value=123)
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_recovery_rejects_window_that_did_not_receive_focus(
        self, windll, _find_window, _sleep
    ):
        windll.user32 = Mock()
        windll.user32.IsIconic.return_value = False
        windll.user32.GetForegroundWindow.return_value = 456

        self.assertFalse(focus_existing_ibapda_window_for_recovery())

    @patch("ui_tests.support.window_setup.time.sleep")
    @patch("ui_tests.support.window_setup.find_ibapda_window_handle", side_effect=[123, None])
    @patch("ui_tests.support.window_setup.ctypes.windll", create=True)
    def test_close_request_is_confirmed_by_window_lookup(self, windll, find_window, sleep):
        windll.user32 = Mock()

        self.assertTrue(close_existing_ibapda_window_and_confirm())

        windll.user32.PostMessageW.assert_called_once_with(123, 0x0010, 0, 0)
        self.assertEqual(find_window.call_count, 2)
        sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
