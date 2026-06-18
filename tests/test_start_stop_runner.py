import unittest
from unittest.mock import Mock, patch

from ui_contexts import IBAPDA_UI_CONTEXT
from ui_contexts import IBAPDA_TF_01_LAYOUT_CONTEXT
from ui_contexts import IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT
from ui_contexts import IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT
from ui_contexts import IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT
from ui_tests.run_test_case import default_report_dir_for_case, load_test_case, run_test_case
from ui_tests.test_cases import UiTestCase


class TestCaseDefinitionTests(unittest.TestCase):
    def test_tf_00_defines_recording_cycle_configuration(self):
        case = load_test_case("TF-00")

        self.assertEqual(case.case_id, "TF-00")
        self.assertEqual(case.additional_system_prompt, IBAPDA_UI_CONTEXT)
        self.assertGreaterEqual(case.max_executed_mouse_actions, 5)
        self.assertIn("Data Recording STOP", case.task)
        self.assertIn("center of the now-red filled Data Recording STOP", case.task)

    def test_tf_01_defines_layout_hierarchy_configuration(self):
        case = load_test_case("TF-01")

        self.assertEqual(case.case_id, "TF-01")
        self.assertEqual(case.additional_system_prompt, IBAPDA_TF_01_LAYOUT_CONTEXT)
        self.assertIn("test_layout_tabs", case.task)
        self.assertIn("double-clicking the visible Windows desktop shortcut", case.task)
        self.assertIn("Do not use a single click", case.task)
        self.assertIn("click only selects the shortcut", case.task)
        self.assertIn("Layout_1", case.task)
        self.assertIn("ABC - <number>", case.task)
        self.assertIn("layout manager", case.task)
        self.assertIn("Only if a layout switch was necessary", case.task)
        self.assertIn("one successful validation in Layout_1 is sufficient", case.task)
        self.assertIn("checkpoint", case.allowed_actions)
        self.assertIn("scroll", case.allowed_actions)

    def test_tf_02_defines_dynamic_label_configuration(self):
        case = load_test_case("TF-02")

        self.assertEqual(case.case_id, "TF-02")
        self.assertEqual(case.additional_system_prompt, IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT)
        self.assertIn("test_layout_dynamic", case.task)
        self.assertIn("expected to be loaded before this test starts", case.task)
        self.assertIn("Do not open or switch projects", case.task)
        self.assertNotIn("Datei -> Projekt öffnen", case.task)
        self.assertNotIn("Initialwerte laden", case.task)
        self.assertIn("FreeText", case.task)
        self.assertIn("visible", case.task)
        self.assertIn("invisible", case.task)
        self.assertIn("entire gray label element", case.task)
        self.assertIn("click 'visible' once", case.task)
        self.assertIn("empty area of the QPanel/display area", case.task)
        self.assertIn("active", case.task)
        self.assertIn("inactive", case.task)
        self.assertIn("right_click", case.allowed_actions)
        self.assertIn("terminate", case.allowed_actions)
        self.assertNotIn("answer", case.allowed_actions)

    def test_tf_03_defines_client_preferences_language_configuration(self):
        case = load_test_case("TF-03")

        self.assertEqual(case.case_id, "TF-03")
        self.assertEqual(
            case.additional_system_prompt,
            IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT,
        )
        self.assertIn("Data Recording is not required", case.task)
        self.assertIn("Client Preferences", case.task)
        self.assertIn("gear icon directly", case.task)
        self.assertIn("Allgemein", case.task)
        self.assertIn("Digitale Textanzeige", case.task)
        self.assertIn("Kreisansicht -> Ansicht", case.task)
        self.assertIn("General", case.task)
        self.assertIn("Text digital display", case.task)
        self.assertIn("Circle View -> Visuals", case.task)
        self.assertIn("概 览", case.task)
        self.assertIn("文本数 显", case.task)
        self.assertIn("圆视图 -> 显示", case.task)
        self.assertIn("double_click", case.allowed_actions)
        self.assertIn("checkpoint", case.allowed_actions)
        self.assertIn("terminate", case.allowed_actions)
        self.assertNotIn("answer", case.allowed_actions)
        self.assertGreaterEqual(case.max_iterations, 50)

    def test_tf_05_defines_design_configuration_workflow(self):
        case = load_test_case("TF-05")

        self.assertEqual(case.case_id, "TF-05")
        self.assertEqual(
            case.additional_system_prompt,
            IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT,
        )
        self.assertIn("test_layout_textanzeige", case.task)
        self.assertIn("QPanel/display area must be empty", case.task)
        self.assertIn("Projekt öffnen", case.task)
        self.assertIn("Initialwerte laden", case.task)
        self.assertIn("Entwurfsmodus", case.task)
        self.assertIn("right-clicking an empty area", case.task)
        self.assertIn("context-menu entry\n   'Entwurfsmodus'", case.task)
        self.assertIn("second icon from the left", case.task)
        self.assertIn("becomes light-blue", case.task)
        self.assertIn("Use mouse_move to hover", case.task)
        self.assertIn("fourth\n   icon from the left", case.task)
        self.assertIn("book icon", case.task)
        self.assertIn("Bibliothek", case.task)
        self.assertIn("wrong pane for TF-05", case.task)
        self.assertIn("Digitale Ziffernanzeige", case.task)
        self.assertIn("Digitale Textanzeige", case.task)
        self.assertIn("Trendkurve", case.task)
        self.assertIn("Target the vertical center of the visible tool text/row", case.task)
        self.assertIn("marker center must be in the\n    vertical middle", case.task)
        self.assertIn("not on the upper edge of the row", case.task)
        self.assertIn("becomes blue highlighted before dragging", case.task)
        self.assertIn("upper-left part of\n    the empty QPanel", case.task)
        self.assertIn("directly to the right of the digital numeric display", case.task)
        self.assertIn("wider free area below the two\n    displays", case.task)
        self.assertIn("If any\n    elements overlap", case.task)
        self.assertIn("final non-overlapping positions", case.task)
        self.assertIn("yellow seven-segment\n    placeholder digits", case.task)
        self.assertIn("gray-framed horizontal rectangle", case.task)
        self.assertIn("larger black plotting area", case.task)
        self.assertIn("Use this method strictly for the numeric display", case.task)
        self.assertIn("do not use a\n    right-click context menu", case.task)
        self.assertIn("try the same double-click once more", case.task)
        self.assertIn("Use\n    this method strictly for the text display", case.task)
        self.assertIn("do not double-click it", case.task)
        self.assertIn("clicking vertically centered inside\n    the visible text area", case.task)
        self.assertIn("Do not assume it opened", case.task)
        self.assertIn("dropdown tree is actually\n    visible", case.task)
        self.assertIn("GenerateSignal(0,100,10,10)", case.task)
        self.assertIn("GenerateText(\"ABC_%1\")", case.task)
        self.assertIn("Prefer expanding 'ibaPDA' and 'Virtuell'", case.task)
        self.assertIn("Plus symbols are indented by tree\n    level", case.task)
        self.assertIn("not all in one vertical column", case.task)
        self.assertIn("exact readable text is\n    visible in the tree", case.task)
        self.assertIn("pointer shifted vertically by no more than 5", case.task)
        self.assertIn("Do not use a normal\n    single click on the node text", case.task)
        self.assertIn("indented child nodes appear underneath", case.task)
        self.assertIn("Exit design mode. This is mandatory", case.task)
        self.assertIn("right-click an empty area of the central\n    QPanel/display area", case.task)
        self.assertIn("context-menu entry 'Entwurfsmodus'\n    again", case.task)
        self.assertIn("design toolbar is no longer visible", case.task)
        self.assertIn("Signalbaum/signal tree", case.task)
        self.assertIn("node 'Virtuell'", case.task)
        self.assertIn("preferably double-click precisely", case.task)
        self.assertIn("do not click beside the parent\n    plus column", case.task)
        self.assertIn("double-click on the 'Virtuell' node text instead", case.task)
        self.assertIn("leftmost\n    expand/collapse control", case.task)
        self.assertIn("small signal/type\n    icon", case.task)
        self.assertIn("Do not click in the gap", case.task)
        self.assertIn("indented signal entries are visible underneath", case.task)
        self.assertIn("exact readable text\n    is visible under 'Virtuell'", case.task)
        self.assertIn("gray pane title/header bar labeled 'ibaPDA-Signalbaum'", case.task)
        self.assertIn("undocked/floating", case.task)
        self.assertIn("docked on the left\n    again", case.task)
        self.assertIn("vertical center of the GenerateSignal node text/row", case.task)
        self.assertIn("dragging GenerateSignal(0,100,10,10) from the\n    signal tree onto the trend curve", case.task)
        self.assertIn("Signalbaum/signal tree\n    is only the drag source", case.task)
        self.assertIn("inside\n    the trend curve element in the QPanel", case.task)
        self.assertIn("wrong drag end", case.task)
        self.assertIn("not on the\n    row's upper edge or on the Signalbaum pane title", case.task)
        self.assertIn("property dialog or signal dropdown", case.task)
        self.assertIn("absolute normalized screen coordinate", case.task)
        self.assertIn("Do not treat the drag coordinate as a relative movement", case.task)
        self.assertIn("mouse_move", case.allowed_actions)
        self.assertIn("left_click_drag", case.allowed_actions)
        self.assertIn("right_click", case.allowed_actions)
        self.assertIn("terminate", case.allowed_actions)
        self.assertNotIn("answer", case.allowed_actions)
        self.assertTrue(case.verify_mouse_targets)
        self.assertFalse(case.abort_on_mouse_verification_failure)
        self.assertGreaterEqual(case.max_iterations, 80)


