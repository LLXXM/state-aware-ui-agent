"""TF-01: Layout switch during runtime."""

from ui_contexts import IBAPDA_UI_CONTEXT
from ui_tests.test_cases import UiTestCase




TASK = """
Execute the TF-01 sequence for switching layouts during runtime

1. Ensure the layout is loaded and visibleand the loading splash screen disappeared. 
2. Verify the project the loaded projekt exactly matches "test_layout_tabs". 
3. If not reload the project using the menu Datei -> Projekt öffnen.
4. Verify that data recording is active
5. If not active, start it using the Go button
6. Identify the digital text display in the currently loaded layout
7. Verify that the identified digital text display shows the ABC-Signal in the expected format and that the counter value is changing over time
8. If the "Main" layout is selected in the dropdown, switch to "Layout 1" by selecting it from the dropdown. Don't click on the layout tabs and don't switch to the "Main" layout if "Layout 1" is already loaded 
9. Identify the same digital text display again in the new loaded layout
10. Verify that the identified digital text display still shows the same ABC-Signal and that the counter value is still changing over time
""".strip()



CASE = UiTestCase(
    case_id="TF-01",
    description="Layout switch during runtime.",
    task=TASK,
    additional_system_prompt=IBAPDA_UI_CONTEXT,
    max_executed_mouse_actions=20,
)