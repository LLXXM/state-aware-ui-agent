# Tests

Unit tests for the computer-use agent, UI-test runner, and support helpers.

## Test Areas

- `test_action_contract.py`: Structured `computer_use` tool schema and action
  executor contract.
- `test_agent_*.py`: Agent configuration, prompting, completion, safety,
  overlays, and mouse-target verification.
- `test_html_report.py`: Incremental HTML report output and summary fields.
- `test_ollama_client.py`: Ollama connection checks, retries, options, and
  response parsing.

Run all tests with:

```powershell
python -m unittest discover -s tests -v
```