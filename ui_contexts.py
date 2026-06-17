"""Application-specific UI knowledge supplied only to relevant agent tasks."""

IBAPDA_BASE_CONTEXT = """You are operating the ibaPDA Client application.

Starting ibaPDA Client:
- The Windows desktop shortcut named 'ibaPDA Client' opens the application.
- Start the application by double-clicking the 'ibaPDA Client' desktop shortcut.
  A single left click only selects the shortcut and does not open the client.
- Wait for the main window to be visibly loaded before selecting controls in
  the application toolbar.

Main ibaPDA workspace:
- The toolbar is at the top of the ibaPDA Client window.
- The central black workspace is the QPanel/display area. This display area is
  where visualization elements such as digital text displays, trend curves,
  tables, nested panels, and embedded layouts are placed.
- The QPanel/display area may show one layout directly, or a nested layout
  structure such as Main containing an embedded Layout_1 tab/container.
- When validating visualization elements, inspect the QPanel/display area rather
  than the signal tree, event log, or bottom status panes.

Tooltips:
- Many clickable ibaPDA toolbar and UI elements show a tooltip after the mouse
  hovers over them or after an attempted click.
- A tooltip is usually a small white rectangle with gray border/shadow near the
  hovered or clicked element, containing the element name or function, for
  example 'Stopp'.
- Use visible tooltip text as additional evidence for identifying the element
  currently under the pointer or the element that was just clicked.
- If a tooltip reveals that the pointer is over the wrong element, correct the
  next action instead of repeating the same click.
- Do not click the tooltip itself; it is only a temporary label and not the
  target control.
"""


IBAPDA_DATA_RECORDING_SHARED_CONTEXT = """
Data Recording controls:
- Data Recording is controlled by a filled circular GO/STOP text-button pair.
- GO is labeled 'GO' in white letters. STOP is labeled 'STOP' in white letters.
- GO is directly to the left of STOP.
- The GO/STOP pair is grouped between a two-person icon on its left and gear
  icons on its right.
- When clicking GO or STOP, target the center of the filled circular text button
  itself. For STOP, click the center of the red circle containing the
  white 'STOP' text. Do not click the gear icons or client preferences controls
  immediately to the right of STOP.

Data Recording states:
- Initial Data Recording state is not guaranteed. When the client opens, Data
  Recording may already be stopped, already running, or unavailable because no
  project/layout is loaded.
- Stopped state: GO is green and STOP is gray.
- Running state: GO is gray and STOP is red.
- Unavailable/no project or layout loaded state: both GO and STOP can be gray
  or otherwise disabled. In this state, do not infer a normal stopped/running
  recording state from button colors alone.
- In the terminal pane at the bottom labeled 'Datenaufzeichnungsstatus', the
  stopped state shows only the system or computer name. No 'Data Store' entry
  is present while Data Recording is stopped.
- During active Data Recording, a 'Data Store' entry appears in
  'Datenaufzeichnungsstatus' with a small green circular indicator before it.
- The presence of 'Data Store' with a green indicator is strong evidence that
  Data Recording is active, especially if toolbar colors are hard to distinguish.
- If the GO/STOP pair is disabled or both buttons are gray because no
  project/layout is loaded, terminate with failure unless the current task
  explicitly allows loading or changing projects/layouts.
- Do not treat a click as successful by itself. Confirm the expected state
  from the button colors and/or 'Datenaufzeichnungsstatus'.
- To start Data Recording when the current test requires active signals, click
  the center of the filled green GO button only if Data Recording is clearly
  stopped and GO is active.
- After a successful GO click, ibaPDA shows a confirmation/progress dialog or
  window for starting Data Recording, often titled 'Erfassung wird gestartet'.
  This dialog may need confirmation if a clear confirmation control is visible,
  but it can also close by itself after a few seconds.
- If Data Recording is already running, do not click GO again. Treat active
  recording as the required condition.

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
- If the 'Erfassung wird gestartet' dialog disappears by itself and the UI then
  shows active Data Recording, continue the test without clicking GO again.
- Interact with a dialog only when its purpose is clearly to confirm the Data
  Recording start or stop action required by the current task.
- If a dialog is ambiguous or requests any other change, terminate with failure.
"""


