"""TF-02: Validate dynamic labels under visibility and active-state changes."""

from ui_contexts import IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-02, robustness of UI element identification with dynamic
attributes and states in ibaPDA.

Project and signals under test:
- Project: test_layout_dynamic. The documentation may also refer to it as
  test_layout_dynamisch.
- The TF-02 project is expected to be loaded before this test starts. Do not
  open or switch projects during this test.
- The QPanel/display area contains four visually similar gray rectangular
  dynamic labels.
- Two labels display dynamic numeric DynVal values.
- Two labels display dynamic LabelText values beginning with 'FreeText'.
- Dynamic label text is visible only while Data Recording is active.
- The visibility controls for the second-row numeric label hide or show the
  entire gray label element, not only the text inside it.

Project setup:
1. Open ibaPDA Client by double-clicking the visible Windows desktop shortcut
   named 'ibaPDA Client'. Do not use a single click for this step; a single
   click only selects the shortcut.
2. Wait until the TF-02 QPanel/display area is visible, with the heading
   'label dynamic' and the visible/invisible/active/inactive controls.

Test steps:
3. Ensure Data Recording is active enough for the dynamic label text to update:
   - Observe whether green dynamic text is visible inside the gray labels.
   - If labels are empty and Data Recording is clearly stopped, start Data
     Recording using the shared GO instructions from the UI context.
   - Wait until dynamic text appears in the relevant labels.
4. Identify all four relevant gray rectangular dynamic labels and assign them:
   - first row numeric label on the left
   - first row text label to its right
   - second row numeric label beside the 'visible' and 'invisible' buttons
   - third row text label beside the 'active' and 'inactive' buttons
   If the second-row numeric label is not visible at the beginning or too few
   labels are visible, click 'visible' once before treating the label as
   missing.
5. Record a checkpoint with the four assigned label positions and their visible
   values.
6. Validate dynamic contents:
    - The two numeric labels show changing decimal DynVal values.
    - The two numeric labels show the same or clearly corresponding current
      signal value.
    - The two text labels show FreeText-based values with a changing suffix.
    - The two text labels follow the same LabelText update pattern.
7. Test visibility of the second-row numeric label:
    - Click the 'invisible' button beside the second-row numeric label.
    - Verify that the entire second-row numeric label is no longer visible,
      including its gray rectangular background and dynamic value text.
    - Record a checkpoint for the invisible state.
    - Click the 'visible' button.
    - Verify that the second-row numeric label is visible again and shows a
      valid dynamic numeric value.
8. Test interactivity of the third-row text label:
    - Click the 'inactive' button beside the third-row text label.
    - Right-click the third-row text label and verify that the expected context
      menu does not open.
    - Record a checkpoint for the inactive state.
    - Click the 'active' button.
    - Right-click the third-row text label and verify that a label-related
      context menu opens, for example containing 'Eigenschaften'.
    - Close the context menu without changing label properties by clicking an
      empty area of the QPanel/display area next to the labels.
9. Terminate with status success only after all four labels have been
    identified, dynamic contents have been validated, visibility switching has
    been verified, and active/inactive interactivity has been verified.

Safety restrictions:
- Do not edit projects, signals, label properties, QPanel objects, application
  settings, or measurement configuration.
- Do not open or switch projects during this test.
- Do not use answer for completion; terminate with status success or failure.
- Do not click Data Recording STOP as part of this test unless required by a
  clear safety dialog. The common test cleanup closes ibaPDA after the workflow.
- If the project, the four labels, the required buttons, or the expected state
  changes cannot be identified clearly, terminate with status failure.
""".strip()


CASE = UiTestCase(
    case_id="TF-02",
    description=(
        "Validate four similar dynamic labels and their visibility/active-state "
        "behavior in ibaPDA."
    ),
    task=TASK,
    additional_system_prompt=IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT,
    allowed_actions=frozenset(
        {
            "double_click",
            "left_click",
            "right_click",
            "scroll",
            "wait",
            "checkpoint",
            "terminate",
        }
    ),
    max_iterations=36,
    max_task_duration=600,
    max_repeated_actions=2,
    max_consecutive_failures=2,
    max_executed_mouse_actions=24,
    verify_mouse_targets=True,
    iteration_delay=0.2,
    post_action_delay=1.0,
    model_options={
        "temperature": 0.1,
        "num_ctx": 12288,
        "num_predict": 384,
    },
)
