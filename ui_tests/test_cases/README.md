# Test Cases

Executable test-case definitions for the UI test runner.

Each `tf_XX.py` file defines:

- `TASK`: The main agent task.
- Optional `PREPARE_TASK`: Setup work that runs once before measured task
  repetitions.
- `CASE`: A `UiTestCase` object containing task text, prompt context, allowed
  actions, iteration/time limits, cleanup settings, reporting behavior, and
  model options.

## Conventions

- Keep test-case-specific goals and procedure text in the `tf_XX.py` file.
- Keep reusable ibaPDA visual knowledge in `ui_tests/contexts/ibapda.py`.
- Restrict `allowed_actions` per test case to the smallest useful set.
- Reports generated from real runs are stored under `Reports_Masterarbeit/`.
  That folder is ignored by Git by default; use `git add -f` only for reports
  that intentionally belong in a result commit.
