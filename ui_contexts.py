"""Application-specific UI knowledge supplied only to relevant agent tasks."""

IBAPDA_UI_CONTEXT = """You are operating the ibaPDA Client application.

Starting ibaPDA Client:
- The Windows desktop shortcut named 'ibaPDA Client' opens the application.
- Wait for the main window to be visibly loaded before selecting controls in
  the application toolbar.

Data Recording controls:
- Data Recording is controlled by a filled circular GO/STOP text-button pair.
- GO is labeled 'GO' in white letters. STOP is labeled 'STOP' in white letters.
- GO is directly to the left of STOP.
- The GO/STOP pair is grouped between a two-person icon on its left and gear
  icons on its right.

Data Recording states:
- Stopped state: GO is green and STOP is gray.
- Running state after a successful GO action: GO is gray and STOP is red.
- In the terminal pane at the bottom labeled 'Datenaufzeichnungsstatus', the
  stopped state shows only the system or computer name. No 'Data Store' entry
  is present while Data Recording is stopped.
- During active Data Recording, a 'Data Store' entry appears in
  'Datenaufzeichnungsstatus' with a small green circular indicator before it.
- The presence of 'Data Store' with a green indicator is strong evidence that
  Data Recording is active, especially if toolbar colors are hard to distinguish.
- Do not treat a click as successful by itself. Confirm the expected state
  from the button colors and/or 'Datenaufzeichnungsstatus'.
- Once a GO click has produced an 'Erfassung wird gestartet' dialog/window or
  a 'Data Store' entry with a green indicator, consider the GO start action
  accepted. Do not click GO a second time in the same start/stop workflow.
  Continue by checking the running state and then selecting STOP.

View controls, not Data Recording:
- 'Ansichten starten' is a separate outlined green circle containing a green
  triangle/play symbol. It has an outlined gray circular pause button beside it.
- 'Ansichten starten' and its pause control do not operate Data Recording.
- For a Data Recording task, select only the filled, text-labeled GO/STOP pair.
  Never select a triangle/play-symbol button as Data Recording GO.

Confirmation dialogs:
- After clicking GO or STOP, a confirmation dialog or window may appear.
- A window titled 'Erfassung wird gestartet' means that the GO action has
  already initiated the start procedure; it is not evidence that GO failed.
- Interact with a dialog only when its purpose is clearly to confirm the Data
  Recording start or stop action required by the current task.
- If a dialog is ambiguous or requests any other change, terminate with failure.
"""
