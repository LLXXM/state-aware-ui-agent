# UI Tests

Executable UI-test infrastructure for the State-aware-UI-agent (State-Agent).
Run computer-use test cases against any Windows application.

## Contents

- `run_test_case.py`: Command-line runner for one `UiTestCase`. It handles
  optional pre-run setup, preparation tasks, measured runs, post-run cleanup,
  and report-folder creation.
- `test_cases/`: Test-case definitions (e.g., `notepad_basic.py`, `calculator_basic.py`).
  Each module exposes one `CASE` object of type `UiTestCase`.
- `contexts/`: Application-specific prompt context. Start with `generic.py` for
  general desktop guidelines; add per-application contexts as needed.
- `support/`: Generic Windows helpers for window management and app lifecycle.

## Running A Case

```powershell
python -m ui_tests.run_test_case NOTEPAD_BASIC
```

Reports are written below the configured report root, grouped by test case.
For prepared measurement workflows, preparation, each measurement run, and
cleanup receive separate report subfolders.

## Creating A Test Case

1. Create a module in `test_cases/` (e.g., `my_app_basic.py`).
2. Define `TASK` (and optional `PREPARE_TASK`) strings.
3. Create a `UiTestCase` instance named `CASE` with:
   - `case_id`: Unique identifier (e.g., `"MYAPP-00"`)
   - `description`: Human-readable description
   - `task`: The main agent task
   - `app_context`: Application-specific UI context (import from `contexts/`)
   - `pre_run_setup`: Callable for app launch/window prep (use `make_setup_fn`)
   - `post_run_cleanup`: Callable for app close/cleanup (use `make_cleanup_fn`)
   - Other limits: `max_iterations`, `allowed_actions`, etc.
4. Run with `python -m ui_tests.run_test_case MYAPP-00`

See `ui_tests/contexts/generic.py` for base desktop context and
`ui_tests/support/app_lifecycle.py` for setup/cleanup factory functions.