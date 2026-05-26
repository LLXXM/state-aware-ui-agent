"""Run a controlled autonomous ibaPDA start/stop UI test."""

import json

from run_open_close_test import (
    minimize_all_windows_for_test,
    restore_minimized_windows_after_test,
)
from see_think_act_agent import SeeThinkActAgent
from ui_contexts import IBAPDA_UI_CONTEXT


TASK = """
Perform only this controlled ibaPDA start/stop test:
1. All previously open windows have already been minimized and the desktop should be visible.
2. Open the ibaPDA Client application by double-clicking its visible desktop icon.
3. Wait until the ibaPDA Client main window is fully visible.
4. Click the round green Go/start button in the top-left toolbar below 'Ansicht'.
5. Inspect the resulting UI state and confirm that the operation has started.
6. Locate and click the visible Stop control that ends the just-started operation.
7. Terminate with status success only after the UI visibly confirms the operation is stopped.

Safety restrictions:
- Do not modify configuration, files, signals, views, or measurement settings.
- Do not interact with any content control other than the explicitly required
  Go/start and Stop controls.
- Do not leave the operation running when terminating.
- If the Stop control or stopped state cannot be identified clearly, terminate
  with status failure instead of clicking another control.
""".strip()


def main() -> None:
    agent = SeeThinkActAgent(
        dry_run=False,
        max_iterations=12,
        save_screenshots=True,
        screenshot_dir="agent_screenshots/start_stop_test",
        max_task_duration=240,
        max_repeated_actions=2,
        max_consecutive_failures=2,
        allowed_actions={"double_click", "left_click", "wait", "checkpoint", "terminate"},
        max_executed_mouse_actions=3,
        additional_system_prompt=IBAPDA_UI_CONTEXT,
    )

    if not agent.ollama_client.test_connection():
        print("ERROR: Ollama is unavailable or the configured model is missing.")
        return

    print("Starting controlled autonomous ibaPDA start/stop test.")
    print("The Go and Stop actions will be executed if visually verified.")
    print("Move the mouse to the top-left corner to trigger pyautogui failsafe.")
    print("Screenshots are stored in agent_screenshots/start_stop_test.")
    minimize_all_windows_for_test()
    try:
        result = agent.run(TASK)
    finally:
        restore_minimized_windows_after_test()

    print(json.dumps(result, indent=2))
    print("Close ibaPDA manually after confirming the operation remains stopped.")


if __name__ == "__main__":
    main()
