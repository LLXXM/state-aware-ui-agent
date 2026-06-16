"""Application-specific UI knowledge supplied only to relevant agent tasks."""

IBAPDA_UI_CONTEXT = """You are operating the ibaPDA Client application.

Starting ibaPDA Client:
- The Windows desktop shortcut named 'ibaPDA Client' opens the application.
- You must double-click the desktop icon to open the application. Single-clicking is not sufficient.
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
- The STOP button being red is direct evidence that Data Recording is active,
  even if the GO button color is difficult to judge.
- The GO button being gray while STOP is red means Data Recording is active.
  Never describe that state as stopped.
- The GO button being green while STOP is gray means Data Recording is stopped.
  Never describe that state as active.
- The exact ibaPDA pane name is 'Datenaufzeichnungsstatus'. Use that exact
  name when referring to this pane.
- When the 'Datenaufzeichnungsstatus' pane is open, its content is visible
  directly above the bottom tab bar. In the stopped state, that content shows
  only the system or computer name. No 'Data Store' entry is present while Data
  Recording is stopped.
- During active Data Recording, a 'Data Store' entry appears in
  'Datenaufzeichnungsstatus' with a small green circular indicator before it.
- The presence of 'Data Store' with a green indicator is strong evidence that
  Data Recording is active, especially if toolbar colors are hard to distinguish.
- The bottom tab bar can show tabs such as 'Datenaufzeichnungsstatus',
  'ibaPDA-Ereignisprotokoll', 'ibaHD-Ereignisprotokoll',
  'Ueberwachungsfenster', and 'Digitalanzeigen'. Seeing the bottom
  'Datenaufzeichnungsstatus' tab alone means only that the pane is available;
  it does not mean the pane is open.
- The 'Datenaufzeichnungsstatus' pane can be collapsed or hidden. If only the
  bottom tab bar is visible and there are no status rows directly above it,
  click the tab labeled 'Datenaufzeichnungsstatus' to open or dock the pane
  before deciding whether a Data Store entry is present or absent.
- If the 'Datenaufzeichnungsstatus' pane is collapsed, absence of a visible
  Data Store entry is not evidence that Data Recording is stopped.
- Do not treat a click as successful by itself. Confirm the expected state
  from the button colors and/or 'Datenaufzeichnungsstatus'.
- Once a GO click has produced an 'Erfassung wird gestartet' dialog/window or
  a 'Data Store' entry with a green indicator, consider the GO start action
  accepted. Do not click GO a second time in the same start/stop workflow.
  Continue by checking the running state and then selecting STOP.

Required state check before every Data Recording action:
- Before clicking GO or STOP, classify the visible Data Recording state as one
  of exactly these cases:
  1. stopped: GO is green and STOP is gray, and no Data Store entry is visible.
  2. active: STOP is red, or GO is gray and STOP is red, or a Data Store entry
     with a green indicator is visible.
  3. starting_or_stopping: a clear Data Recording start/stop dialog or progress
     window is visible.
  4. status_pane_collapsed: only the bottom tab bar is visible; the
     'Datenaufzeichnungsstatus' tab may be visible, but no status content rows
     are visible directly above the tab bar.
  5. unclear: the GO/STOP pair and 'Datenaufzeichnungsstatus' pane cannot be
     read reliably.
- If the state is active, the next Data Recording control is STOP, not GO.
- If the state is stopped and the current task still needs to start recording,
  the next Data Recording control is GO.
- If the state is status_pane_collapsed, click the bottom
  'Datenaufzeichnungsstatus' tab first, then inspect the state again.
- If the state is unclear, do not guess by clicking GO. Wait once if the UI may
  still be loading; otherwise terminate with failure.

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

Loading projects:
- Use menu "Datei" -> "Projekt öffnen" to load a project
- After selecting a project from the dropdown, confirm with "Öffnen"
- If a dialog appears due to active recording, confirm it

Layout:
- On the left side there is the navigation tree "ibaPDA-Signalbaum"
- Next to the right the big grey layout labeled "Untitled 1" is called "QPanel"
- the QPanel is a layout container which can be filled with UI-Elements for data representation and visualization, called "QPanel Elements"
- Layouts can be grouped
- You can switch layouts by using the left layout selection dropdown in the menu  
- The layout selection dropdown shows the currently loaded layout (Main, Layout 1, Layout 2) 
"""
