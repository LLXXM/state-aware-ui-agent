"""Application-specific UI knowledge supplied only to relevant agent tasks."""

IBAPDA_BASE_CONTEXT = """You are operating the ibaPDA Client application.

Starting ibaPDA Client:
- The Windows desktop shortcut named 'ibaPDA Client' opens the application.
- Start the application by double-clicking the 'ibaPDA Client' desktop shortcut.
  A single left click only selects the shortcut and does not open the client.
- If an ibaPDA loading screen or splash screen appears after the double-click,
  treat the desktop shortcut launch as successful. Do not double-click the
  shortcut again; wait until the main window is available, for up to 1 minute.
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

Proprietary navigation and selection trees:
- ibaPDA often uses proprietary tree controls in dialogs, dropdowns, tool panes,
  layout selectors, and signal selectors. These trees may not behave like
  standard HTML or file-system trees.
- Tree entries are selected by clicking the visible text or row of the entry.
  A selected entry is often highlighted, commonly with a blue selection
  background.
- When clicking, double-clicking, or starting a drag from a tree entry, target
  the vertical center of the visible node text or row. Avoid the upper/lower
  edge of the row, tiny icons, and empty spacing.
- To verify that the intended node text/row was targeted, you may first click
  the node text/row once and check whether that exact row becomes highlighted
  blue. Use that as selection evidence, not as proof of expansion.
- During mouse-target verification, a blue-highlighted tree row may still be
  the row selected by a previous click. Do not treat an old blue highlight as
  proof that the new red marker target is wrong. Judge whether the marker center
  is on the intended current node text/row.
- This also applies when verifying left-clicks or double-clicks on tree node
  text such as 'Virtuell': approve a correctly centered marker on the intended
  node text even if another row is still blue-highlighted from the previous
  selection.
- Nodes with a small plus symbol or collapsed branch indicator can be expanded.
  Prefer expanding by double-clicking the visible node text. Use the plus symbol
  only if the correct plus for that exact node row is clearly visible and
  targetable.
- When expanding a tree node, target either the plus symbol itself or the
  visible node text. Use a normal single click only on the plus symbol; use a
  double-click on the node text. Do not single-click the node text when the goal
  is to expand it, and do not click in the empty gap between the plus symbol and
  the node name; this may select nothing and leave the tree collapsed.
- Plus symbols are indented with their tree level. Do not assume all plus
  symbols are in one vertical column. For child nodes, the plus symbol is
  shifted to the right compared with its parent. If the correct plus position is
  uncertain, use a double-click on the visible node text instead.
- If expansion by double-clicking the node text does not work on the first
  attempt, try the same double-click once more with the pointer shifted
  vertically by no more than 5 pixels, while still staying within the vertical
  center band of the same node text/row.
- Some tree rows contain a small icon between the plus symbol and the node text.
  Do not confuse that icon with the plus symbol. The true plus symbol is the
  expand/collapse control at the far left of the tree row; if unsure, use a
  double-click on the vertical center of the visible node text instead.
- Nodes with a minus symbol or expanded branch indicator are already expanded.
  Do not collapse them unless the current task explicitly requires it.
- Treat a node as successfully expanded only when new indented child nodes are
  visible underneath the targeted parent node. Do not rely on a suspected
  plus/minus symbol alone as proof of expansion.
- Treat a target leaf item as visible only when its actual text is readable in
  the tree. For example, do not claim GenerateSignal(0,100,10,10) is visible
  unless that exact text is visible as an entry under the expanded parent.
- Child nodes are visually indented below their parent. Use this indentation and
  the parent-child path to distinguish similarly named entries.
- If several entries contain similar words, prefer the full hierarchy path over
  a single text match, for example parent -> child.
- Dropdown trees can open from a closed field that displays the current text.
  Open such a tree by clicking the visible text/field of the closed dropdown,
  then click the target tree entry once to select it.
- After selecting an entry from a dropdown tree, confirm the surrounding dialog
  with OK only when the intended selection is visible or otherwise clearly
  accepted.

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

Mouse target verification overlays:
- Planned mouse-target screenshots may contain a red crosshair and a white label
  describing the proposed action. The crosshair and label can cover UI text,
  icons, borders, or parts of the intended control.
- When interpreting these overlay screenshots, account for the possibility that
  the marker itself hides content underneath. Judge the center of the crosshair
  together with the surrounding layout and nearby UI geometry.
- Only the center point/dot of the crosshair is the target. The red line arms
  are visual guides and must not be treated as the click, hover, or drag-start
  location.
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
  but it can also close by itself after a few seconds. The dialog should appear
  within about 3 seconds after the GO click if the click was accepted.
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
- If no start dialog appears within about 3 seconds and Data Recording does not
  become active, treat the GO click as not clearly accepted and choose a
  corrected next action based on the current screenshot. Do not repeat the exact
  same GO click coordinates with the same intent.
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


IBAPDA_CLIENT_PREFERENCES_TREE_CONTEXT = """
Client preferences dialog and tree navigation:
- The Client Preferences dialog is opened from the small gear icon directly to
  the right of the Data Recording STOP button in the top toolbar. This is the
  client-preferences gear, not the Data Recording GO/STOP pair itself.
