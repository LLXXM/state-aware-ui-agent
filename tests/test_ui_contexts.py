import unittest

from ui_contexts import IBAPDA_UI_CONTEXT


class UiContextsTests(unittest.TestCase):
    def test_ibapda_context_distinguishes_recording_controls_and_states(self):
        self.assertIn("Ansichten starten", IBAPDA_UI_CONTEXT)
        self.assertIn("GO is directly to the left of STOP", IBAPDA_UI_CONTEXT)
        self.assertIn("labeled 'GO'", IBAPDA_UI_CONTEXT)
        self.assertIn("center of the red or gray circle", IBAPDA_UI_CONTEXT)
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
        self.assertIn("Do not click GO a second time", IBAPDA_UI_CONTEXT)
        self.assertIn("confirmation dialog", IBAPDA_UI_CONTEXT)


if __name__ == "__main__":
    unittest.main()
