"""TF-05: Create and configure visualization elements in design mode."""

from ui_contexts import IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-05, complex interaction and configuration of UI elements in
ibaPDA.

Project and signals under test:
- Project: test_layout_textanzeige.
- The central QPanel/display area must be empty at the beginning of the test.
  Achieve this by reloading the project at the start of the test.
- Numeric signal for the digital numeric display and trend curve:
  GenerateSignal(0,100,10,10).
- Text signal for the digital text display: GenerateText("ABC_%1").

Initialization and project reload:
1. Open ibaPDA Client by double-clicking the visible Windows desktop shortcut
   named 'ibaPDA Client'. Do not use a single click for this step; a single
   click only selects the shortcut.
2. Wait until the ibaPDA main window is visible.
3. If Data Recording is active, stop it using the filled Data Recording STOP
   button and verify that recording is stopped.
4. Reload the project test_layout_textanzeige through Datei -> Projekt öffnen:
   select the project row, confirm with Öffnen, confirm a clear project-change
   dialog with Yes if it appears, then click Initialwerte laden if that dialog
   appears.
5. Wait until the project is loaded and verify that the central QPanel/display
   area is empty.
6. Record a checkpoint confirming the freshly loaded empty QPanel.

Create visualization elements:
7. Open Entwurfsmodus/design mode by right-clicking an empty area of the
   central QPanel/display area and then left-clicking the context-menu entry
   'Entwurfsmodus'. Do not right-click the signal tree, toolbar, bottom status
   panes, tabs, or an existing visualization element for this step.
8. Verify that the additional design toolbar appears below the menu and the
   normal toolbar.
9. Open the Werkzeug/Werkzeuge tool pane using the Werkzeuge/tool-pane button in
   the design toolbar. In the reference UI this is the second icon from the left
   of the design toolbar. Use mouse_move to hover over a candidate toolbar
   button first; the button under the pointer becomes light-blue. Click only
   after the second icon from the left is highlighted. Do not click the fourth
   icon from the left: it is a book icon that opens a pane titled 'Bibliothek',
   which is the wrong pane for TF-05.
10. In the tool tree, locate the following tools:
    - Digitale Ziffernanzeige
    - Digitale Textanzeige
    - Trendkurve
    For each drag-and-drop action, first move the mouse to the source tool entry.
    Target the vertical center of the visible tool text/row when starting the
    drag. If uncertain, click the tool row once and verify that the intended row
    becomes blue highlighted before dragging. Then use left_click_drag with the
    absolute normalized screen coordinate of the intended final drop target in
    the QPanel. For the preparatory mouse_move, the marker center must be in the
    vertical middle of the source tool text, not on the upper edge of the row.
    Do not treat the drag coordinate as a relative movement.
11. Drag Digitale Ziffernanzeige from the tool tree into the upper-left part of
    the empty QPanel.
12. Drag Digitale Textanzeige from the tool tree into the upper-left part of the
    QPanel, directly to the right of the digital numeric display with visible
    spacing between the two displays.
13. Drag Trendkurve from the tool tree into a wider free area below the two
    displays, with enough vertical spacing to avoid overlap.
14. Verify that all three elements are visible and do not overlap. If any
    elements overlap, move one of the overlapping elements by dragging it to a
    nearby free area of the QPanel, then verify again. Record a checkpoint with
    their final non-overlapping positions. The empty digital numeric display is
    the small gray-framed element with black fields, yellow seven-segment
    placeholder digits, and Min/Max labels. The empty digital text display is
    the gray-framed horizontal rectangle with a black inner text area. The trend
    curve is the much larger black plotting area below them with a light toolbar
    row at the top.

Configure the digital numeric display:
15. Open the property dialog of the digital numeric display by double-clicking
    the element. Use this method strictly for the numeric display; do not use a
    right-click context menu for this element. If the double-click does not open
    the dialog, wait briefly, verify that the pointer target is centered on the
    numeric display, and try the same double-click once more.
16. Open its signal-selection dropdown by clicking vertically centered inside
    the visible text area of the closed dropdown field. Do not assume it opened
    after the click; verify that the proprietary dropdown tree is actually
    visible before selecting a signal.
17. In the dropdown tree, expand ibaPDA -> Virtuell and select
    GenerateSignal(0,100,10,10). Prefer expanding 'ibaPDA' and 'Virtuell' by
    double-clicking the visible node text. Use a normal single click only on the
    exact plus symbol for that same node row. Plus symbols are indented by tree
    level and are not all in one vertical column; if the correct plus is
    uncertain, use double-click on the node text instead. Do not use a normal
    single click on the node text to expand it. Treat a node as expanded only
    when indented child nodes appear underneath it. Treat
    GenerateSignal(0,100,10,10) as visible only when that exact readable text is
    visible in the tree. If a double-click on node text does not expand on the
    first attempt, try the same double-click once more with the pointer shifted
    vertically by no more than 5 pixels while still staying on the same node
    text/row.
18. Confirm the property dialog with OK.

Configure the trend curve:
19. Exit design mode. This is mandatory before linking the trend curve with a
    signal. To exit design mode, right-click an empty area of the central
    QPanel/display area and left-click the context-menu entry 'Entwurfsmodus'
    again. Verify that the additional design toolbar is no longer visible before
    continuing.
