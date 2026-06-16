import unittest

from ui_contexts import IBAPDA_UI_CONTEXT


class UiContextsTests(unittest.TestCase):
    def test_ibapda_context_distinguishes_recording_controls_and_states(self):
        self.assertIn("Ansichten starten", IBAPDA_UI_CONTEXT)
        self.assertIn("GO is directly to the left of STOP", IBAPDA_UI_CONTEXT)
        self.assertIn("labeled 'GO'", IBAPDA_UI_CONTEXT)
        self.assertIn("two-person icon", IBAPDA_UI_CONTEXT)
        self.assertIn("triangle/play symbol", IBAPDA_UI_CONTEXT)
        self.assertIn("Never", IBAPDA_UI_CONTEXT)
        self.assertIn("GO is gray", IBAPDA_UI_CONTEXT)
        self.assertIn("STOP is red", IBAPDA_UI_CONTEXT)
        self.assertIn("Datenaufzeichnungsstatus", IBAPDA_UI_CONTEXT)
        self.assertIn("No 'Data Store' entry", IBAPDA_UI_CONTEXT)
        self.assertIn("small green circular indicator", IBAPDA_UI_CONTEXT)
        self.assertIn("system or computer name", IBAPDA_UI_CONTEXT)
        self.assertIn("Erfassung wird gestartet", IBAPDA_UI_CONTEXT)
        self.assertIn("Do not click GO a second time", IBAPDA_UI_CONTEXT)
        self.assertIn("confirmation dialog", IBAPDA_UI_CONTEXT)
        self.assertIn("Required state check", IBAPDA_UI_CONTEXT)
        self.assertIn("If the state is active", IBAPDA_UI_CONTEXT)
        self.assertIn("Never describe that state as stopped", IBAPDA_UI_CONTEXT)
        self.assertIn("can be collapsed", IBAPDA_UI_CONTEXT)
        self.assertIn("bottom tab bar", IBAPDA_UI_CONTEXT)
        self.assertIn("it does not mean the pane is open", IBAPDA_UI_CONTEXT)
        self.assertIn("no status content rows", IBAPDA_UI_CONTEXT)
        self.assertIn("ibaPDA-Ereignisprotokoll", IBAPDA_UI_CONTEXT)
        self.assertIn("status_pane_collapsed", IBAPDA_UI_CONTEXT)
        self.assertNotIn("Data Recording pane", IBAPDA_UI_CONTEXT)
        self.assertNotIn("Data Recording status pane", IBAPDA_UI_CONTEXT)


if __name__ == "__main__":
    unittest.main()