- In the top toolbar, locate the filled circular Data Recording buttons first:
  GO is on the left and STOP is immediately to its right. The client-preferences
  gear icon is the small black/gray gear immediately to the right of STOP and
  immediately to the left of the layout selection dropdown. It is the first gear
  after the GO/STOP pair.
- Do not click other gear-like icons elsewhere in the toolbar or inside the
  Client Preferences dialog. Use nearby controls and tooltips to confirm that
  the hovered icon is the client preferences/settings control.
- Data Recording is not required for client-preferences navigation. Do not
  start or stop Data Recording for tests that only inspect Client Preferences.
- The dialog contains a proprietary navigation tree on the left and a settings
  area for the selected node on the right.
- When the dialog opens, the first/root node is normally selected. In German
  this node is 'Allgemein' and the selected row is highlighted in blue.
- Selecting a node in the left tree changes the settings area on the right.
  Validate both the selected tree text and that the right settings area changes
  to a plausible page for that selected node.
- Tree nodes with a small plus symbol can be expanded. Expand such a node by
  double-clicking the node name, not by clicking random empty tree space.
- Nodes without a plus symbol are leaf nodes and should be selected with a
  normal click.
- The node 'Kreisansicht' / 'Circle View' / '圆视图' is normally collapsed when
  the dialog opens. Expand it before selecting its child 'Ansicht' / 'Visuals'
  / '显示'.
- Multiple nodes can contain similar words, for example 'Ansicht' also appears
  inside names like 'FFT-Ansicht'. Use hierarchy and the parent node to avoid
  selecting the wrong entry.
- Close the dialog with 'Abbrechen' / 'Cancel' or the equivalent cancel button
  after validation. Use 'OK' only if the test explicitly requires accepting a
  settings change.
"""


IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT = (
    IBAPDA_BASE_CONTEXT
    + IBAPDA_CLIENT_PREFERENCES_TREE_CONTEXT
    + """
TF-03 project and goal:
- TF-03 validates text-based identification in the Client Preferences dialog.
- The test is independent from the currently loaded project/layout.
- The same navigation flow is validated in German, English, and Chinese.
- Language changes are performed through the application menu path
  View/Ansicht -> Language/Sprache -> target language, depending on the
  currently active UI language.
- After changing the language, ibaPDA may show a confirmation dialog and may
  restart or require waiting until the UI is available again. Confirm only
  clear language-change/restart prompts and wait for the main window to return.

Language and translation rules:
- When validating translated UI labels or menu entries, do not require an exact
  literal word-by-word match if the visible text is semantically and
  contextually correct.
- Minor wording differences, shortened labels, industry-specific terminology,
  or localized synonyms are acceptable if the intended meaning is preserved.
- For Chinese labels, small glyphs and OCR artifacts are expected. Use the
  visible tree position, icon, hierarchy, selection highlight, and right-side
  settings page as supporting evidence.
