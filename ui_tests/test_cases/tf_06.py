"""TF-06: Validate semantic consistency of dynamic UI states."""

from ui_tests.contexts.ibapda import IBAPDA_TF_06_SEMANTIC_STATE_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-06, semantic validation of dynamic UI states in ibaPDA.

Goal:
- Validate the loaded test_layout_multistatelabel scenario.
- Confirm semantic consistency between the trend curve signal state and the
  multistatelabel text/background color.
- Observe and checkpoint both semantic states at least once:
  positive: trend positive, label 'Wert > 0', green background;
  negative: trend negative, label 'Wert < 0', red background.
- Stop Data Recording before terminating successfully.

Initialization:
1. Open ibaPDA Client by double-clicking the visible Windows desktop shortcut
   named 'ibaPDA Client'. Do not use a single click for this step; a single
   click only selects the shortcut.
2. Wait until the ibaPDA main window is visible and the QPanel/display area is
   loaded.
3. Verify that the loaded project/layout is the TF-06 multistatelabel scenario.
4. Ensure Data Recording is active. If it is stopped, start it by clicking the
   center of the filled green GO button and wait until active recording is
   visible. If it is already running, do not click GO again.

Identify the relevant UI elements:
5. Identify the trend curve and the multistatelabel in the QPanel/display area.
6. Record a checkpoint confirming that both elements are visible in the same
   overall view.

Semantic validation:
7. Observe the current trend state, multistatelabel text, and multistatelabel
   background color from the same full-screen view.
8. Validate the positive state when visible: trend positive, label 'Wert > 0',
   green background.
9. Validate the negative state when visible: trend negative, label 'Wert < 0',
   red background.
10. If the trend is crossing near zero or the label state changes while being
    observed, wait briefly and repeat the observation instead of treating the
    transient frame as failure.
11. For each validated state, record a checkpoint that states the trend state,
    label text, label background color, and whether the consistency rule is
    satisfied.
12. Continue observing after short waits until both the positive and negative
    states have each been validated at least once.

Completion:
13. Terminate with status success only after both semantic states were observed
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