class TestCaseRunnerTests(unittest.TestCase):
    @patch("ui_tests.run_test_case.print")
    @patch("ui_tests.run_test_case.restore_minimized_windows_after_test")
    @patch("ui_tests.run_test_case.minimize_all_windows_for_test")
    @patch("ui_tests.run_test_case.SeeThinkActAgent")
    @patch(
        "ui_tests.run_test_case.ensure_ibapda_closed",
        side_effect=[
            {"success": True, "status": "already_closed"},
            {"success": True, "status": "success", "window_closed": True},
        ],
    )
    def test_runs_tf_00_between_pre_and_post_cleanup(
        self, ensure_closed, agent_class, minimize, restore, _output
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "success"}
        agent_class.return_value = agent

        result = run_test_case(load_test_case("TF-00"))

        self.assertEqual(ensure_closed.call_count, 2)
        self.assertEqual(
            ensure_closed.call_args_list[0].kwargs,
            {"screenshot_dir": "artifacts/ui_tests/tf_00/pre_cleanup"},
        )
        self.assertEqual(
            ensure_closed.call_args_list[1].kwargs,
            {
                "screenshot_dir": "artifacts/ui_tests/tf_00/post_cleanup",
                "check_connection": False,
            },
        )
        kwargs = agent_class.call_args.kwargs
        case = load_test_case("TF-00")
        self.assertEqual(
            kwargs["max_executed_mouse_actions"],
            case.max_executed_mouse_actions,
        )
        self.assertEqual(kwargs["additional_system_prompt"], IBAPDA_UI_CONTEXT)
        self.assertEqual(kwargs["screenshot_dir"], "artifacts/ui_tests/tf_00")
        self.assertEqual(kwargs["verify_mouse_targets"], case.verify_mouse_targets)
        self.assertEqual(
            kwargs["abort_on_mouse_verification_failure"],
            case.abort_on_mouse_verification_failure,
        )
        self.assertEqual(kwargs["save_action_overlays"], case.save_action_overlays)
        self.assertIn(
            "ui_tests\\test_cases\\Reports\\tf_00\\tf_00_",
            kwargs["report_dir"],
        )
        minimize.assert_called_once_with()
        restore.assert_called_once_with()
        self.assertTrue(result["success"])
        self.assertEqual(result["report_dir"], kwargs["report_dir"])

    def test_default_report_dir_is_next_to_test_case_module(self):
        report_dir = default_report_dir_for_case(load_test_case("TF-00"))

        self.assertIn("ui_tests\\test_cases\\Reports\\tf_00\\tf_00_", report_dir)

    @patch("ui_tests.run_test_case.print")
    @patch("ui_tests.run_test_case.restore_minimized_windows_after_test")
    @patch("ui_tests.run_test_case.minimize_all_windows_for_test")
    @patch("ui_tests.run_test_case.SeeThinkActAgent")
    @patch("ui_tests.run_test_case.ensure_ibapda_closed")
    def test_case_can_run_without_data_recording_or_ibapda_cleanup(
        self, ensure_closed, agent_class, minimize, restore, _output
    ):
        case = UiTestCase(
            case_id="TF-01",
            description="Observe a non-recording state.",
            task="Inspect the displayed value and terminate with success.",
            additional_system_prompt=None,
            allowed_actions=frozenset({"wait", "terminate"}),
            verify_mouse_targets=False,
            abort_on_mouse_verification_failure=True,
            save_action_overlays=False,
            iteration_delay=0.1,
            post_action_delay=0.2,
            model_options={"temperature": 0},
            cleanup_ibapda_before=False,
            cleanup_ibapda_after=False,
        )
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"status": "success"}
        agent_class.return_value = agent

        result = run_test_case(case)

        ensure_closed.assert_not_called()
        kwargs = agent_class.call_args.kwargs
        self.assertIsNone(kwargs["additional_system_prompt"])
        self.assertEqual(kwargs["allowed_actions"], {"wait", "terminate"})
        self.assertFalse(kwargs["verify_mouse_targets"])
        self.assertTrue(kwargs["abort_on_mouse_verification_failure"])
        self.assertFalse(kwargs["save_action_overlays"])
        self.assertEqual(kwargs["iteration_delay"], 0.1)
        self.assertEqual(kwargs["post_action_delay"], 0.2)
        self.assertEqual(kwargs["model_options"], {"temperature": 0})
        self.assertIn(
            "ui_tests\\test_cases\\Reports\\tf_01\\tf_01_",
            kwargs["report_dir"],
        )
        minimize.assert_called_once_with()
        restore.assert_called_once_with()
        self.assertEqual(result["post_cleanup"]["status"], "not_required")

    @patch("ui_tests.run_test_case.SeeThinkActAgent")
    @patch(
        "ui_tests.run_test_case.ensure_ibapda_closed",
        return_value={"success": False, "status": "window_focus_failed"},
    )
    def test_failed_pre_cleanup_prevents_test_start(self, ensure_closed, agent_class):
        result = run_test_case(load_test_case("TF-00"))

        ensure_closed.assert_called_once_with(
            screenshot_dir="artifacts/ui_tests/tf_00/pre_cleanup"
        )
        agent_class.assert_not_called()
        self.assertEqual(result["status"], "pre_cleanup_failed")

    @patch("ui_tests.run_test_case.print")
    @patch("ui_tests.run_test_case.restore_minimized_windows_after_test")
    @patch("ui_tests.run_test_case.minimize_all_windows_for_test")
    @patch("ui_tests.run_test_case.SeeThinkActAgent")
    @patch(
        "ui_tests.run_test_case.ensure_ibapda_closed",
        side_effect=[
            {"success": True, "status": "already_closed"},
            {"success": True, "status": "success", "window_closed": True},
        ],
    )
    def test_failed_workflow_still_runs_post_cleanup(
        self, ensure_closed, agent_class, _minimize, restore, _output
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"success": False, "status": "aborted"}
        agent_class.return_value = agent

        result = run_test_case(load_test_case("TF-00"))

        self.assertEqual(ensure_closed.call_count, 2)
        restore.assert_called_once_with()
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "workflow_failed")

    @patch("ui_tests.run_test_case.print")
    @patch("ui_tests.run_test_case.restore_minimized_windows_after_test")
    @patch("ui_tests.run_test_case.minimize_all_windows_for_test")
    @patch("ui_tests.run_test_case.SeeThinkActAgent")
    @patch(
        "ui_tests.run_test_case.ensure_ibapda_closed",
        side_effect=[
            {"success": True, "status": "already_closed"},
            {"success": False, "status": "window_close_failed"},
        ],
    )
    def test_failed_post_cleanup_is_reported(
        self, _ensure_closed, agent_class, _minimize, restore, _output
    ):
        agent = Mock()
        agent.ollama_client.test_connection.return_value = True
        agent.run.return_value = {"success": True, "status": "success"}
        agent_class.return_value = agent

        result = run_test_case(load_test_case("TF-00"))

        restore.assert_called_once_with()
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "post_cleanup_failed")

if __name__ == "__main__":
    unittest.main()
