# Computer-Use-Agent

Windows UI agent prototype for controlled ibaPDA test cases using Ollama and
Qwen3.5. The agent observes screenshots, proposes structured computer actions,
verifies mouse targets, and records self-contained HTML reports for each run.

## Structure

```text
Computer-Use-Agent/
  see_think_act_agent.py       Core see-think-act loop
  config.py                    Runtime and safety defaults
  ui_contexts.py               ibaPDA-specific visual knowledge
  utils/                       Ollama client and action execution
  ui_tests/
    run_test_case.py           Single test-case runner
    test_cases/                Executable test-case definitions
      tf_00.py                 Data Recording start/stop cycle
    support/                   Cleanup and window-management helpers
  tests/                       Automated unit tests
  ui_tests/test_cases/
    Reports_Masterarbeit/      Generated reports and screenshots, ignored by Git
```

## Run A Test Case

Run TF-00:

```powershell
py -m ui_tests.run_test_case TF-00
```

`TF-00` cleans up an existing ibaPDA Client window if needed, opens ibaPDA,
starts Data Recording, verifies the running state, stops recording, verifies
the stopped state, and closes the client safely.

## Add A Test Case

Create a module such as `ui_tests/test_cases/tf_01.py` containing a
`UiTestCase` instance named `CASE`. Each case defines its task text, allowed
actions, optional UI context, limits, and whether ibaPDA cleanup is required.
Tests that do not activate Data Recording use the same runner and simply omit
recording actions from their task.

## Configure A UI Test Run

Most run behavior is configured on the `UiTestCase` object in
`ui_tests/test_cases/tf_XX.py`. Defaults come from `config.py`.

Common fields:

- `task`: The main instruction executed by the agent.
- `prepare_task`: Optional preparation instruction. If set, the runner executes
  preparation once and then runs `task` as measured repetitions. If `None`, the
  runner executes `task` directly once.
- `measurement_repetitions`: Number of measured `task` runs after a successful
  `prepare_task`.
- `additional_system_prompt`: Extra UI context, usually from `ui_contexts.py`.
- `allowed_actions`: Actions allowed for this test case. Use this to restrict
  risky or irrelevant tools per TF case.
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

Window and cleanup fields:

- `cleanup_ibapda_before`: If true, the runner closes an existing ibaPDA window
  before the test starts.
- `cleanup_ibapda_after`: If true, the runner closes ibaPDA after the workflow.
- `minimize_windows_before`: If true, the runner uses `Win+M` before the
  workflow. This minimizes all windows, including an already open ibaPDA.
- `minimize_vscode_before`: If true, the runner minimizes visible Visual Studio
  Code windows only and leaves ibaPDA untouched. Use this for special manual
  starts where ibaPDA is already open and should remain visible.

Report output:

- By default, UI test reports are written next to the test-case scripts under
  `ui_tests/test_cases/Reports_Masterarbeit/<tf_xx>/...`.
- Each report folder is self-contained. Screenshots, action overlays, and other
  image artifacts are stored below that report folder in `screenshots/`.
- For prepared measurement runs, preparation, each measurement run, and cleanup
  each get their own subfolder with its own HTML report and `screenshots/`
  directory.
- The older `ui_tests/test_cases/Reports/...` folder is left untouched, so old
  exploratory runs and new master-thesis runs stay separated.
- Change `config.TEST_CASE_REPORTS_DIR_NAME` to use another default report
  folder name.
- Use `--report-dir <path>` when starting a single run if a one-off custom
  report path is needed.

Typical modes:

- Standard automated mode:
  `prepare_task=PREPARE_TASK`, `cleanup_ibapda_before=True`,
  `minimize_windows_before=True`, `minimize_vscode_before=False`.
- Manual existing-ibaPDA mode:
  `prepare_task=None`, `cleanup_ibapda_before=False`,
  `minimize_windows_before=False`, `minimize_vscode_before=True`.

## Safety

- Move the mouse to the top-left corner to trigger the `pyautogui` failsafe.
- Mouse targets are saved as overlays and visually verified before execution.
- ibaPDA cleanup prevents duplicate client instances and avoids leaving Data
  Recording active after a test case.

## Verify

```powershell
python -m unittest discover -s tests -v
```
