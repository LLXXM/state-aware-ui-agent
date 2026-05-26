"""Application-specific UI knowledge supplied only to relevant agent tasks."""

IBAPDA_UI_CONTEXT = """You are operating the ibaPDA Client application.

Known UI elements:
- The Windows desktop shortcut named 'ibaPDA Client' opens the application.
- In the ibaPDA main window, the round green button with a play symbol in the
  top-left toolbar below 'Ansicht' is the Go/start control.
- Activating Go can start a measurement or recording. Click it only when the
  current task explicitly requires starting and later stopping that operation.
- After Go has been clicked, inspect the current screenshot for the running
  state and the corresponding Stop control. Do not guess its position from
  memory; click Stop only when it is visually identifiable as the control that
  returns the application to the stopped state.
- A task is not complete after Stop until the screenshot visually confirms that
  the operation is no longer running.
"""