- A selected tree node is visually highlighted in blue. Use this highlight as
  evidence that the intended node was selected.

TF-03 language-specific target labels:
- German run:
  - Menu path: Ansicht -> Sprache -> Deutsch
  - Dialog title: Client-Voreinstellungen
  - Root/general node: Allgemein
  - Text display node: Digitale Textanzeige
  - Nested tree path: Kreisansicht -> Ansicht
  - Dialog buttons: OK, Abbrechen
- English run:
  - Menu path: View -> Language -> English
  - Dialog title: Client Preferences or equivalent client preferences title
  - Root/general node: General
  - Text display node: Text digital display
  - Nested tree path: Circle View -> Visuals
  - Dialog buttons: OK, Cancel
- Chinese run:
  - Menu path: the localized View/Language menu to select Chinese
  - Root/general node: 概 览
  - Text display node: 文本数 显
  - Nested tree path: 圆视图 -> 显示
  - Dialog buttons: localized OK and cancel buttons

Validation scope:
- For each language, open Client Preferences, identify the left navigation tree,
  select the root/general node, select the text digital display node, expand
  the circle-view node, select its visuals/view child, and record checkpoints.
- For every selected node, verify the visible selected text and that the
  right-side settings area is present and plausible for the selected category.
- Do not edit settings, change numeric values, toggle checkboxes, reset client
  settings, or change project/layout configuration.
- If a required language, menu item, dialog, node, or settings area cannot be
  identified clearly, terminate with failure.
"""
)


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


IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT = (
    IBAPDA_BASE_CONTEXT
    + IBAPDA_DATA_RECORDING_SHARED_CONTEXT
    + """
TF-05 project and goal:
- The relevant project is named 'test_layout_textanzeige'.
- TF-05 starts from a freshly reloaded project with an empty central QPanel or
  empty central display area. Reload the project at the beginning even if it
  already appears to be loaded, so the QPanel is clean.
- The test creates and configures three visualization elements: a digital
  numeric display, a digital text display, and a trend curve.
- The numeric display and trend curve use the signal GenerateSignal(0,100,10,10).
- The digital text display uses the text signal GenerateText("ABC_%1").

Project reload for TF-05:
- At the start of TF-05, use Datei -> Projekt öffnen, select the project
  'test_layout_textanzeige', confirm with 'Öffnen', and then click
  'Initialwerte laden' if the initial-values dialog appears.
- If Data Recording is running while the project is reloaded, confirm the clear
  project-change dialog with 'Yes' and wait for the reload to finish.
- After reload, verify that the central QPanel/display area is empty before
  creating new visualization elements.

Design mode and design toolbar:
- Open Entwurfsmodus/design mode before creating visualization elements.
- To open design mode, right-click an empty area of the central QPanel/display
  area and then left-click the context-menu entry 'Entwurfsmodus'.
- To exit design mode, use the same toggle: right-click an empty area of the
  central QPanel/display area and left-click the context-menu entry
  'Entwurfsmodus' again. Then verify that the additional design toolbar is no
  longer visible before continuing.
- Use a clearly empty part of the QPanel for this right-click. Do not right-click
  the signal tree, bottom Data Recording status pane, tabs, toolbar, or an
  existing visualization element when trying to open design mode.
- In design mode, an additional toolbar appears directly below the menu bar and
  the normal toolbar containing GO, STOP, the client-preferences gear, and the
  layout dropdown.
- The design toolbar belongs to the active QPanel tab, such as 'Untitled 1'.
- The Werkzeuge/tool-pane button is in this design toolbar. In the TF-05
  reference UI it is the second icon from the left side of that design toolbar.
  It opens the Werkzeug/Werkzeuge tool navigation pane.
- When the mouse hovers over a button in the design toolbar, the button under
  the pointer is highlighted with a light-blue background. Use the mouse_move
  action to hover over a candidate button and verify the light-blue highlight
  before clicking. Do not click until the highlighted button is the intended
  second icon from the left.
