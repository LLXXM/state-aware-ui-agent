"""Run a controlled autonomous ibaPDA start/stop UI test."""

import json

from ui_tests.window_setup import (
    ensure_no_existing_ibapda_window_before_launch,
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
4. Click the filled green Data Recording button labeled 'GO' in white text.
   It is directly left of the filled gray button labeled 'STOP', between a
   two-person icon and gear icons. Do not click the separate green outlined
   'Ansichten starten' triangle/play button elsewhere in the toolbar.
5. If a dialog clearly asks to confirm starting Data Recording, confirm it.
6. Confirm that Data Recording has started: Go becomes gray, Stop becomes red,
   and/or a 'Data Store' entry with a small green circular indicator appears in
   'Datenaufzeichnungsstatus'. In the stopped state that entry is absent and
   only the system or computer name is shown there.
7. Click the now-red Data Recording Stop button directly to the right of Go.
8. If a dialog clearly asks to confirm stopping Data Recording, confirm it.
9. Terminate with status success only after the UI visibly confirms Data
   Recording is stopped again: Go is green, Stop is gray, and/or
   the 'Data Store' entry has disappeared from 'Datenaufzeichnungsstatus'.

Safety restrictions:
- Do not modify configuration, files, signals, views, or measurement settings.
- Do not interact with any content control other than the explicitly required
  Data Recording Go/Stop controls and their unambiguous confirmation dialogs.
- After GO has produced an 'Erfassung wird gestartet' window or a 'Data Store'
  entry with a green indicator has appeared, never click GO again during this
  task. Treat it as started or starting and proceed toward verified STOP.
- Do not leave the operation running when terminating.
- If Go, Stop, a confirmation dialog, or the stopped state cannot be
  identified clearly, terminate with status failure instead of clicking
  another control.
""".strip()


def main() -> None:
    if not ensure_no_existing_ibapda_window_before_launch():
        return

    agent = SeeThinkActAgent(
        dry_run=False,
        max_iterations=12,
        save_screenshots=True,
        screenshot_dir="artifacts/ui_tests/start_stop_test",
        max_task_duration=240,
        max_repeated_actions=2,
        max_consecutive_failures=2,
        allowed_actions={"double_click", "left_click", "wait", "checkpoint", "terminate"},
        max_executed_mouse_actions=5,
        additional_system_prompt=IBAPDA_UI_CONTEXT,
    )

    if not agent.ollama_client.test_connection():
        print("ERROR: Ollama is unavailable or the configured model is missing.")
        return

    print("Starting controlled autonomous ibaPDA start/stop test.")
    print("The Go and Stop actions will be executed if visually verified.")
    print("Move the mouse to the top-left corner to trigger pyautogui failsafe.")
    print("Screenshots are stored in artifacts/ui_tests/start_stop_test.")
    minimize_all_windows_for_test()
    try:
        result = agent.run(TASK)
    finally:
        restore_minimized_windows_after_test()

    print(json.dumps(result, indent=2))
    print("Close ibaPDA manually after confirming the operation remains stopped.")


if __name__ == "__main__":
    main()
