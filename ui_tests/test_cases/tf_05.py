"""TF-05: Create and configure visualization elements in design mode."""

from ui_tests.contexts.ibapda import IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-05, complex interaction and configuration of UI elements in
ibaPDA.

Goal:
- Reload project test_layout_textanzeige so the central QPanel/display area is
  empty.
- Create three visualization elements in design mode:
  Digitale Ziffernanzeige, Digitale Textanzeige, and Trendkurve.
- Place them in a non-overlapping layout: numeric display top-left, text display
  directly to its right, trend curve below both.
- Configure the numeric display and trend curve with GenerateSignal(0,100,10,10).
- Configure the text display with GenerateText("ABC_%1").
- Validate all three elements during active Data Recording, then stop Data
  Recording before terminating successfully.

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
   central QPanel/display area and selecting the context-menu entry
   'Entwurfsmodus'.
8. Verify that the additional design toolbar appears below the menu and the
   normal toolbar.
9. Open the Werkzeug/Werkzeuge tool pane from the design toolbar.
10. Drag Digitale Ziffernanzeige into the upper-left part of the empty QPanel.
11. Drag Digitale Textanzeige directly to the right of the digital numeric
    display with visible spacing.
12. Drag Trendkurve into a wider free area below both displays.
13. Verify that all three elements are visible, correctly placed, and not
    overlapping. If needed, move misplaced or overlapping elements before
    continuing. Record a checkpoint that explicitly states the final position of
    each element.

Configure the digital numeric display:
14. Open the property dialog of the digital numeric display by double-clicking
    the element.
15. In the Datensignal signal-selection dropdown, select
    GenerateSignal(0,100,10,10) via ibaPDA -> Virtuell.
16. Confirm the property dialog with OK.

Configure the trend curve:
17. Exit design mode before linking the trend curve with a signal.
18. In the Signalbaum/signal tree, locate GenerateSignal(0,100,10,10) under
    Virtuell.
19. Link the trend curve by dragging GenerateSignal(0,100,10,10) from the
    Signalbaum/signal tree onto the trend curve element in the QPanel.

Configure the digital text display:
20. Open the digital text display properties through its right-click context
    menu.
21. In the Datensignal signal-selection dropdown, select GenerateText("ABC_%1")
    via ibaPDA -> Virtuell.
22. Confirm the property dialog with OK.
23. Record a checkpoint confirming that the three elements have been configured.

Runtime validation:
24. Start Data Recording with the filled GO button if recording is stopped.
25. Wait until Data Recording is active and dynamic values can update.
26. Verify that the digital numeric display shows numeric values and that they
    change after a short wait.
27. Verify that the digital text display shows text values in the expected
    format beginning with 'ABC_'.
28. Verify that the trend curve displays graphical measurement data or a
    changing signal trace.
29. Record a checkpoint summarizing the observed numeric display, text display,
    and trend curve behavior.
30. Stop Data Recording with the filled STOP button and verify that recording is
    stopped.
31. Terminate with status success only after all three elements have been
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
