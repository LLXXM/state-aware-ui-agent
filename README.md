# State-aware-UI-agent (State-Agent)

Windows UI agent for computer-use test automation using Ollama and Qwen3.5.
The agent observes screenshots, proposes structured computer actions,
verifies mouse targets visually, and records self-contained HTML reports.

## Structure

```text
State-aware-UI-agent/
  see_think_act_agent.py       Core see-think-act loop
  config.py                    Runtime and safety defaults
  utils/                       Ollama client, action execution, screenshots, reports
  ui_tests/
    contexts/                  Application-specific UI context prompts
    run_test_case.py           Single test-case runner
    test_cases/                Executable test-case definitions
      notepad_basic.py         Example: Notepad text entry
      calculator_basic.py      Example: Calculator operations
    support/                   Generic window management & app lifecycle
  tests/                       Automated unit tests
  ui_tests/test_cases/
    Reports/                   Generated reports and screenshots (gitignored)
```

## Run A Test Case

Run an example test case:

```powershell
py -m ui_tests.run_test_case NOTEPAD-00
```

This launches Notepad, types text, saves the file, and closes Notepad safely.

## Add A Test Case

Create a module in `ui_tests/test_cases/` (e.g., `my_app_basic.py`) containing
a `UiTestCase` instance named `CASE`. Each case defines:

- Task text (`task`, optional `prepare_task`)
- Application UI context (`app_context` from `contexts/`)
- Allowed actions, iteration/time limits
- Pre-run setup & post-run cleanup callables (use `make_setup_fn`/`make_cleanup_fn`)

See `ui_tests/test_cases/README.md` for full field documentation and examples.

## Configure A UI Test Run

Most run behavior is configured on the `UiTestCase` object in
`ui_tests/test_cases/<name>.py`. Defaults come from `config.py`.

Common fields:

- `task`: The main instruction executed by the agent.
- `prepare_task`: Optional preparation instruction. If set, the runner executes
  preparation once and then runs `task` as measured repetitions. If `None`, the
  runner executes `task` directly once.
- `measurement_repetitions`: Number of measured `task` runs after a successful
  `prepare_task`.
- `app_context`: Extra UI context, usually from `ui_tests/contexts/<app>.py`
  (or `generic.py` for simple apps).
- `allowed_actions`: Actions allowed for this test case. Use this to restrict
  risky or irrelevant tools per case.
- `max_iterations`: Maximum agent iterations per agent run.
- `max_task_duration`: Maximum runtime in seconds per agent run.
- `max_repeated_actions`: Blocks repeated identical actions.
- `max_consecutive_failures`: Stops after repeated failed actions.
- `max_executed_mouse_actions`: Optional cap for executed mouse actions.
- `verify_mouse_targets`: If true, proposed mouse targets are visually verified
  before execution.
- `abort_on_mouse_verification_failure`: If true, a failed mouse verification
  aborts the run. If false, the rejection is returned to the agent as feedback.
- `iteration_delay`: Delay in seconds after each iteration.
- `post_action_delay`: Delay in seconds after executed mouse actions.
- `model_options`: Ollama options for this case, for example `temperature`,
  `num_ctx`, and `num_predict`.

Setup/cleanup fields:

- `pre_run_setup`: Callable `() -> dict` for app launch, window prep, etc.
- `post_run_cleanup`: Callable `() -> dict` for app close, window restore, etc.
- `report_dir_name`: Report subdirectory name (default from config).

Use `ui_tests.support.app_lifecycle.make_setup_fn()` and `make_cleanup_fn()`
for standard patterns.

Report output:

- By default, UI test reports are written under `ui_tests/test_cases/Reports/<case_id>/...`.
- Each report folder is self-contained. Screenshots, action overlays, and other
  image artifacts are stored below that report folder in `screenshots/`.
- For prepared measurement runs, preparation, each measurement run, and cleanup
  each get their own subfolder with its own HTML report and `screenshots/` directory.
- Change `config.TEST_CASE_REPORTS_DIR_NAME` to use another default report folder name.
- Use `--report-dir <path>` when starting a single run if a one-off custom report path is needed.

## Safety

- Move the mouse to the top-left corner to trigger the `pyautogui` failsafe.
- Mouse targets are saved as overlays and visually verified before execution.
- Setup/cleanup hooks handle application lifecycle to avoid duplicate instances.

## Verify

```powershell
python -m unittest discover -s tests -v
```

## Documentation

See README files in `utils/`, `ui_tests/`, `ui_tests/contexts/`,
`ui_tests/test_cases/`, `ui_tests/support/`, and `tests/` for folder-level
module overviews.