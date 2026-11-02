"""Generic application lifecycle helpers for UI test runners."""

import ctypes
import re
import time
from typing import Callable, Optional, Pattern

import pyautogui


def find_window_by_title(pattern: str | Pattern[str]) -> Optional[int]:
    """Return a visible or minimized window handle matching the title pattern.

    Args:
        pattern: Regex pattern string or compiled regex to match window title.

    Returns:
        Window handle (HWND) or None if not found.
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern, re.IGNORECASE)

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
            if pattern.search(title.value.strip()):
                found.append(int(hwnd))
                return False
        return True

    user32.EnumWindows(enum_callback(inspect_window), 0)
    return found[0] if found else None


def focus_window(hwnd: int, restore_if_minimized: bool = True) -> bool:
    """Focus a window, optionally restoring it if minimized.

    Args:
        hwnd: Window handle to focus.
        restore_if_minimized: If True, restore minimized window before focusing.

    Returns:
        True if window is now in foreground.
    """
    user32 = ctypes.windll.user32
    if restore_if_minimized and user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    return user32.GetForegroundWindow() == hwnd


def close_window(hwnd: int, timeout: float = 15.0) -> bool:
    """Close a window and confirm it's gone.

    Args:
        hwnd: Window handle to close.
        timeout: Maximum time to wait for window to close.

    Returns:
        True if window no longer exists.
    """
    user32 = ctypes.windll.user32
    user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
    deadline = time.time() + timeout
    while time.time() < deadline:
        if find_window_by_title("") is None or not _window_exists(user32, hwnd):
            return True
        time.sleep(0.2)
    return not _window_exists(user32, hwnd)


def _window_exists(user32, hwnd: int) -> bool:
    """Check if a window handle still exists."""
    try:
        return user32.IsWindow(hwnd)
    except Exception:
        return False


def minimize_all_windows() -> None:
    """Minimize all visible windows (Win+M)."""
    print("Minimizing all windows with Win+M.")
    pyautogui.hotkey("win", "m")
    time.sleep(1)


def restore_all_windows() -> None:
    """Restore windows minimized with Win+Shift+M."""
    pyautogui.hotkey("win", "shift", "m")
    time.sleep(1)


def minimize_windows_by_title(pattern: str | Pattern[str]) -> int:
    """Minimize all visible windows matching a title pattern.

    Args:
        pattern: Regex pattern string or compiled regex to match window title.

    Returns:
        Number of windows minimized.
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern, re.IGNORECASE)

    user32 = getattr(getattr(ctypes, "windll", None), "user32", None)
    if user32 is None:
        return 0

    handles: list[int] = []
    enum_callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def inspect_window(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return True

        title_length = user32.GetWindowTextLengthW(hwnd)
        if title_length:
            title = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(hwnd, title, title_length + 1)
            if pattern.search(title.value.strip()):
                handles.append(int(hwnd))
        return True

    user32.EnumWindows(enum_callback(inspect_window), 0)
    if not handles:
        print(f"No visible window matching {pattern.pattern!r} found to minimize.")
        return 0

    print(f"Minimizing {len(handles)} window(s) matching {pattern.pattern!r}.")
    for hwnd in handles:
        user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
    time.sleep(1)
    return len(handles)


def make_setup_fn(
    *,
    launch_command: Optional[str] = None,
    wait_for_window: Optional[str | Pattern[str]] = None,
    wait_timeout: float = 60.0,
    minimize_all_first: bool = False,
    minimize_matching: Optional[str | Pattern[str]] = None,
    focus_window_title: Optional[str | Pattern[str]] = None,
) -> Callable[[], dict]:
    """Create a pre-run setup callable for UiTestCase.pre_run_setup.

    Args:
        launch_command: Optional command to launch the target application.
        wait_for_window: Window title pattern to wait for after launch.
        wait_timeout: Maximum time to wait for window to appear.
        minimize_all_first: If True, minimize all windows before launch.
        minimize_matching: Optional window title pattern to minimize (e.g., VS Code).
        focus_window_title: Window title pattern to focus after setup.

    Returns:
        A callable that returns a result dict with success/status/message.
    """
    import subprocess

    def setup() -> dict:
        if minimize_all_first:
            minimize_all_windows()

        if minimize_matching:
            minimize_windows_by_title(minimize_matching)

        if launch_command:
            print(f"Launching: {launch_command}")
            try:
                subprocess.Popen(launch_command, shell=True)
            except Exception as e:
                return {
                    "success": False,
                    "status": "launch_failed",
                    "message": f"Failed to launch application: {e}",
                }

        if wait_for_window:
            print(f"Waiting for window matching {wait_for_window!r}...")
            deadline = time.time() + wait_timeout
            hwnd = None
            while time.time() < deadline:
                hwnd = find_window_by_title(wait_for_window)
                if hwnd:
                    break
                time.sleep(0.5)
            if not hwnd:
                return {
                    "success": False,
                    "status": "window_not_found",
                    "message": f"Window matching {wait_for_window!r} did not appear within {wait_timeout}s.",
                }
            print(f"Found window (HWND={hwnd})")

        if focus_window_title:
            hwnd = find_window_by_title(focus_window_title)
            if hwnd and not focus_window(hwnd):
                return {
                    "success": False,
                    "status": "focus_failed",
                    "message": f"Could not focus window matching {focus_window_title!r}.",
                }

        return {"success": True, "status": "ready", "message": "Pre-run setup completed."}

    return setup


def make_cleanup_fn(
    *,
    close_window_title: Optional[str | Pattern[str]] = None,
    close_timeout: float = 15.0,
    restore_windows: bool = False,
) -> Callable[[], dict]:
    """Create a post-run cleanup callable for UiTestCase.post_run_cleanup.

    Args:
        close_window_title: Window title pattern to close.
        close_timeout: Maximum time to wait for window to close.
        restore_windows: If True, restore all minimized windows (Win+Shift+M).

    Returns:
        A callable that returns a result dict with success/status/message.
    """
    def cleanup() -> dict:
        if close_window_title:
            hwnd = find_window_by_title(close_window_title)
            if hwnd:
                print(f"Closing window matching {close_window_title!r} (HWND={hwnd})...")
                if not close_window(hwnd, timeout=close_timeout):
                    return {
                        "success": False,
                        "status": "close_failed",
                        "message": f"Window matching {close_window_title!r} did not close within {close_timeout}s.",
                    }
                print("Window closed.")
            else:
                print(f"No window matching {close_window_title!r} found to close.")

        if restore_windows:
            restore_all_windows()

        return {"success": True, "status": "cleaned_up", "message": "Post-run cleanup completed."}

    return cleanup