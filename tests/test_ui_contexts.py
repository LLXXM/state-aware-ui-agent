import unittest

from ui_contexts import (
    IBAPDA_BASE_CONTEXT,
    IBAPDA_PROJECT_OPEN_CONTEXT,
    IBAPDA_TF_01_LAYOUT_CONTEXT,
    IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT,
    IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT,
    IBAPDA_UI_CONTEXT,
)


class UiContextsTests(unittest.TestCase):
    def test_base_context_describes_qpanel_display_area(self):
        self.assertIn("QPanel/display area", IBAPDA_BASE_CONTEXT)
        self.assertIn("double-clicking the 'ibaPDA Client' desktop shortcut", IBAPDA_BASE_CONTEXT)
        self.assertIn("single left click only selects", IBAPDA_BASE_CONTEXT)
        self.assertIn("central black workspace", IBAPDA_BASE_CONTEXT)
        self.assertIn("digital text displays", IBAPDA_BASE_CONTEXT)
        self.assertIn("trend curves", IBAPDA_BASE_CONTEXT)
        self.assertIn("embedded layouts", IBAPDA_BASE_CONTEXT)
        self.assertIn("Tooltips", IBAPDA_BASE_CONTEXT)
        self.assertIn("small white rectangle", IBAPDA_BASE_CONTEXT)
        self.assertIn("wrong element", IBAPDA_BASE_CONTEXT)
        self.assertIn("Do not click the tooltip itself", IBAPDA_BASE_CONTEXT)

    def test_ibapda_context_distinguishes_recording_controls_and_states(self):
        self.assertIn("Ansichten starten", IBAPDA_UI_CONTEXT)
        self.assertIn("GO is directly to the left of STOP", IBAPDA_UI_CONTEXT)
        self.assertIn("labeled 'GO'", IBAPDA_UI_CONTEXT)
        self.assertIn("center of the red circle", IBAPDA_UI_CONTEXT)
        self.assertIn("client preferences controls", IBAPDA_UI_CONTEXT)
        self.assertIn("two-person icon", IBAPDA_UI_CONTEXT)
        self.assertIn("triangle/play symbol", IBAPDA_UI_CONTEXT)
        self.assertIn("Never", IBAPDA_UI_CONTEXT)
        self.assertIn("GO is gray", IBAPDA_UI_CONTEXT)
        self.assertIn("STOP is red", IBAPDA_UI_CONTEXT)
        self.assertIn("already be stopped", IBAPDA_UI_CONTEXT)
        self.assertIn("already running", IBAPDA_UI_CONTEXT)
        self.assertIn("unavailable", IBAPDA_UI_CONTEXT)
        self.assertIn("both GO and STOP can be gray", IBAPDA_UI_CONTEXT)
        self.assertIn("no", IBAPDA_UI_CONTEXT)
        self.assertIn("project/layout is loaded", IBAPDA_UI_CONTEXT)
        self.assertIn("do not click GO", IBAPDA_UI_CONTEXT)
        self.assertIn("Datenaufzeichnungsstatus", IBAPDA_UI_CONTEXT)
        self.assertIn("No 'Data Store' entry", IBAPDA_UI_CONTEXT)
        self.assertIn("small green circular indicator", IBAPDA_UI_CONTEXT)
        self.assertIn("system or computer name", IBAPDA_UI_CONTEXT)
        self.assertIn("Erfassung wird gestartet", IBAPDA_UI_CONTEXT)
        self.assertIn("close by itself after a few seconds", IBAPDA_UI_CONTEXT)
        self.assertIn("continue the test without clicking GO again", IBAPDA_UI_CONTEXT)
        self.assertIn("Do not click GO a second time", IBAPDA_UI_CONTEXT)
        self.assertIn("confirmation dialog", IBAPDA_UI_CONTEXT)

    def test_tf_01_context_describes_layout_and_abc_signal_validation(self):
        self.assertIn("test_layout_tabs", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("Layout_1", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("ABC-Signal", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("ABC -", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("numeric value changes", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("empty or black", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("Do not open the layout manager", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("right of the\n  gear/client-preferences icon", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("closed layout selection", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("Do not open the dropdown just to determine", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("only when a layout change is required", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("proprietary navigation/tree", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("Do not confuse", IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("QPanel/display area", IBAPDA_TF_01_LAYOUT_CONTEXT)

    def test_tf_02_context_describes_dynamic_labels_and_state_controls(self):
        self.assertIn("test_layout_dynamic", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("test_layout_dynamisch", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("FreeText", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("visible", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("invisible", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("active", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("inactive", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("expected to be loaded before the test starts", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("Do not open\n  another project during TF-02", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertNotIn("Initialwerte laden", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("right-click", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("entire second-row numeric label element", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("can already be\n  invisible at the beginning", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("click 'visible' once", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("clicking an empty area of the QPanel/display area", IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)

    def test_tf_03_context_describes_client_preferences_language_tree(self):
        context = IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT

        self.assertIn("Client Preferences dialog", context)
        self.assertIn("right of the Data Recording STOP", context)
        self.assertIn("Data Recording is not required", context)
        self.assertIn("proprietary navigation tree", context)
        self.assertIn("highlighted in blue", context)
        self.assertIn("small plus symbol", context)
        self.assertIn("double-clicking the node name", context)
        self.assertIn("Allgemein", context)
        self.assertIn("Digitale Textanzeige", context)
        self.assertIn("Kreisansicht -> Ansicht", context)
        self.assertIn("General", context)
        self.assertIn("Text digital display", context)
        self.assertIn("Circle View -> Visuals", context)
        self.assertIn("概 览", context)
        self.assertIn("文本数 显", context)
        self.assertIn("圆视图 -> 显示", context)
        self.assertIn("semantically", context)
        self.assertIn("Do not edit settings", context)

    def test_project_open_context_is_available_for_later_tests(self):
        self.assertIn("Datei -> Projekt öffnen", IBAPDA_PROJECT_OPEN_CONTEXT)
        self.assertIn("Öffnen", IBAPDA_PROJECT_OPEN_CONTEXT)
        self.assertIn("Initialwerte laden", IBAPDA_PROJECT_OPEN_CONTEXT)
        self.assertIn("Yes", IBAPDA_PROJECT_OPEN_CONTEXT)


if __name__ == "__main__":
    unittest.main()
