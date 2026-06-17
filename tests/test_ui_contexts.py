import unittest

from ui_contexts import (
    IBAPDA_BASE_CONTEXT,
    IBAPDA_TF_01_LAYOUT_CONTEXT,
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


if __name__ == "__main__":
    unittest.main()
