"""TF-04: Navigate and validate a complex docked QPanel layout."""

from ui_contexts import IBAPDA_TF_04_COMPLEX_LAYOUT_CONTEXT
from ui_tests.test_cases import UiTestCase


PREPARE_TASK = """
Prepare ibaPDA for test case TF-04.

Preparation scope:
- Project: test_layout_komplex.
- This preparation is not part of the measured navigation run.
- The goal is only to open ibaPDA and ensure active Data Recording.

Preparation steps:
1. Open ibaPDA Client by double-clicking the visible Windows desktop shortcut
   named 'ibaPDA Client'. Do not use a single click for this step; a single
   click only selects the shortcut.
2. Wait until the ibaPDA main window and QPanel/display area are visible.
3. Verify that the loaded project/layout is the TF-04 complex layout scenario.
   The title bar or visible layout should refer to test_layout_komplex, or the
   QPanel should clearly show a complex docked tab/sub-tab layout.
4. Ensure the QPanel is in normal docked mode. Do not switch to fullscreen and
   do not undock panes.
5. Ensure Data Recording is active using only the GO/STOP button colors:
   active = GO gray and STOP red; stopped = GO green and STOP gray. If STOP is
   already red, recording is already active: do not click GO and finish
   preparation successfully. If recording is stopped, click the center of the
   filled green GO button once. If an 'Erfassung wird gestartet' dialog appears,
   wait until OK is enabled/clickable, click OK, then treat recording as active
   and do not verify or click GO again.
6. Do not wait for, validate, or checkpoint the full complex tab layout during
   preparation. Layout stabilization and tab navigation belong to the measured
   TF-04 task.
7. Terminate with status success when ibaPDA is open and Data Recording is
   active, or when the Data Recording start dialog has already been confirmed
   after a GO click.

Safety restrictions:
- Do not open or switch projects during this preparation.
- Do not enter design mode, move QPanel elements, configure views, edit signals,
  open property dialogs, or save project changes.
- Do not stop Data Recording during preparation.
- If STOP is red and GO is gray, Data Recording is already active; do not click
  any GO-like button in that state.
- When locating GO/STOP, prefer finding the red STOP button first. The real
  GO/STOP group has a green/black two-person icon left of GO, STOP right of GO,
  and the black/green client-preferences gear right of STOP.
- If a suspected GO button has a black-outlined, white-filled pause button with
  black pause bars to its right, it is the view Play button, not Data Recording
  GO.
- Do not use the bottom Datenaufzeichnungsstatus/Data Recording status pane to
  verify recording state.
- Do not click, select, expand, or otherwise interact with the bottom
  Datenaufzeichnungsstatus/Data Recording status pane during preparation.
- Do not repeatedly re-check the Data Recording status after a confirmed
  Data Recording start dialog. Treat that confirmed dialog as sufficient and
  move on.
""".strip()


