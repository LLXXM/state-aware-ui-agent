"""TF-06: Validate semantic consistency of dynamic UI states."""

from ui_contexts import IBAPDA_TF_06_SEMANTIC_STATE_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-06, semantic validation of dynamic UI states in ibaPDA.

Project and visualization under test:
- Project: test_layout_multistatelabel.
- The QPanel/display area contains a trend curve and a multistatelabel.
- Both elements are driven by the same triangle signal with a value range from
  -100 to 100.
- The test verifies consistency between signal state, label text, and label
  background color.

Initialization:
1. Open ibaPDA Client by double-clicking the visible Windows desktop shortcut
   named 'ibaPDA Client'. Do not use a single click for this step; a single
   click only selects the shortcut.
2. Wait until the ibaPDA main window is visible and the QPanel/display area is
   loaded.
3. Verify that the loaded project/layout is the TF-06 multistatelabel scenario.
   The title bar or visible layout should refer to test_layout_multistatelabel,
   or the QPanel should clearly show the TF-06 trend curve and multistatelabel.
4. Ensure Data Recording is active. If it is stopped, start it by clicking the
   center of the filled green GO button and wait until active recording is
   visible. If it is already running, do not click GO again.

Identify the relevant UI elements:
5. Identify the trend curve in the QPanel/display area. It is the large black
   chart with grid lines, a blue triangle-like signal trace, time labels, and
   a right-side y-axis with values around -100 to 100.
6. Identify the multistatelabel below the trend curve. It is a rectangular
   label whose background changes color and whose text changes between
   'Wert > 0' and 'Wert < 0'.
7. Record a checkpoint confirming that both elements are visible in the same
   overall view.

Semantic validation:
8. Observe the current trend state, the current multistatelabel text, and the
   current multistatelabel background color from the same full-screen view.
9. If the trend state is positive, verify that the label shows 'Wert > 0' and
   has a green background.
10. If the trend state is negative, verify that the label shows 'Wert < 0' and
    has a red background.
11. If the trend is crossing near zero or the label state changes while being
    observed, wait briefly and repeat the observation instead of treating the
    transient frame as failure.
12. For a validated positive state, record a checkpoint that states the trend
    is positive, the label text is 'Wert > 0', the background is green, and the
    consistency rule is satisfied.
13. For a validated negative state, record a checkpoint that states the trend
    is negative, the label text is 'Wert < 0', the background is red, and the
    consistency rule is satisfied.
14. Continue observing after short waits until both the positive and negative
    states have each been validated at least once.

Completion:
15. Stop Data Recording with the filled STOP button if Data Recording is still
    active, and verify that recording is stopped.
16. Terminate with status success only after both semantic states were observed
    and validated consistently, and Data Recording has been stopped.

Safety restrictions:
- Do not open or switch projects during TF-06.
- Do not enter design mode, move elements, configure elements, open property
  dialogs, edit signals, or save project changes.
- Do not use answer for completion; terminate with status success or failure.
- If the trend curve, multistatelabel, Data Recording controls, positive state,
  or negative state cannot be identified clearly, terminate with status failure
  and explain what could not be validated.
""".strip()


CASE = UiTestCase(
    case_id="TF-06",
    description=(
        "Validate semantic consistency between trend curve signal state and "
        "multistatelabel text/color state."
    ),
    task=TASK,
    additional_system_prompt=IBAPDA_TF_06_SEMANTIC_STATE_CONTEXT,
    allowed_actions=frozenset(
        {
            "double_click",
            "left_click",
            "wait",
            "checkpoint",
            "terminate",
        }
    ),
    max_iterations=50,
    max_task_duration=900,
    max_repeated_actions=3,
    max_consecutive_failures=2,
    max_executed_mouse_actions=12,
    verify_mouse_targets=True,
    abort_on_mouse_verification_failure=False,
    iteration_delay=0.2,
    post_action_delay=1.0,
    model_options={
        "temperature": 0.1,
        "num_ctx": 8192,
        "num_predict": 384,
    },
)
