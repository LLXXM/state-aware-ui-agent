# Test Cases

Executable test-case definitions for the UI test runner.

Each test case module (e.g., `notepad_basic.py`) defines:

- `TASK`: The main agent task.
- Optional `PREPARE_TASK`: Setup work that runs once before measured task
  repetitions.
- `CASE`: A `UiTestCase` object containing task text, prompt context, allowed
  actions, iteration/time limits, setup/cleanup hooks, reporting behavior,
  and model options.

## UiTestCase Fields

Key fields (see `ui_tests/test_cases/__init__.py` for full list):

- `case_id`: Unique identifier (e.g., `"NOTEPAD-00"`)
- `description`: Human-readable description
- `task`: Main task string
- `prepare_task`: Optional preparation task string
- `measurement_repetitions`: Number of measured runs after preparation
- `app_context`: Application-specific UI context (from `contexts/`)
- `allowed_actions`: Restricted action set (frozenset) or None for all
- `max_iterations`, `max_task_duration`: Safety limits
- `verify_mouse_targets`, `abort_on_mouse_verification_failure`: Verification
- `pre_run_setup`: Callable `() -> dict` for app launch/window prep
- `post_run_cleanup`: Callable `() -> dict` for app close/cleanup
- `report_dir_name`: Report subdirectory name (default from config)

## Conventions

- Keep test-case-specific goals and procedure text in the test case file.
- Keep reusable application visual knowledge in `ui_tests/contexts/<app>.py`.
- Restrict `allowed_actions` per test case to the smallest useful set.
- Use `make_setup_fn()` / `make_cleanup_fn()` from `app_lifecycle.py` for
  standard launch/close patterns.
- Reports generated from real runs are stored under `Reports/` (gitignored).

## Example

```python
from ui_tests.contexts.generic import SIMPLE_APP_CONTEXT
from ui_tests.support.app_lifecycle import make_setup_fn, make_cleanup_fn
from ui_tests.test_cases import UiTestCase

TASK = "Open Notepad, type 'Hello World', save as test.txt, and close."

CASE = UiTestCase(
    case_id="NOTEPAD-00",
    description="Basic Notepad text entry and save.",
    task=TASK,
    app_context=SIMPLE_APP_CONTEXT,
    allowed_actions=frozenset({"left_click", "double_click", "type", "key", "wait", "checkpoint", "terminate"}),
    max_iterations=15,
    max_task_duration=180,
    pre_run_setup=make_setup_fn(
        launch_command="notepad.exe",
        wait_for_window=r".*Notepad",
        minimize_all_first=True,
    ),
    post_run_cleanup=make_cleanup_fn(
        close_window_title=r".*Notepad",
        restore_windows=True,
    ),
)
```