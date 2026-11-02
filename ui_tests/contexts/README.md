# UI Contexts

Application-specific prompt context for UI test cases.

## Modules

- `generic.py`: Universal desktop interaction guidelines (`GENERIC_DESKTOP_CONTEXT`,
  `SIMPLE_APP_CONTEXT`). Import and extend for your application.
- `<appname>.py`: Per-application contexts (e.g., `notepad.py`, `calculator.py`).
  Should import `GENERIC_DESKTOP_CONTEXT` and append application-specific knowledge.

## Usage

In your test case file:

```python
from ui_tests.contexts.generic import SIMPLE_APP_CONTEXT

MY_APP_CONTEXT = SIMPLE_APP_CONTEXT + """
MyApp specific knowledge:
- The main toolbar has Save, Open, New buttons...
- The status bar shows...
"""

CASE = UiTestCase(
    ...,
    app_context=MY_APP_CONTEXT,
    ...
)
```

Keep concrete application UI descriptions here rather than in generic agent
or utility modules.