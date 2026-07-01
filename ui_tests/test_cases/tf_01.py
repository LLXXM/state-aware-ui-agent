"""TF-01: Validate dynamic ABC display across layout hierarchy changes."""

from ui_contexts import IBAPDA_TF_01_LAYOUT_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-01, robustness against layout and hierarchy changes in ibaPDA.

This test is designed to be reusable for both documented start states:
- Run 1 precondition: the project starts in the Main layout.
- Run 2 precondition: the project starts directly in Layout_1.
The start layout is configured outside the automated test runtime. Do not open
the layout manager or change persistent layout configuration during this test.

Project and signal under test:
- Project: test_layout_tabs.
- Relevant display: digital text display for signal '[0:0] ABC-Signal'.
- Expected visible text format: 'ABC - <number>'.
- The number after 'ABC -' must change over time while Data Recording is active.

Test steps:
1. Open ibaPDA Client by double-clicking the visible Windows desktop shortcut
   named 'ibaPDA Client'. Do not use a single click for this step; a single
   click only selects the shortcut.
2. Wait until the ibaPDA Client main window and its QPanel content are fully visible.
3. Determine whether the current layout state is Main or Layout_1.
4. Ensure Data Recording is active enough for the ABC value to update:
   - Observe the visible 'ABC - <number>' text if it is already available.
   - Wait briefly and observe the value again.
   - If the value does not change and the filled Data Recording GO button is
     clearly active, click the center of GO to start Data Recording and wait for
     the value to begin changing.
5. Identify the digital text display for '[0:0] ABC-Signal' in the current QPanel.
6. Record a checkpoint with the current layout state and the observed ABC value.
7. Verify that the displayed text starts with 'ABC -' and that the numeric value
   changes after a short wait.
8. If the current layout is Main, load Layout_1 through the layout selection
   control/dropdown. Do not switch to Main if Layout_1 is already loaded.
9. Only if step 8 actually switched from Main to Layout_1, wait until Layout_1
   and its QPanel content are fully loaded.
10. Only if a layout switch was necessary, identify the digital text display
    again after the layout state changed.
11. Only if a layout switch was necessary, record another checkpoint with the
    current Layout_1 state and the observed ABC value after the switch.
12. Only if a layout switch was necessary, verify again that the text starts
    with 'ABC -' and that the numeric value changes after a short wait.
13. Terminate with status success after the ABC display has been identified and
    its dynamic value has been validated. If the test started directly in
    Layout_1, one successful validation in Layout_1 is sufficient. If the test
    started in Main, success requires validation before and after the switch to
    Layout_1.

Safety restrictions:
- Do not edit layouts, projects, signals, QPanel objects, application settings,
  or measurement configuration.
- Do not use the layout manager during the automated test.
- Do not click Data Recording STOP as part of this test unless required by a
  clear safety dialog. The common test cleanup closes ibaPDA after the workflow.
- If the project, Layout_1, the ABC display, or the needed Data Recording control
  cannot be identified clearly, terminate with status failure.
""".strip()


CASE = UiTestCase(
    case_id="TF-01",
    description=(
        "Validate the dynamic ABC signal display before and after a layout "
        "state check or Main-to-Layout_1 switch."
    ),
    task=TASK,
    additional_system_prompt=IBAPDA_TF_01_LAYOUT_CONTEXT,
    allowed_actions=frozenset(
        {
            "double_click",
            "left_click",
            "scroll",
            "wait",
            "checkpoint",
            "terminate",
        }
    ),
    max_iterations=24,
    max_task_duration=420,
    max_repeated_actions=2,
    max_consecutive_failures=2,
    max_executed_mouse_actions=14,
    verify_mouse_targets=True,
    iteration_delay=0.2,
    post_action_delay=1.0,
    model_options={
        "temperature": 0.1,
        "num_ctx": 12288,
        "num_predict": 384,
    },
)
