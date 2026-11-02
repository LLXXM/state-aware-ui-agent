"""Example test case: Basic Notepad text entry and save."""

from ui_tests.contexts.notepad import NOTEPAD_CONTEXT
from ui_tests.support.app_lifecycle import make_setup_fn, make_cleanup_fn
from ui_tests.test_cases import UiTestCase

TASK = """
Perform basic text entry and file save in Notepad:
1. Notepad is already open (launched by pre-run setup).
2. Click in the main text editing area to ensure focus.
3. Type the text: "Hello, State-Agent!" (including the comma and exclamation).
4. Save the file as "state_agent_test.txt" on the Desktop:
   - Press Ctrl+S to open Save As dialog (since it's a new untitled file).
   - In the file name field, type "state_agent_test.txt".
   - Navigate to Desktop in the dialog (type "%USERPROFILE%\\Desktop" in address bar and press Enter, or click Desktop in left pane).
   - Click Save button.
   - If a "file already exists" confirmation appears, click Yes/Replace.
5. Verify the title bar now shows "state_agent_test.txt - Notepad".
6. Close Notepad via File -> Exit (or Ctrl+W).
7. Terminate with status success.
"""

PREPARE_TASK = None

CASE = UiTestCase(
    case_id="NOTEPAD-00",
    description="Basic Notepad text entry, save to Desktop, and close.",
    task=TASK,
    prepare_task=PREPARE_TASK,
    measurement_repetitions=1,
    app_context=NOTEPAD_CONTEXT,
    allowed_actions=frozenset({
        "left_click", "double_click", "type", "key", "wait", "checkpoint", "terminate"
    }),
    max_iterations=20,
    max_task_duration=180,
    max_repeated_actions=2,
    max_consecutive_failures=2,
    verify_mouse_targets=True,
    iteration_delay=0.3,
    post_action_delay=0.8,
    model_options={
        "temperature": 0.1,
        "num_ctx": 8192,
        "num_predict": 384,
    },
    pre_run_setup=make_setup_fn(
        launch_command="notepad.exe",
        wait_for_window=r".*Notepad",
        minimize_all_first=True,
    ),
    post_run_cleanup=make_cleanup_fn(
        close_window_title=r".*Notepad",
        restore_windows=True,
    ),
    report_dir_name="Reports",
)