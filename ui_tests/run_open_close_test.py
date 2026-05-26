"""Run the constrained VS Code -> ibaPDA open/close UI test."""

import json

from see_think_act_agent import SeeThinkActAgent
from ui_contexts import IBAPDA_UI_CONTEXT
from ui_tests.window_setup import (
    ensure_no_existing_ibapda_window_before_launch,
    minimize_all_windows_for_test,
    restore_minimized_windows_after_test,
)


TASK = """
Perform only this limited UI test:
1. All previously open windows have already been minimized and the desktop should be visible.
2. Open the ibaPDA Client application from the desktop or Windows search.
3. As soon as the ibaPDA Client window is visibly open, close that window using only
   its normal window close button in the title bar.
4. Terminate with status success only after the ibaPDA Client window is visibly closed.

Safety restrictions:
- Do not click, type, or interact with any control inside the ibaPDA Client content area.
- Do not start, stop, configure, or change any recording, process, measurement, or file.
- Do not perform any task beyond opening ibaPDA Client and closing its window.
- If it is not clear how to open or close the window without interacting with its
  contents, terminate with status failure instead of attempting another action.
""".strip()

def main() -> None:
    if not ensure_no_existing_ibapda_window_before_launch():
        return

    agent = SeeThinkActAgent(
        dry_run=False,
        max_iterations=10,
        save_screenshots=True,
        screenshot_dir="artifacts/ui_tests/open_close_test",
        max_task_duration=180,
        max_repeated_actions=2,
        max_consecutive_failures=2,
        allowed_actions={"double_click", "left_click", "wait", "terminate"},
        additional_system_prompt=IBAPDA_UI_CONTEXT,
    )

    if not agent.ollama_client.test_connection():
        print("ERROR: Ollama is unavailable or the configured model is missing.")
        return

    print("Starting constrained open/close test.")
    print("Move the mouse to the top-left corner to trigger pyautogui failsafe.")
    print("Screenshots are stored in artifacts/ui_tests/open_close_test.")
    minimize_all_windows_for_test()
    try:
        result = agent.run(TASK)
    finally:
        restore_minimized_windows_after_test()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
