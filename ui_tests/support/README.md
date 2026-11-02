# Support

Generic deterministic helpers for UI test execution.

## Modules

- `app_lifecycle.py`: Cross-application window management and setup/cleanup factories:
  - `find_window_by_title(pattern)` — find window by regex title
  - `focus_window(hwnd)` — focus/restore window
  - `close_window(hwnd)` — close and confirm
  - `minimize_all_windows()` / `restore_all_windows()` — Win+M / Win+Shift+M
  - `minimize_windows_by_title(pattern)` — selective minimization
  - `make_setup_fn(...)` — factory for `UiTestCase.pre_run_setup`
  - `make_cleanup_fn(...)` — factory for `UiTestCase.post_run_cleanup`

## Usage

In test case files:

```python
from ui_tests.support.app_lifecycle import make_setup_fn, make_cleanup_fn

CASE = UiTestCase(
    ...,
    pre_run_setup=make_setup_fn(
        launch_command="myapp.exe",
        wait_for_window=r".*MyApp",
        minimize_all_first=True,
    ),
    post_run_cleanup=make_cleanup_fn(
        close_window_title=r".*MyApp",
        restore_windows=True,
    ),
)
```

Keep support code focused on setup/cleanup mechanics. Test goals and prompt
wording belong in `ui_tests/test_cases/` and `ui_tests/contexts/`.