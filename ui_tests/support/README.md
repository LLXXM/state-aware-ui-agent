# Support

Deterministic support helpers for UI test execution.

## Modules

- `ibapda_cleanup.py`: Uses the agent only for the UI-dependent part of
  stopping Data Recording, then closes the existing ibaPDA window through
  deterministic window-management helpers.
- `window_setup.py`: Finds, focuses, minimizes, restores, and closes relevant
  Windows windows around test execution.

Keep support code focused on setup/cleanup mechanics. Test goals and prompt
wording belong in `ui_tests/test_cases/` and `ui_tests/contexts/`.
