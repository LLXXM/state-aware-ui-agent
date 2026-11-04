"""Example test case: Basic Calculator arithmetic operations."""

from ui_tests.contexts.calculator import CALCULATOR_CONTEXT
from ui_tests.support.app_lifecycle import make_setup_fn, make_cleanup_fn
from ui_tests.test_cases import UiTestCase

TASK = """
Perform basic arithmetic operations in Calculator (Standard mode):
1. Calculator is already open in Standard mode (launched by pre-run setup).
2. Verify the display shows "0" initially.
3. Calculate 25 * 4:
   - Click "2", then "5" (display shows "25").
   - Click "*" (multiply).
   - Click "4" (display shows "25*4" or "25 × 4").
   - Click "=" (display shows "100").
   - Record a checkpoint: "25 * 4 = 100".
4. Calculate 100 - 37:
   - Click "1", "0", "0" (or just continue from result).
   - Click "-" (subtract).
   - Click "3", "7".
   - Click "=" (display shows "63").
   - Record a checkpoint: "100 - 37 = 63".
5. Calculate 63 / 9:
   - Click "/" (divide).
   - Click "9".
   - Click "=" (display shows "7").
   - Record a checkpoint: "63 / 9 = 7".
6. Clear and verify:
   - Click "C" (clear all).
   - Display should show "0".
   - Record a checkpoint: "Cleared, display shows 0".
7. Terminate with status success.
"""

PREPARE_TASK = None

CASE = UiTestCase(
    case_id="CALC-00",
    description="Basic Calculator arithmetic: multiply, subtract, divide, clear.",
    task=TASK,
    prepare_task=PREPARE_TASK,
    measurement_repetitions=1,
    app_context=CALCULATOR_CONTEXT,
    allowed_actions=frozenset(
        {"left_click", "double_click", "type", "key", "wait", "checkpoint", "terminate"}
    ),
    max_iterations=25,
    max_task_duration=180,
    max_repeated_actions=2,
    max_consecutive_failures=2,
    verify_mouse_targets=True,
    iteration_delay=0.2,
    post_action_delay=0.5,
    model_options={
        "temperature": 0.1,
        "num_ctx": 8192,
        "num_predict": 384,
    },
    pre_run_setup=make_setup_fn(
        launch_command="calc.exe",
        wait_for_window=r"(Calculator|Rechner)",
        minimize_all_first=True,
    ),
    post_run_cleanup=make_cleanup_fn(
        close_window_title=r"(Calculator|Rechner)",
        restore_windows=True,
    ),
    report_dir_name="Reports",
)
