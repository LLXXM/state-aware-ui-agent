"""TF-00: Safely start and stop ibaPDA Data Recording."""

from ui_tests.contexts.ibapda import IBAPDA_UI_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-00, the controlled ibaPDA Data Recording cycle:
1. All previously open windows have already been minimized and the desktop should be visible.
2. Open the ibaPDA Client application by double-clicking its visible desktop icon.
3. Wait until the ibaPDA Client main window is fully visible.
4. Click the filled green Data Recording button labeled 'GO' in white text.
   It is directly left of the filled gray button labeled 'STOP', between a
   two-person icon and gear icons. Do not click the separate green outlined
   'Ansichten starten' triangle/play button elsewhere in the toolbar.
5. If a dialog clearly asks to confirm starting Data Recording, confirm it.
6. Confirm that Data Recording has started: GO becomes gray, STOP becomes red,
   and/or a 'Data Store' entry with a small green circular indicator appears in
   'Datenaufzeichnungsstatus'.
7. Click the center of the now-red filled Data Recording STOP button directly
   to the right of GO. The click target must be inside the red circle containing
   the white 'STOP' text, not on the gear/client preferences controls to its
   right.
8. If a dialog clearly asks to confirm stopping Data Recording, confirm it.
9. Terminate with status success only after the UI visibly confirms Data
   Recording is stopped again: GO is green, STOP is gray, and/or
   the 'Data Store' entry has disappeared from 'Datenaufzeichnungsstatus'.

Safety restrictions:
- Do not modify configuration, files, signals, views, or measurement settings.
- Do not interact with any content control other than the explicitly required
  Data Recording GO/STOP controls and their unambiguous confirmation dialogs.
- After GO has produced an 'Erfassung wird gestartet' window or a 'Data Store'
  entry with a green indicator has appeared, never click GO again during this
  test case. Treat it as started or starting and proceed toward verified STOP.
- Do not leave Data Recording running when terminating.
- If GO, STOP, a confirmation dialog, or the stopped state cannot be
  identified clearly, terminate with status failure.
""".strip()


CASE = UiTestCase(
    case_id="TF-00",
    description="Start and stop ibaPDA Data Recording and leave the client closed.",
    task=TASK,
    additional_system_prompt=IBAPDA_UI_CONTEXT,
    allowed_actions=frozenset(
        {"double_click", "left_click", "wait", "checkpoint", "terminate"}
    ),
    max_executed_mouse_actions=10,

    verify_mouse_targets=True,     # True
    iteration_delay=0.1,            # 0.5
    post_action_delay=1.0,          # 1.0  
    model_options={
        "temperature": 0.1,
        "num_ctx": 8192,          # 32768,
        "num_predict": 256,       #512, 
    }
)
