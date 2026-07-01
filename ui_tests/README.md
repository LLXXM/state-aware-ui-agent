# UI Tests

Executable UI-test infrastructure for ibaPDA-based computer-use test cases.

## Contents

- `run_test_case.py`: Command-line runner for one `UiTestCase`. It handles
  optional pre-cleanup, window minimization, preparation tasks, measured runs,
  post-cleanup, and report-folder creation.
- `test_cases/`: Test-case definitions such as `tf_01.py` through `tf_06.py`.
  Each module exposes one `CASE` object.
- `contexts/`: Application-specific prompt context, currently focused on
  ibaPDA Client.
- `support/`: Deterministic helpers around Windows/ibaPDA cleanup and window
  setup.

## Running A Case

```powershell
python -m ui_tests.run_test_case TF-04
```

Reports are written below the configured report root, grouped by test case.
For prepared measurement workflows, preparation, each measurement run, and
cleanup receive separate report subfolders.
