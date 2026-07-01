"""TF-03: Validate multilingual navigation in Client Preferences."""

from ui_contexts import IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT
from ui_tests.test_cases import UiTestCase


TASK = """
Perform test case TF-03, text-based identification and language validation in
proprietary ibaPDA UI structures.

Scope:
- Data Recording is not required for TF-03. Do not start or stop Data Recording.
- The loaded project/layout is irrelevant. TF-03 uses the Client Preferences
  dialog, which is available independently from the current project.
- The same Client Preferences navigation flow must be validated in German,
  English, and Chinese.
- The relevant dialog is opened with the client-preferences gear icon directly
  to the right of the Data Recording STOP button.

Initialization:
1. Open ibaPDA Client by double-clicking the visible Windows desktop shortcut
   named 'ibaPDA Client'. Do not use a single click for this step; a single
   click only selects the shortcut.
2. Wait until the ibaPDA main window and top menu bar are visible.
3. Determine the current UI language from visible menu/dialog text if possible.
4. If the current language is not German, change the language to German through
   the menu path View/Ansicht -> Language/Sprache -> German/Deutsch.
   Confirm only a clear language-change or restart prompt. Wait until ibaPDA is
   available again; if the application closed for the language change, reopen it
   with the desktop shortcut and wait for the main window.

Run 1 - German:
5. Open the Client Preferences dialog by clicking the small gear icon directly
   to the right of the Data Recording STOP button.
6. Identify the proprietary navigation tree on the left and the settings area
   on the right. The first/root node 'Allgemein' should normally be selected and
   highlighted in blue.
7. Select 'Allgemein'. Verify the selected text 'Allgemein' and verify that the
   right-side settings area for the general/client settings is visible.
8. Select 'Digitale Textanzeige'. Verify the selected text and verify that the
   corresponding settings area is visible.
9. Expand 'Kreisansicht' with a double-click if it is collapsed, then select its
   child node 'Ansicht'. Verify both the parent/child path
   'Kreisansicht -> Ansicht' and the corresponding settings area.
10. Record a checkpoint summarizing the German node selections and validation
    results.
11. Close the dialog with 'Abbrechen' without changing settings.

Run 2 - English:
12. Change the language to English through the menu path
    Ansicht/View -> Sprache/Language -> English. Confirm only a clear
    language-change or restart prompt. Wait until ibaPDA is available again; if
    the application closed, reopen it with the desktop shortcut.
13. Open the Client Preferences dialog again with the same gear icon.
14. Select 'General'. Verify the selected text and the associated settings area.
15. Select 'Text digital display'. Verify the selected text and the associated
    settings area.
16. Expand 'Circle View' with a double-click if it is collapsed, then select its
    child node 'Visuals'. Verify the path 'Circle View -> Visuals' and the
    associated settings area.
17. Record a checkpoint summarizing the English node selections and validation
    results.
18. Close the dialog with 'Cancel' without changing settings.

Run 3 - Chinese:
19. Change the language to Chinese through the menu path
    View/Ansicht -> Language/Sprache -> Chinese/Chinesisch, using the localized
    equivalent if the UI is already in English or Chinese. Confirm only a clear
    language-change or restart prompt. Wait until ibaPDA is available again; if
    the application closed, reopen it with the desktop shortcut.
20. Open the Client Preferences dialog again with the same gear icon.
21. Select the Chinese general node '概 览'. Verify the selected text and the
    associated settings area.
22. Select the Chinese text-display node '文本数 显'. Verify the selected text and
    the associated settings area.
23. Expand the Chinese circle-view node '圆视图' with a double-click if it is
    collapsed, then select its child node '显示'. Verify the path
    '圆视图 -> 显示' and the associated settings area.
24. Record a checkpoint summarizing the Chinese node selections and validation
    results.
25. Close the dialog with the localized cancel button without changing settings.

Completion:
26. Terminate with status success only after all three language runs have been
    completed, the required tree nodes were selected, their visible texts were
    validated, and the associated settings areas were observed.

Safety restrictions:
- Do not edit settings, change numeric values, toggle checkboxes, reset client
  settings, or change project/layout configuration.
- Do not use Data Recording GO or STOP for TF-03.
- Do not use answer for completion; terminate with status success or failure.
- If a required language, menu entry, Client Preferences dialog, tree node, or
  associated settings area cannot be identified clearly, terminate with status
  failure and explain which language/step failed.
""".strip()


CASE = UiTestCase(
    case_id="TF-03",
    description=(
        "Validate text-based navigation in the Client Preferences tree across "
        "German, English, and Chinese UI languages."
    ),
    task=TASK,
    additional_system_prompt=IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT,
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
    max_iterations=60,
    max_task_duration=900,
    max_repeated_actions=2,
    max_consecutive_failures=2,
    max_executed_mouse_actions=44,
    verify_mouse_targets=True,
    iteration_delay=0.2,
    post_action_delay=1.0,
    model_options={
        "temperature": 0.1,
        "num_ctx": 12288,
        "num_predict": 448,
    },
)
