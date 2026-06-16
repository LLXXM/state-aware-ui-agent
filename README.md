# Computer-Use-Agent

Windows UI agent prototype for controlled ibaPDA test cases using Ollama and
Qwen3.5. The agent observes screenshots, proposes structured computer actions,
verifies mouse targets, and records screenshot artifacts for each run.

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
  artifacts/ui_tests/          Generated run screenshots, ignored by Git
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

## Safety

- Move the mouse to the top-left corner to trigger the `pyautogui` failsafe.
- Mouse targets are saved as overlays and visually verified before execution.
- ibaPDA cleanup prevents duplicate client instances and avoids leaving Data
  Recording active after a test case.

## Verify

```powershell
python -m unittest discover -s tests -v
```
