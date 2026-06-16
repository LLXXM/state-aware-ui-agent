"""TF-00: Safely start and stop ibaPDA Data Recording."""

from ui_contexts import IBAPDA_UI_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-00, the controlled ibaPDA Data Recording cycle:
1. All previously open windows have already been minimized and the desktop should be visible.
2. Open the ibaPDA Client application by double-clicking its visible desktop icon.
3. Wait until the ibaPDA Client main window is fully visible.
4. Use the ibaPDA UI context to inspect the Data Recording state before every
   Data Recording action. Open the 'Datenaufzeichnungsstatus' tab/pane if only
   its bottom tab is visible.
5. Complete the start phase once: if Data Recording is already active or
   starting, the start phase is done. If it is stopped, click GO once and handle
   only a clear Data Recording start dialog if one appears. After this step,
   do not click GO again during this test case.
6. Once the start phase is done, move only toward STOP: stop Data Recording and
   handle only a clear Data Recording stop dialog if one appears.
7. Terminate with status success only after the UI visibly confirms Data
   Recording is stopped again.

Safety restrictions:
- Do not modify configuration, files, signals, views, or measurement settings.
- Do not interact with any content control other than the explicitly required
  Data Recording controls, the 'Datenaufzeichnungsstatus' tab, and unambiguous
  Data Recording confirmation dialogs.
- Do not leave Data Recording running when terminating.
- If GO, STOP, a confirmation dialog, or the stopped state cannot be
  identified clearly, terminate with status failure.
""".strip()



CASE = UiTestCase(
    case_id="TF-00",
    description="Start and stop ibaPDA Data Recording and leave the client closed.",
    task=TASK,
    additional_system_prompt=IBAPDA_UI_CONTEXT,
)
