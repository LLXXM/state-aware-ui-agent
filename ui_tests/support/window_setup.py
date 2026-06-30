"""Shared desktop preparation helpers for UI test runners."""

import ctypes
import re
import time
from typing import Optional

import pyautogui


IBAPDA_CLIENT_TITLE_PATTERN = re.compile(r"^ibapda\s+v\d", re.IGNORECASE)
VSCODE_TITLE_PATTERN = re.compile(r"visual studio code", re.IGNORECASE)


def find_ibapda_window_handle() -> Optional[int]:
    """Return a visible or minimized ibaPDA user-window handle."""
    user32 = getattr(getattr(ctypes, "windll", None), "user32", None)
    if user32 is None:
        return None

    found = []
    enum_callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def inspect_window(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
            return True

        title_length = user32.GetWindowTextLengthW(hwnd)
        if title_length:
            title = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(hwnd, title, title_length + 1)
            if IBAPDA_CLIENT_TITLE_PATTERN.match(title.value.strip()):
                found.append(int(hwnd))
                return False
        return True

    user32.EnumWindows(enum_callback(inspect_window), 0)
    return found[0] if found else None


def focus_existing_ibapda_window_for_recovery() -> bool:
    """Focus an ibaPDA window, restoring it only when it is minimized."""
    hwnd = find_ibapda_window_handle()
    if hwnd is None:
        return False

    user32 = ctypes.windll.user32
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(1)
    return user32.GetForegroundWindow() == hwnd


def close_existing_ibapda_window_and_confirm() -> bool:
    """Close ibaPDA and confirm no visible or minimized user window remains."""
    hwnd = find_ibapda_window_handle()
    if hwnd is None:
        return True

    user32 = ctypes.windll.user32
    user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
    deadline = time.time() + 15
    while time.time() < deadline:
        if find_ibapda_window_handle() is None:
            return True
        time.sleep(0.5)
    return find_ibapda_window_handle() is None


def minimize_all_windows_for_test() -> None:
    """Minimize all visible windows so the test starts on the desktop."""
    print("Minimizing all windows with Win+M.")
    pyautogui.hotkey("win", "m")
    time.sleep(1)


def minimize_vscode_windows_for_test() -> None:
    """Minimize visible VS Code windows without touching ibaPDA."""
    user32 = getattr(getattr(ctypes, "windll", None), "user32", None)
    if user32 is None:
        return

    handles: list[int] = []
    enum_callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def inspect_window(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return True

        title_length = user32.GetWindowTextLengthW(hwnd)
        if title_length:
            title = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(hwnd, title, title_length + 1)
            if VSCODE_TITLE_PATTERN.search(title.value.strip()):
                handles.append(int(hwnd))
        return True

    user32.EnumWindows(enum_callback(inspect_window), 0)
    if not handles:
        print("No visible VS Code window found to minimize.")
        return

    print(f"Minimizing {len(handles)} VS Code window(s).")
    for hwnd in handles:
        user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
    time.sleep(1)


def restore_minimized_windows_after_test() -> None:
    """Restore windows minimized before the test, including VS Code."""
    pyautogui.hotkey("win", "shift", "m")
    time.sleep(1)