TASK = """
Perform one measured TF-04 navigation run through the complex ibaPDA QPanel tab
layout.

Goal:
- Visit the expected 7 primary tabs and 53 secondary tabs exactly once, using
  the TF-04 layout context for tab names, counts, and drag-bar handling.
- Use only the canonical primary/secondary tab names listed in the TF-04 layout
  context. A secondary tab is valid only when its full readable label matches
  one expected checklist entry for the current primary tab.
- Validate the QPanel/display-area content after every secondary-tab selection.
- Record secondary-tab checkpoints and primary-tab summary checkpoints that
  prove the visited tab names and visible content.

Measured run rules:
- ibaPDA is already open, Data Recording is active, and preparation is complete.
- Start by resetting to primary tab 'Start' and secondary tab 'Start'. If those
  tabs are hidden by a previous run's drag position, use the drag-bar rules from
  the TF-04 context to reveal them first.
- Mandatory rule before every secondary-tab click:
  1. Look at the current screenshot and read the exact full target secondary-tab
     label on the screen.
  2. If the full label is not completely visible and readable on the current
     screenshot, use the horizontal drag-bar first. Do not click the tab.
  3. Click the target secondary tab only after the full exact canonical label is
     completely visible and readable on the current screenshot.
- A clipped or abbreviated label such as 'Sig...', 'Trend...', or any visible
  prefix with ellipses is not a readable tab name. Never assume what it means.
  Never treat it as Signalbaum, Trend kurve, Überwachungs ansicht, or any other
  canonical tab until the complete label is visible on the screenshot.
- Confidence gate: continue with a tab click or tab checkpoint only when you
  have 100% visual evidence from the current screenshot that the complete
  canonical tab label is visible/readable. If the label is clipped, hidden,
  partially readable, inferred from position/history, or only expected to be
  nearby, do not click or checkpoint. First make the tab fully visible/readable,
  verify again, or terminate with failure if it cannot be made unambiguous.
- Before clicking primary tab 'Start', verify that its full label is readable
  in the primary-tab row. If the row is shifted so the first readable primary
  tab is not 'Start', drag the horizontal drag-bar left until 'Start' is fully
  visible. Do not click guessed coordinates for hidden tabs.
- Traverse primary tabs left to right. After selecting any primary tab, click
  its first visible secondary tab before continuing through the rest.
- Do not skip 'Spielwiese' under the Start primary tab.
- Maintain an explicit checklist/count of fully read and visited secondary-tab
  names. Never use ordinal, guessed, inferred, or truncated tab names in
  checkpoints.
- Only claim tab names/counts that are readable in the current screenshot. If
  the tab row is blank, hidden, clipped, or unreadable, state that and recover
  with the drag-bar instead of inferring visible tabs from memory.
- Never create a secondary-tab checkpoint with a tab name that is not in the
  canonical checklist for the current primary tab.
- A tab click is only an attempted action. Before checkpointing or moving on,
  verify in the current screenshot that the intended canonical tab label is
  fully readable and visibly selected/active. Execution history, previous
  intent, checklist order, and QPanel content alone are not evidence that the
  tab switch succeeded.
- If a required secondary-tab checkpoint is missing, record it before any
  further navigation.
- Do not click nested/tertiary tabs inside QPanel content. They are not part of
  TF-04.
- Do not open or switch projects, enter design mode, move QPanel elements,
  configure views, edit signals, open property dialogs, save project changes,
  stop Data Recording, switch fullscreen mode, or use answer.

Procedure:
1. Record a starting checkpoint describing only what is actually readable in
   the current screenshot: current primary tab, current secondary tab, visible
   tab labels, and QPanel/display-area content. Do not infer hidden tab names.
2. Reset navigation to the leftmost start point. First verify whether the full
   primary-tab label 'Start' is currently readable in the primary-tab row.
   If 'Start' is not fully readable, do not click any expected Start
   coordinate. Use the horizontal drag-bar to reveal the left side until
   'Start' is fully readable.
3. Click primary tab 'Start' only after its full label is visible/readable.
   Then verify from the next screenshot that 'Start' is visibly active.
4. Verify whether secondary tab 'Start' is fully readable in the secondary-tab
   row. Click it only if its full label is visible/readable; otherwise use the
   drag-bar to reveal it first.
5. Validate 'Start'/'Start' from the current screenshot and record its
   secondary-tab checkpoint.
6. Select 'Spielwiese' under the Start primary tab only after the full
   'Spielwiese' label is visible/readable. Validate its QPanel content and
   record its secondary-tab checkpoint.
7. Traverse each remaining primary tab from left to right in this order:
   Demos, Allgemeine Funktionen, Anzeige Elemente, Eingabe Elemente, Ansichten,
   Gestaltung/Layout/Web. For each primary tab, complete all substeps below
   before moving to the next primary tab:
   a. Make the primary-tab label fully visible/readable. If it is hidden or
      clipped, reveal it with the horizontal drag-bar first. Do not click
      guessed coordinates.
   b. Click the primary tab only after its full canonical label is readable.
      Verify from the next screenshot that this primary tab is visibly active.
   c. Using the canonical checklist for this primary tab, visit its secondary
      tabs from left to right. For each secondary tab, repeat this exact
      sequence without skipping any step:
      c1. Look at the current screenshot and try to read the full target
          secondary-tab label.
      c2. If the full exact label is not completely visible and readable, use
          the horizontal drag-bar. Do not click the tab and do not checkpoint.
      c3. After dragging, inspect the new screenshot again. Repeat c2 until the
          full exact label is completely visible/readable, or terminate with
          failure if it cannot be made readable.
      c4. Click the secondary tab only after the full exact canonical label is
          completely visible/readable in the screenshot.
      c5. Verify from the next screenshot that the same full canonical
          secondary-tab label is visibly selected/active.
      c6. Validate the QPanel content and record that secondary-tab checkpoint
          only after c5 is satisfied.
   d. After all expected secondary tabs for this primary tab have verified
      checkpoints, record one primary-tab summary checkpoint listing the
      secondary tabs successfully visited under that primary tab.
8. Record a final checkpoint summarizing the visited counts, drag-bar
   interactions, any ambiguous validation, and whether all 7 primary tabs and
   all 53 secondary tabs were visited.
9. Terminate with status success only if all 7 primary tabs and all 53
   secondary tabs were visited and each secondary-tab visit has a
   content-validation checkpoint. Otherwise terminate with status failure and
   explain the missing primary tab, secondary tab, drag-bar state, or content
   validation.
""".strip()


CASE = UiTestCase(
    case_id="TF-04",
    description=(
        "Navigate nested primary and secondary tabs in the complex docked "
        "ibaPDA QPanel layout and validate stability across repeated runs."
    ),
    task=TASK,
    prepare_task=PREPARE_TASK,
    measurement_repetitions=1,
    additional_system_prompt=IBAPDA_TF_04_COMPLEX_LAYOUT_CONTEXT,
    allowed_actions=frozenset(
        {
            "double_click",
            "left_click",
            "mouse_move",
            "left_click_drag",
            "wait",
            "checkpoint",
            "terminate",
        }
    ),
    max_iterations=160,
    max_task_duration=2400,
    max_repeated_actions=2,
    max_consecutive_failures=2,
    max_executed_mouse_actions=120,
    verify_mouse_targets=False,
    abort_on_mouse_verification_failure=False,
    minimize_windows_before=True,
    minimize_vscode_before=False,
    cleanup_ibapda_before=True,
    iteration_delay=0.2,
    post_action_delay=0.8,
    model_options={
        "temperature": 0.0,
        "num_ctx": 12288,
        "num_predict": 512,
    },
)
