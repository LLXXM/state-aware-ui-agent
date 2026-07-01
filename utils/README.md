# Utils

Shared runtime helpers used by the computer-use agent and the UI test runner.

## Modules

- `action_executor.py`: Executes normalized computer-use actions with
  `pyautogui`, including clicks, keyboard input, waits, and drag operations.
- `agent_function_call.py`: Defines and validates the structured
  `computer_use` tool schema used by the model.
- `html_report.py`: Writes incremental HTML reports with screenshots,
  overlays, action history, model usage, and final run metadata.
- `ollama_client.py`: Wraps Ollama chat/image requests, model connection
  checks, response normalization, retries, and tool-call parsing.
- `screenshot_capture.py`: Captures the current screen image for the
  see-think-act loop.

Keep this folder domain-neutral where possible. Application-specific prompt
knowledge belongs under `ui_tests/contexts/`.
