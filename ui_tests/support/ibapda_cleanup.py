"""Bring an existing ibaPDA instance to a safe stopped and closed state."""

from see_think_act_agent import SeeThinkActAgent
from ui_tests.contexts.ibapda import IBAPDA_UI_CONTEXT
from ui_tests.support.window_setup import (
    close_existing_ibapda_window_and_confirm,
    find_ibapda_window_handle,
    focus_existing_ibapda_window_for_recovery,
)


TASK = """
Perform only this ibaPDA cleanup task on the existing foreground ibaPDA window:
1. Do not open or launch ibaPDA. An existing instance has already been restored and focused.
2. Inspect Data Recording state.
3. If Data Recording is active, indicated by a 'Data Store' entry with a green
   circular indicator and/or gray GO with red STOP, click the red Data Recording
   STOP button and confirm only an unambiguous stop dialog.
4. If Data Recording is already stopped, do not click GO or STOP.
5. Terminate with status success as soon as Data Recording is visibly stopped.
   The runner, not you, will close the existing ibaPDA window afterward.

Safety restrictions:
- Never click GO in this cleanup task.
- Never launch a new ibaPDA instance.
- Never close the ibaPDA window yourself and never click a title-bar close button.
- Do not modify configuration, files, signals, views, or measurement settings.
- If recording is active but STOP or an expected stop confirmation cannot be
  identified clearly, terminate with status failure.
""".strip()


def ensure_ibapda_closed(
    screenshot_dir: str = "artifacts/ui_tests/ensure_ibapda_closed",
    check_connection: bool = True,
    report_dir: str | None = None,
) -> dict:
    """Stop recording if necessary and close an existing ibaPDA client window."""
    if find_ibapda_window_handle() is None:
        return {
            "success": True,
            "status": "already_closed",
            "message": "No visible or minimized ibaPDA Client main window was detected.",
        }

    if not focus_existing_ibapda_window_for_recovery():
        return {
            "success": False,
            "status": "window_focus_failed",
            "message": (
                "An ibaPDA Client main window was detected, but could not be "
                "confirmed in the foreground. No UI action was executed."
            ),
        }

    agent = SeeThinkActAgent(
        dry_run=False,
        max_iterations=10,
        save_screenshots=True,
        screenshot_dir=screenshot_dir,
        max_task_duration=180,
        max_repeated_actions=2,
        max_consecutive_failures=2,
        allowed_actions={"left_click", "wait", "checkpoint", "terminate"},
        max_executed_mouse_actions=2,
        report_dir=report_dir,
        additional_system_prompt=IBAPDA_UI_CONTEXT,
    )

    if check_connection and not agent.ollama_client.test_connection():
        return {
            "success": False,
            "status": "connection_failed",
            "message": "Ollama is unavailable or the configured model is missing.",
        }

    print("Starting cleanup of an existing ibaPDA instance.")
    print("The cleanup runner will not open a new ibaPDA instance.")
    print(f"Screenshots are stored in {screenshot_dir}.")
    result = agent.run(TASK)
    if result.get("status") == "success":
        window_closed = close_existing_ibapda_window_and_confirm()
        result["window_closed"] = window_closed
        if not window_closed:
            result["success"] = False
            result["status"] = "window_close_failed"
            result["message"] = (
                "Data Recording is stopped, but a visible or minimized ibaPDA "
                "window remains after the close request."
            )
    return result