- The fourth icon from the left is a book icon and opens a pane titled
  'Bibliothek'. That is the wrong pane for TF-05. If 'Bibliothek' appears, treat
  it as evidence that the wrong icon was clicked; close or ignore that pane and
  open 'Werkzeuge' with the second icon from the left instead.
- Do not confuse this design toolbar button with the client-preferences gear in
  the main toolbar or the Data Recording controls.

Tool navigation pane:
- The tool pane is titled 'Werkzeuge'. It opens to the left of the QPanel
  editing area, beside the signal tree.
- The tool pane contains a proprietary navigation tree: select entries by
  clicking their visible text or row, use indentation to understand parent-child
  hierarchy, and expand collapsed plus-symbol nodes only if needed. No node is
  preselected and all relevant nodes should already be expanded.
- Relevant tree sections include 'Standardwerkzeuge', 'Ansichten',
  'Anzeigeelemente', and individual tools such as 'Trendkurve',
  'Digitale Textanzeige', and 'Digitale Ziffernanzeige'.
- Add tools by dragging the tool entry from the tool tree into free space in
  the central QPanel. Place the elements with enough spacing so they do not
  overlap.
- When selecting or dragging a tool entry, target the vertical center of the
  tool's visible text/row. If uncertain whether the intended tool row is being
  targeted, click the tool row once and verify that that exact row becomes blue
  highlighted before starting the drag.
- For a mouse_move that prepares dragging a tool entry, the marker center must
  be vertically centered on the intended tool text itself. Do not place the
  marker on the upper edge of the text row, because the drag may start from the
  row above or from a pane title such as 'Signalbaum'.
- Use mouse_move to position the pointer on the tool entry first, then use
  left_click_drag to drag to the absolute target position in the QPanel.
- The coordinate for left_click_drag is an absolute normalized screen
  coordinate of the final drop target, not a relative movement from the tool
  entry. First move to the source tool, then drag to the absolute QPanel
  destination.

Element placement:
- Place the digital numeric display, digital text display, and trend curve in
  separate areas of the empty QPanel.
- Empty digital numeric display: a small gray-framed element with black display
  fields, yellow seven-segment placeholder digits, and 'Min:'/'Max:' labels.
- Empty digital text display: a gray-framed horizontal rectangle with a black
  inner text area.
- Empty trend curve: a much larger black plotting area with a light toolbar row
  at the top containing small gray control icons.
- Place the two display elements in the upper-left part of the empty QPanel:
  put the digital numeric display first at the upper-left, then put the digital
  text display directly to its right with visible spacing between them.
- Place the trend curve below the two display elements, with enough vertical
  spacing that it does not overlap either display.
- After each drag-and-drop, wait briefly and visually confirm that a new element
  appeared before adding the next one.
- Before starting configuration, verify that the three elements do not overlap.
- If any created elements overlap, move one of the overlapping elements by
  dragging it to a nearby free area of the QPanel before continuing. Do not
  configure or validate overlapped elements.

Property dialogs and signal dropdowns:
- Use the exact configuration method specified for each element. Do not choose
  between double-click and right-click yourself.
- For TF-05, configure the digital numeric display only by double-clicking the
  digital numeric display element.
- If the double-click on the digital numeric display does not open the property
  dialog, wait briefly, verify that the pointer target is centered on that
  element, and try the same double-click method once more. Do not switch to the
  right-click context-menu method for this element.
- For TF-05, configure the digital text display only by right-clicking the
  digital text display element and selecting its properties entry from the
  context menu.
- For TF-05, configure the trend curve only by dragging the signal from the
  Signalbaum/signal tree onto the trend curve after design mode has been
  exited.
- Signal selection controls in these dialogs are proprietary dropdowns with a
  visible closed text field. Open the signal dropdown by clicking the visible
  text of the closed dropdown field.
- Click vertically centered inside the visible closed dropdown text field. Do
  not click above, below, or just beside the field; imprecise clicks may do
  nothing.
- Do not assume the signal dropdown opened just because it was clicked. Treat it
  as open only when the proprietary dropdown tree becomes visible underneath or
  near the field.
- The opened signal dropdown contains a small proprietary navigation tree,
  where entries are selected by clicking their visible text and parent-child
  hierarchy is indicated by indentation.