IBAPDA_TF_00_RECORDING_WORKFLOW_CONTEXT = """
Data Recording workflow for TF-00:
- If Data Recording is already running at the beginning of a start/stop test,
  do not click GO. Treat the start condition as already satisfied and proceed
  toward a verified STOP action.
- Once a GO click has produced an 'Erfassung wird gestartet' dialog/window or
  a 'Data Store' entry with a green indicator, consider the GO start action
  accepted. Do not click GO a second time in the same start/stop workflow.
  Continue by checking the running state and then selecting STOP.
- For TF-00, STOP is clicked only when Data Recording is active and STOP is red.
  Do not click a gray STOP button.
"""


IBAPDA_TF_01_LAYOUT_CONTEXT = IBAPDA_BASE_CONTEXT + IBAPDA_DATA_RECORDING_SHARED_CONTEXT + """
TF-01 project and goal:
- The relevant project is named 'test_layout_tabs'.
- The project contains a Main layout with a QPanel and an embedded tabbed layout
  container.
- The project also contains 'Layout_1' as a separately loadable layout view.
- The relevant display is a digital text display for signal '[0:0] ABC-Signal'.
- The displayed text has the format 'ABC - <number>'. The numeric value changes
  continuously while data acquisition is active.
- If Data Recording is not active, the inner area of the digital text display
  can be empty or black and the 'ABC - <number>' value may not be visible.

Layout recognition:
- The test may start in the Main layout or directly in Layout_1.
- The currently active top-level layout is shown in the closed layout selection
  dropdown in the top toolbar.
- This layout selection dropdown is located immediately to the right of the
  gear/client-preferences icon, and that gear icon follows the Data Recording
  STOP button.
- The visible text on the closed dropdown field is the current top-level layout,
  for example 'Main' or 'Layout_1'.
- Read the active top-level layout only from the visible text on the closed
  dropdown field. Do not open the dropdown just to determine which layout is
  active.
- Open the layout selection by clicking inside the closed dropdown field or its
  small arrow only when a layout change is required. This opens a proprietary navigation/tree
  that represents the available layout structure.
- Select a layout by clicking its visible entry in the opened proprietary
  layout navigation/tree. This opens the selected layout in the QPanel/display
  area.
- If the current view is already Layout_1, do not switch back to Main.
- If the current view is Main and Layout_1 is not already opened, load Layout_1
  through the layout selection control.
- Do not confuse the top toolbar layout selection dropdown with tabs inside the
  QPanel/display area. The QPanel may contain internal tabs such as 'Layout_1',
  'Layout_2', or 'Untitled 1', but TF-01 changes the top-level layout through
  the toolbar dropdown/navigation, not by clicking embedded QPanel tabs.
- Prefer visible text such as 'Main', 'Layout_1', or 'Layout 1' to identify the
  active layout state.
- After a layout switch, wait until the QPanel content is fully loaded before
  validating the text display again.

Digital text display validation:
- Identify the digital text display visually inside the QPanel/display area, not
  through a fixed technical hierarchy path.
- In the Main start layout, the QPanel can show a nested white/gray embedded
  layout container within the black display area. The ABC text display appears
  inside that nested container.
- The expected text starts with 'ABC -' followed by a changing number.
- If the digital text display frame is visible but its inner value area is empty
  or black, treat this as evidence that Data Recording may not be active yet;
  do not conclude that the ABC display is missing solely from an empty value
  area.
- To validate dynamic behavior, observe the value, wait briefly, then observe it
  again. Treat the value as dynamic only if the number after 'ABC -' changes.
- Use checkpoint actions to record observed values and layout states during the
  test. A checkpoint does not complete the task.

Data Recording for TF-01:
- The ABC-Signal value changes only when Data Recording is active.
- If Data Recording is stopped, the ABC-Signal text/value can disappear and the
  inner display area can remain black or empty.
- If the value does not change and Data Recording is clearly stopped, use the
  shared Data Recording GO instructions above to start Data Recording.
- Do not stop Data Recording as part of TF-01 unless the current UI state or a
  confirmation dialog clearly requires it for safety. The common test cleanup
  closes ibaPDA after the workflow.

Safety boundaries:
- Do not edit the project, layouts, signals, QPanel objects, or application
  configuration.
- Do not open the layout manager during the automated test; setting the start
  layout is a precondition outside the test runtime.
- If the project 'test_layout_tabs', Layout_1, the ABC display, or Data
  Recording controls cannot be identified clearly, terminate with failure.
"""


IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT = IBAPDA_BASE_CONTEXT + IBAPDA_DATA_RECORDING_SHARED_CONTEXT + """
TF-02 project and goal:
- The relevant project is named 'test_layout_dynamic' in the ibaPDA title bar.
  In some documentation it may also be referred to as 'test_layout_dynamisch'.
- TF-02 validates several visually similar gray rectangular digital text labels
  in the QPanel/display area.
- The labels use green text while Data Recording is active. If Data Recording is
  stopped, the dynamic text may be empty and only the gray label background may
  remain visible.

TF-02 layout structure:
- The QPanel/display area has a mostly white background with a green heading
  'label dynamic' near the upper left.
- There are four relevant gray rectangular dynamic labels arranged in three
  rows. They are structurally and visually similar, so identify them by row,
  content type, and neighboring controls.
- First row: one numeric label on the left and one text label to its right.
- Second row: one numeric label on the left, with two buttons labeled 'visible'
  and 'invisible' to its right. These buttons control the visibility of that
  entire second-row numeric label element, including the gray rectangle and its
  dynamic text.
- Third row: one text label on the left, with two buttons labeled 'active' and
  'inactive' to its right. These buttons control the interactivity/enabled state
  of that third-row text label.
- Numeric labels show changing decimal values, for example '430.45' or values
  with a comma decimal separator.
- Text labels show text beginning with 'FreeText' followed by a changing suffix,
  for example 'FreeTextX'.

Dynamic content validation:
- Identify all four relevant dynamic labels and assign them to their positions:
  first-row numeric, first-row text, second-row numeric controlled by
  visible/invisible, and third-row text controlled by active/inactive.
- The second-row numeric label controlled by visible/invisible can already be
  invisible at the beginning of the test. If the layout shows too few labels or
  the second-row numeric label cannot be found, click 'visible' once before
  concluding that the label is missing.
- To validate dynamic content, observe the labels, wait briefly, then observe
  them again.
- The two numeric labels should show the same current DynVal signal value, or
  clearly equivalent current values if the value updates between observations.
- The two text labels should show FreeText-based values following the same
  LabelText update pattern.
- Use checkpoint actions to record observed label positions, visible values, and
  state changes.

Visibility validation:
- Use the 'invisible' button beside the second-row numeric label to hide that
  entire label element.
- Verify visually that the entire second-row numeric label disappears, including
  its gray rectangular background and its dynamic value text.
- Use the 'visible' button to show the second-row numeric label again.
- Verify that the second-row numeric label can be identified again and displays
  a valid dynamic numeric value.

Interactivity validation:
- Use the 'inactive' button beside the third-row text label to disable that
  text label.
- Verify that a right-click on the third-row text label does not open the
  expected context menu.
- Use the 'active' button to enable that third-row text label again.
- Verify that a right-click on the third-row text label opens a context menu
  containing an item such as 'Eigenschaften' or another clearly label-related
  context menu entry.
- Close any opened context menu after validation without changing properties by
  clicking an empty area of the QPanel/display area next to the labels.

Safety boundaries:
- Do not edit projects, signals, label properties, QPanel objects, or
  measurement configuration.
- The TF-02 project is expected to be loaded before the test starts. Do not open
  another project during TF-02.
- Interact only with Data Recording controls, the four relevant dynamic labels,
  and the visible/invisible/active/inactive buttons required for TF-02.
- If the TF-02 project, the dynamic label layout, required buttons, or Data
  Recording controls cannot be identified clearly, terminate with failure.
"""


IBAPDA_PROJECT_OPEN_CONTEXT = """
Project opening workflow for later test cases:
- To load another project, use the menu bar path Datei -> Projekt öffnen.
- In the project-open dialog, select the intended project row in the table and
  confirm with the 'Öffnen' button.
- If Data Recording is running while opening another project, ibaPDA may show an
  additional confirmation dialog. Confirm it with 'Yes' only if it clearly asks
  to continue opening the selected project.
- After selecting the project, another dialog may ask how to load initial values.
  Click the 'Initialwerte laden' button to continue loading the project.
- Wait until the selected project is loaded before validating its layout.
"""


IBAPDA_DATA_RECORDING_CONTEXT = (
    IBAPDA_BASE_CONTEXT
    + IBAPDA_DATA_RECORDING_SHARED_CONTEXT
    + IBAPDA_TF_00_RECORDING_WORKFLOW_CONTEXT
)


# Backward-compatible name used by existing TF-00 imports.
IBAPDA_UI_CONTEXT = IBAPDA_DATA_RECORDING_CONTEXT