20. In the Signalbaum/signal tree on the left side of the main window, expand
    the node 'Virtuell' if needed and locate GenerateSignal(0,100,10,10). To
    expand 'Virtuell', preferably double-click precisely on the visible
    'Virtuell' node text. Use a normal single click only when targeting the exact
    plus symbol for the 'Virtuell' row itself. Plus symbols are indented by tree
    level and are not all in one vertical column; do not click beside the parent
    plus column when expanding 'Virtuell'. If the correct plus is uncertain, use
    double-click on the 'Virtuell' node text instead. Do not click in the gap
    between the plus symbol and the text. The true plus symbol is the leftmost
    expand/collapse control for that row; do not mistake the small signal/type
    icon between the plus and the node text for the plus symbol. Treat the node
    as expanded only when indented signal entries are visible underneath it.
    Treat GenerateSignal(0,100,10,10) as found only when that exact readable text
    is visible under 'Virtuell'. If a double-click on node text does not expand
    on the first attempt, try the same double-click once more with the pointer
    shifted vertically by no more than 5 pixels while still staying on the same
    node text/row.
21. Link the trend curve by dragging GenerateSignal(0,100,10,10) from the
    signal tree onto the trend curve element in the QPanel. Start the drag from
    the vertical center of the GenerateSignal node text/row. If uncertain, click
    the GenerateSignal row once and verify that the intended row becomes blue
    highlighted before dragging. The preparatory mouse_move must place the marker
    center vertically in the middle of the GenerateSignal text/row, not on the
    row's upper edge or on the Signalbaum pane title. The Signalbaum/signal tree
    is only the drag source; the final left_click_drag coordinate must be inside
    the trend curve element in the QPanel, not in the Signalbaum. If
    mouse-target verification shows the red crosshair in the Signalbaum, treat
    that as the wrong drag end and choose a new final drop target inside the
    trend curve. Do not use a property dialog or signal dropdown for the trend
    curve in TF-05.

Configure the digital text display:
22. Open the context menu of the digital text display with a right-click. Use
    this method strictly for the text display; do not double-click it for
    configuration in TF-05.
23. Select the properties entry from the context menu.
24. Open its signal-selection dropdown by clicking vertically centered inside
    the visible text area of the closed dropdown field. Do not assume it opened
    after the click; verify that the proprietary dropdown tree is actually
    visible before selecting a signal.
25. In the dropdown tree, expand ibaPDA -> Virtuell and select
    GenerateText("ABC_%1"). Prefer expanding 'ibaPDA' and 'Virtuell' by
    double-clicking the visible node text. Use a normal single click only on the
    exact plus symbol for that same node row. Plus symbols are indented by tree
    level and are not all in one vertical column; if the correct plus is
    uncertain, use double-click on the node text instead. Do not use a normal
    single click on the node text to expand it. Treat a node as expanded only
    when indented child nodes appear underneath it. Treat GenerateText("ABC_%1")
    as visible only when that exact readable text is visible in the tree. If a
    double-click on node text does not expand on the first attempt, try the same
    double-click once more with the pointer shifted vertically by no more than 5
    pixels while still staying on the same node text/row. Do not double-click
    the gray pane title/header bar labeled 'ibaPDA-Signalbaum'. If the
    Signalbaum pane becomes undocked/floating after an accidental double-click
    on that title/header bar, restore it by double-clicking the same gray title
    bar in the floating pane and continue only after it is docked on the left
    again.
26. Confirm the property dialog with OK.
27. Record a checkpoint confirming that the three elements have been configured.

Runtime validation:
28. Start Data Recording with the filled GO button if recording is stopped.
29. Wait until Data Recording is active and dynamic values can update.
30. Verify that the digital numeric display shows numeric values and that they
    change after a short wait.
31. Verify that the digital text display shows text values in the expected
    format beginning with 'ABC_'.
32. Verify that the trend curve displays graphical measurement data or a
    changing signal trace.
33. Record a checkpoint summarizing the observed numeric display, text display,
    and trend curve behavior.
34. Stop Data Recording with the filled STOP button and verify that recording is
    stopped.
35. Terminate with status success only after all three elements have been
    created, configured with the expected signals, validated during active Data
    Recording, and Data Recording has been stopped.

Safety restrictions:
- Do not edit unrelated settings, signals, project configuration, or application
  preferences.
- Do not save unrelated changes during the test.
- Do not allow the created visualization elements to overlap.
- Do not use answer for completion; terminate with status success or failure.
- If project reload, design mode, the tool pane, drag-and-drop creation, a
  property dialog, signal selection, or runtime validation cannot be completed
  clearly, terminate with status failure and explain the failed step.
""".strip()


CASE = UiTestCase(
    case_id="TF-05",
    description=(
        "Create and configure digital numeric display, digital text display, "
        "and trend curve in ibaPDA design mode."
    ),
    task=TASK,
    additional_system_prompt=IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT,
    allowed_actions=frozenset(
        {
            "double_click",
            "left_click",
            "right_click",
            "mouse_move",
            "left_click_drag",
            "scroll",
            "hscroll",
            "wait",
            "checkpoint",
            "terminate",
        }
    ),
    max_iterations=84,
    max_task_duration=1200,
    max_repeated_actions=2,
    max_consecutive_failures=2,
    max_executed_mouse_actions=72,
    verify_mouse_targets=True,
    abort_on_mouse_verification_failure=False,
    iteration_delay=0.2,
    post_action_delay=1.0,
    model_options={
        "temperature": 0.1,
        "num_ctx": 16384,
        "num_predict": 512,
    },
)