- Select signals by expanding 'ibaPDA' -> 'Virtuell' -> the desired signal.
- In a signal dropdown tree, expand 'ibaPDA' exactly like any other tree node:
  either single-click the plus symbol next to 'ibaPDA' or double-click the
  visible 'ibaPDA' node text. Do not use a normal single click on the 'ibaPDA'
  text to expand it.
- After expanding 'ibaPDA', expand 'Virtuell' the same way: single-click its plus
  symbol or double-click its visible node text. Treat expansion as successful
  only when indented child nodes appear underneath the targeted parent.
- Use a normal click on the desired signal to select it.
- Confirm each property dialog with 'OK' after the correct signal is selected.
- If a dialog provides multiple signal fields, change only the field required
  for the current element. Do not modify unrelated settings.

Signal tree for trend curve assignment:
- The Signalbaum/signal tree is the proprietary selection tree on the left side
  of the ibaPDA main window, to the left of the central QPanel/display area.
- The gray title/header bar labeled 'ibaPDA-Signalbaum' belongs to the pane
  itself, not to a signal node. Do not double-click or drag from this title bar
  when trying to expand or select 'Virtuell' or a signal.
- If the Signalbaum pane becomes undocked or floating after an accidental
  double-click on the gray 'ibaPDA-Signalbaum' title/header bar, restore it by
  double-clicking the same gray title/header bar in the floating pane. Then
  continue only after the Signalbaum is docked on the left side again.
- It contains the available signals for the loaded project.
- For TF-05, use the node 'Virtuell' in the signal tree. Expand it if needed and
  locate the signal GenerateSignal(0,100,10,10).
- When expanding 'Virtuell', preferably double-click precisely on the visible
  'Virtuell' node text. Use a normal single click on the plus symbol only if
  targeting the exact plus symbol for the 'Virtuell' row itself.
- In the Signalbaum, plus symbols are indented according to tree depth. The
  plus for 'Virtuell' is not necessarily vertically aligned with the plus for
  its parent. Do not click beside the parent plus column when trying to expand a
  child node; if unsure, double-click the 'Virtuell' node text instead.
- Do not click in the space between the plus symbol and the text.
- In the signal tree, target the vertical center of the visible node text/row
  when selecting, double-clicking, or starting a drag. If needed, first click
  the node text/row once and verify that the correct row becomes blue
  highlighted before using it as a drag source.
- For a mouse_move that prepares dragging GenerateSignal, the marker center
  must be vertically centered on the GenerateSignal text/row. Do not start the
  drag from the top border of the row or from the pane title/header; that can
  drag or select the wrong item such as 'Signalbaum'.
- Do not mistake the small signal/type icon between the expand control and the
  node text for the plus symbol. The plus symbol is the leftmost expand/collapse
  control for the row.
- Consider 'Virtuell' expanded only if indented signal entries appear underneath
  it. A suspected minus symbol alone is not sufficient proof that expansion
  succeeded.
- Consider GenerateSignal(0,100,10,10) found only when the exact readable
  GenerateSignal(0,100,10,10) text is visible under 'Virtuell'. If it is not
  visible, continue expanding or correcting the tree state instead of claiming
  it is visible.
- The trend curve is linked by dragging the signal from the signal tree onto
  the trend curve visualization element in the QPanel.
- For this signal assignment, the signal tree is only the drag source. The final
  left_click_drag coordinate must be inside the trend curve element in the
  QPanel/display area. A drop target in the Signalbaum/signal tree is wrong and
  must be corrected.
- Do not configure the trend curve through a property dialog or signal dropdown
  for TF-05. The required interaction is signal-tree drag-and-drop.
- Design mode must be exited before assigning the signal to the trend curve.
- Use mouse_move to position the pointer on the GenerateSignal entry in the
  signal tree first, then use left_click_drag to drag to the absolute target
  position inside the trend curve element. During mouse-target verification,
  the red crosshair for this drag must appear over the trend curve destination,
  not over the Signalbaum source.

