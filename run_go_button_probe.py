"""Open ibaPDA and stop before clicking the proposed recording Go button."""

import json

from run_open_close_test import (
    minimize_all_windows_for_test,
    restore_minimized_windows_after_test,
)
from see_think_act_agent import SeeThinkActAgent
from ui_contexts import IBAPDA_UI_CONTEXT


TASK = """
Perform only this controlled inspection task:
1. All previously open windows have already been minimized and the desktop should be visible.
2. Open the ibaPDA Client application by double-clicking its visible desktop icon.
3. Wait until the ibaPDA Client main window is fully visible.
4. Identify the filled green Data Recording button labeled 'GO' in white text.
   It lies directly to the left of the filled gray button labeled 'STOP',
   between a two-person icon and gear icons. Do not select the separate
   'Ansichten starten' button, which is a green outlined circle with a
   triangle/play symbol and has no 'GO' text.
5. Propose exactly one left click on the Data Recording Go button as the next action.

Safety restrictions:
- The runner will stop before the proposed Go-button click can be executed.
- Do not click any control inside ibaPDA before proposing the Go-button target.
- Do not start, stop, configure, or change any recording, process, measurement, or file.
- Do not close ibaPDA during this inspection task.
""".strip()


def main() -> None:
    agent = SeeThinkActAgent(
        dry_run=False,
        max_iterations=10,
        save_screenshots=True,
        screenshot_dir="agent_screenshots/go_button_probe",
        max_task_duration=180,
        max_repeated_actions=2,
        max_consecutive_failures=2,
        allowed_actions={"double_click", "left_click", "wait", "terminate"},
        max_executed_mouse_actions=1,
        additional_system_prompt=IBAPDA_UI_CONTEXT,
    )

    if not agent.ollama_client.test_connection():
        print("ERROR: Ollama is unavailable or the configured model is missing.")
        return

    print("Starting Go-button inspection. The proposed Go click will not execute.")
    print("Move the mouse to the top-left corner to trigger pyautogui failsafe.")
    print("Screenshots are stored in agent_screenshots/go_button_probe.")
    minimize_all_windows_for_test()
    try:
        result = agent.run(TASK)
    finally:
        restore_minimized_windows_after_test()

    print(json.dumps(result, indent=2))
    print("Close ibaPDA manually after reviewing the proposed action overlay.")


if __name__ == "__main__":
    main()
