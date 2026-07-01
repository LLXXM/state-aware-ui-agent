# Tests

Unit tests for the computer-use agent, UI-test runner, ibaPDA context prompts,
and support helpers.

## Test Areas

- `test_action_contract.py`: Structured `computer_use` tool schema and action
  executor contract.
- `test_agent_*.py`: Agent configuration, prompting, completion, safety,
  overlays, and mouse-target verification.
- `test_html_report.py`: Incremental HTML report output and summary fields.
- `test_ibapda_cleanup.py`: Cleanup runner behavior around existing ibaPDA
  windows.
- `test_ollama_client.py`: Ollama connection checks, retries, options, and
  response parsing.
- `test_start_stop_runner.py`: `UiTestCase` definitions and runner behavior.
- `test_ui_contexts.py`: Expected phrases and rules in ibaPDA prompt contexts.
- `test_window_setup.py`: Window discovery, focus, restore, and close helpers.

Run all tests with:

```powershell
python -m unittest discover -s tests -v
```