Runtime validation:
- After creating and configuring all three elements, exit design mode.
- Start Data Recording only after the elements are configured.
- Validate that the digital numeric display shows changing numeric values.
- Validate that the digital text display shows text in the expected format,
  for example values beginning with 'ABC_'.
- Validate that the trend curve shows graphical measurement data or a changing
  signal trace.
- Stop Data Recording after validation.

Safety boundaries:
- Do not save unrelated project changes or modify unrelated application
  settings.
- Do not allow visualization elements to overlap in a way that prevents
  validation.
- If project reload, empty QPanel, design mode, the tool pane, a required tool,
  a property dialog, a signal dropdown, or Data Recording controls cannot be
  identified clearly, terminate with failure.
"""
)


IBAPDA_TF_06_SEMANTIC_STATE_CONTEXT = (
    IBAPDA_BASE_CONTEXT
    + IBAPDA_DATA_RECORDING_SHARED_CONTEXT
    + """
TF-06 project and goal:
- The relevant project is named 'test_layout_multistatelabel'.
- TF-06 validates semantic consistency between a trend curve and a
  multistatelabel in the QPanel/display area.
- Both visualization elements are driven by the same dynamic triangle signal
  with a value range from -100 to 100.
- This is a runtime validation test. Do not edit the project, do not enter
  design mode, do not open property dialogs, and do not change signal
  assignments.

Relevant visualization elements:
- The trend curve is the large black chart in the QPanel/display area. It has a
  grid, time labels on the x-axis, a blue signal trace, blue y-axis labels from
  about -100 to 100 on the right side, and a small toolbar above the chart.
- The signal trace should look like a triangle signal: it rises and falls
  approximately linearly between negative and positive values.
- The multistatelabel is a rectangular colored label below the trend curve. It
  changes both text and background color based on the current signal state.
- In the positive state, the multistatelabel shows the text 'Wert > 0' on a
  green background.
- In the negative state, the multistatelabel shows the text 'Wert < 0' on a red
  background.

Semantic consistency rules:
- If the current signal state in the trend curve is positive, the
  multistatelabel must show 'Wert > 0' and must have a green background.
- If the current signal state in the trend curve is negative, the
  multistatelabel must show 'Wert < 0' and must have a red background.
- Validate the signal state, label text, and label background color from the
  same full-screen observation whenever possible. Do not zoom into only one
  element in a way that separates the label state from the trend state in time.
- A state is stable enough for validation when the label text and background
  color remain consistent across two observations separated by a short wait.
- Because the signal changes continuously, the trend curve may update while the
  screenshot is being interpreted. Use repeated observations and checkpoints
  instead of judging a transient border-crossing frame as failure.
- The positive and negative states must both be observed at least once before
  TF-06 can succeed.

Runtime validation:
- Data Recording must be active for the dynamic trend curve and multistatelabel
  to update. If Data Recording is stopped, start it using the shared Data
  Recording GO instructions.
- If Data Recording is active but the label is near a transition or the trend
  state is ambiguous, wait briefly and observe again.
- Use checkpoint actions to record each validated state. Each checkpoint should
  mention the observed trend state, label text, label background color, and
  whether the consistency rule was satisfied.

Safety boundaries:
- Do not open or switch projects during TF-06. The project is expected to be
  loaded when ibaPDA starts.
- Do not enter design mode, move visualization elements, modify labels, modify
  the trend curve, or save project changes.
- Do not use answer for completion; terminate with status success or failure.
- If the project, trend curve, multistatelabel, Data Recording controls, or one
  of the two semantic states cannot be identified clearly, terminate with
  failure and explain the missing or inconsistent observation.
"""
)


IBAPDA_DATA_RECORDING_CONTEXT = (
    IBAPDA_BASE_CONTEXT
    + IBAPDA_DATA_RECORDING_SHARED_CONTEXT
    + IBAPDA_TF_00_RECORDING_WORKFLOW_CONTEXT
)


# Backward-compatible name used by existing TF-00 imports.
IBAPDA_UI_CONTEXT = IBAPDA_DATA_RECORDING_CONTEXT
