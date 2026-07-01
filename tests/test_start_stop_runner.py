import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import config
from ui_tests.contexts.ibapda import IBAPDA_UI_CONTEXT
from ui_tests.contexts.ibapda import IBAPDA_TF_01_LAYOUT_CONTEXT
from ui_tests.contexts.ibapda import IBAPDA_TF_02_DYNAMIC_LABEL_CONTEXT
from ui_tests.contexts.ibapda import IBAPDA_TF_03_CLIENT_PREFERENCES_LANGUAGE_CONTEXT
from ui_tests.contexts.ibapda import IBAPDA_TF_04_COMPLEX_LAYOUT_CONTEXT
from ui_tests.contexts.ibapda import IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT
from ui_tests.contexts.ibapda import IBAPDA_TF_06_SEMANTIC_STATE_CONTEXT
from ui_tests.run_test_case import default_report_dir_for_case, load_test_case, run_test_case
from ui_tests.test_cases import UiTestCase


class TestCaseDefinitionTests(unittest.TestCase):
    def test_ui_test_case_defaults_come_from_config(self):
        case = UiTestCase(
            case_id="TF-X",
            description="Minimal configurable test case.",
            task="Do one thing.",
        )

        self.assertEqual(case.prepare_task, config.TEST_CASE_DEFAULT_PREPARE_TASK)
        self.assertEqual(
            case.measurement_repetitions,
            config.TEST_CASE_DEFAULT_MEASUREMENT_REPETITIONS,
        )
        self.assertEqual(
            case.additional_system_prompt,
            config.TEST_CASE_DEFAULT_ADDITIONAL_SYSTEM_PROMPT,
        )
        self.assertEqual(case.allowed_actions, config.TEST_CASE_DEFAULT_ALLOWED_ACTIONS)
        self.assertEqual(
            case.max_iterations,
            config.TEST_CASE_DEFAULT_MAX_ITERATIONS,
        )
        self.assertEqual(
            case.max_task_duration,
            config.TEST_CASE_DEFAULT_MAX_TASK_DURATION,
        )
        self.assertEqual(
            case.max_repeated_actions,
            config.TEST_CASE_DEFAULT_MAX_REPEATED_ACTIONS,
        )
        self.assertEqual(
            case.max_consecutive_failures,
            config.TEST_CASE_DEFAULT_MAX_CONSECUTIVE_FAILURES,
        )
        self.assertEqual(
            case.max_executed_mouse_actions,
            config.TEST_CASE_DEFAULT_MAX_EXECUTED_MOUSE_ACTIONS,
        )
        self.assertEqual(case.verify_mouse_targets, config.VERIFY_MOUSE_TARGETS)
        self.assertEqual(
            case.abort_on_mouse_verification_failure,
            config.ABORT_ON_MOUSE_VERIFICATION_FAILURE,
        )
        self.assertEqual(case.save_action_overlays, config.SAVE_ACTION_OVERLAYS)
        self.assertEqual(case.iteration_delay, config.ITERATION_DELAY)
        self.assertEqual(case.post_action_delay, config.POST_ACTION_DELAY)
        self.assertEqual(case.model_options, config.MODEL_OPTIONS)
        self.assertIsNot(case.model_options, config.MODEL_OPTIONS)
        self.assertEqual(
            case.minimize_windows_before,
            config.TEST_CASE_MINIMIZE_WINDOWS_BEFORE,
        )
        self.assertEqual(
            case.cleanup_ibapda_before,
            config.TEST_CASE_CLEANUP_IBAPDA_BEFORE,
        )
        self.assertEqual(
            case.cleanup_ibapda_after,
            config.TEST_CASE_CLEANUP_IBAPDA_AFTER,
        )

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
        self.assertNotIn("scroll", case.allowed_actions)

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
        self.assertNotIn("scroll", case.allowed_actions)
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
        self.assertNotIn("scroll", case.allowed_actions)
        self.assertNotIn("answer", case.allowed_actions)
        self.assertGreaterEqual(case.max_iterations, 53)

    def test_tf_04_defines_complex_layout_navigation_workflow(self):
        case = load_test_case("TF-04")

        self.assertEqual(case.case_id, "TF-04")
        self.assertEqual(
            case.additional_system_prompt,
            IBAPDA_TF_04_COMPLEX_LAYOUT_CONTEXT,
        )
        self.assertIn("Goal:", case.task)
        self.assertIn("Measured run rules:", case.task)
        self.assertIn("Procedure", case.task)
        self.assertIn("primary tabs", case.task)
        self.assertIn("53 secondary tabs", case.task)
        self.assertIn("using\n  the TF-04 layout context", case.task)
        self.assertIn("Use only the canonical primary/secondary tab names", case.task)
        self.assertIn("matches\n  one expected checklist entry", case.task)
        self.assertIn("Reset navigation to the leftmost start point", case.task)
        self.assertIn("First verify whether the full\n   primary-tab label 'Start'", case.task)
        self.assertIn("do not click any expected Start\n   coordinate", case.task)
        self.assertIn("Click primary tab 'Start' only after", case.task)
        self.assertIn("verify from the next screenshot", case.task)
        self.assertIn("Verify whether secondary tab 'Start' is fully readable", case.task)
        self.assertIn("use the drag-bar rules from\n  the TF-04 context", case.task)
        self.assertIn("Mandatory rule before every secondary-tab click", case.task)
        self.assertIn("Look at the current screenshot and read the exact full", case.task)
        self.assertIn("use the horizontal drag-bar first", case.task)
        self.assertIn("Click the target secondary tab only after", case.task)
        self.assertIn("clipped or abbreviated label such as 'Sig...'", case.task)
        self.assertIn("Never assume what it means", case.task)
        self.assertIn("Confidence gate", case.task)
        self.assertIn("100% visual evidence", case.task)
        self.assertIn("inferred from position/history", case.task)
        self.assertIn("Before clicking primary tab 'Start'", case.task)
        self.assertIn("full label is readable\n  in the primary-tab row", case.task)
        self.assertIn("Do not click guessed coordinates for hidden tabs", case.task)
        self.assertIn("'Spielwiese' under the Start primary tab", case.task)
        self.assertIn("full\n   'Spielwiese' label is visible/readable", case.task)
        self.assertIn("Do not skip 'Spielwiese'", case.task)
        self.assertIn("Traverse each remaining primary tab from left to right", case.task)
        self.assertIn("complete all substeps below\n   before moving to the next primary tab", case.task)
        self.assertIn("Make the primary-tab label fully visible/readable", case.task)
        self.assertIn("Do not click\n      guessed coordinates", case.task)
        self.assertIn("Click the primary tab only after its full canonical label is readable", case.task)
        self.assertIn("Using the canonical checklist for this primary tab", case.task)
        self.assertIn("repeat this exact\n      sequence", case.task)
        self.assertIn("c1. Look at the current screenshot", case.task)
        self.assertIn("c2. If the full exact label is not completely visible", case.task)
        self.assertIn("c4. Click the secondary tab only after", case.task)
        self.assertIn("c6. Validate the QPanel content", case.task)
        self.assertIn("After all expected secondary tabs for this primary tab", case.task)
        self.assertIn("primary-tab summary checkpoint", case.task)
        self.assertIn("Never use ordinal, guessed, inferred, or truncated tab names", case.task)
        self.assertIn("not in the\n  canonical checklist", case.task)
        self.assertIn("A tab click is only an attempted action", case.task)
        self.assertIn("Execution history, previous\n  intent, checklist order", case.task)
        self.assertIn("secondary-tab checkpoint is missing", case.task)
        self.assertIn("nested/tertiary tabs", case.task)
        self.assertIn("all 7 primary tabs and all 53\n   secondary tabs were visited", case.task)
        self.assertNotIn("Include the known difficult sub-tab", case.task)
        self.assertIn("Do not open or switch projects", case.task)
        self.assertIn("stop Data Recording", case.task)
        self.assertIn("use answer", case.task)
        self.assertNotIn("Known layout facts", case.task)
        self.assertNotIn("horizontal tab drag-bar/scrollbar", case.task)
        self.assertNotIn("y=920-930", case.task)
        self.assertIsNotNone(case.prepare_task)
        self.assertTrue(case.cleanup_ibapda_before)
        self.assertTrue(case.minimize_windows_before)
        self.assertFalse(case.minimize_vscode_before)
        self.assertGreaterEqual(case.measurement_repetitions, 1)
        self.assertNotIn("five independent times", case.task)
        self.assertNotIn("stable initial state", case.prepare_task)
        self.assertNotIn("hscroll", case.allowed_actions)
        self.assertNotIn("scroll", case.allowed_actions)
        self.assertIn("left_click_drag", case.allowed_actions)
        self.assertIn("checkpoint", case.allowed_actions)
        self.assertIn("terminate", case.allowed_actions)
        self.assertNotIn("answer", case.allowed_actions)
        self.assertFalse(case.verify_mouse_targets)
        self.assertFalse(case.abort_on_mouse_verification_failure)
        self.assertGreaterEqual(case.max_iterations, 16)
        self.assertGreaterEqual(case.max_task_duration, 900)
        self.assertGreaterEqual(case.max_executed_mouse_actions, 100)

    def test_tf_05_defines_design_configuration_workflow(self):
        case = load_test_case("TF-05")

        self.assertEqual(case.case_id, "TF-05")
        self.assertEqual(
            case.additional_system_prompt,
            IBAPDA_TF_05_DESIGN_CONFIGURATION_CONTEXT,
        )
        self.assertIn("test_layout_textanzeige", case.task)
        self.assertIn("central QPanel/display area is\n  empty", case.task)
        self.assertIn("Projekt öffnen", case.task)
        self.assertIn("Initialwerte laden", case.task)
        self.assertIn("Entwurfsmodus", case.task)
        self.assertIn("Werkzeug/Werkzeuge tool pane", case.task)
        self.assertIn("Digitale Ziffernanzeige", case.task)
        self.assertIn("Digitale Textanzeige", case.task)
        self.assertIn("Trendkurve", case.task)
        self.assertIn("numeric display top-left", case.task)
        self.assertIn("text display\n  directly to its right", case.task)
        self.assertIn("trend curve below both", case.task)
        self.assertIn("Datensignal signal-selection dropdown", case.task)
        self.assertIn("GenerateSignal(0,100,10,10)", case.task)
        self.assertIn("GenerateText(\"ABC_%1\")", case.task)
        self.assertIn("Exit design mode before linking", case.task)
        self.assertIn("Signalbaum/signal tree", case.task)
        self.assertIn("validated during active Data\n    Recording", case.task)

        context = case.additional_system_prompt
        self.assertIn("right-click an empty area of the central QPanel/display", context)
        self.assertIn("second icon from the left", context)
        self.assertIn("light-blue background", context)
        self.assertIn("fourth icon from the left is a book icon", context)
        self.assertIn("'Bibliothek'. That is the wrong pane for TF-05", context)
        self.assertIn("target the vertical center of the\n  tool's visible text/row", context)
        self.assertIn("marker on the upper edge of the text row", context)
        self.assertIn("absolute normalized screen\n  coordinate", context)
        self.assertIn("yellow seven-segment placeholder", context)
        self.assertIn("gray-framed horizontal rectangle", context)
        self.assertIn("much larger black plotting area", context)
        self.assertIn("digital numeric display only by double-clicking", context)
        self.assertIn("digital text display only by right-clicking", context)
        self.assertIn("Datensignal field", context)
        self.assertIn("Do not assume the signal dropdown opened", context)
        self.assertIn("Select signals by expanding 'ibaPDA' -> 'Virtuell'", context)
        self.assertIn("indented child nodes appear underneath", context)
        self.assertIn("gray title/header bar labeled 'ibaPDA-Signalbaum'", context)
        self.assertIn("GenerateSignal(0,100,10,10) text is visible under 'Virtuell'", context)
        self.assertIn("not over the Signalbaum source", context)
        self.assertIn("mouse_move", case.allowed_actions)
        self.assertIn("left_click_drag", case.allowed_actions)
        self.assertIn("right_click", case.allowed_actions)
        self.assertIn("terminate", case.allowed_actions)
        self.assertNotIn("scroll", case.allowed_actions)
        self.assertNotIn("hscroll", case.allowed_actions)
        self.assertNotIn("answer", case.allowed_actions)
        self.assertTrue(case.verify_mouse_targets)
        self.assertFalse(case.abort_on_mouse_verification_failure)
        self.assertGreaterEqual(case.max_iterations, 80)

    def test_tf_06_defines_semantic_state_validation_workflow(self):
        case = load_test_case("TF-06")

        self.assertEqual(case.case_id, "TF-06")
        self.assertEqual(
            case.additional_system_prompt,
            IBAPDA_TF_06_SEMANTIC_STATE_CONTEXT,
        )
        self.assertIn("test_layout_multistatelabel", case.task)
        self.assertIn("trend curve", case.task)
        self.assertIn("multistatelabel", case.task)
        self.assertIn("'Wert > 0'", case.task)
        self.assertIn("green background", case.task)
        self.assertIn("'Wert < 0'", case.task)
        self.assertIn("red background", case.task)
        self.assertIn("same full-screen view", case.task)
        self.assertIn("positive state", case.task)
        self.assertIn("negative state", case.task)
        self.assertIn("both semantic states", case.task)
        self.assertIn("Do not open or switch projects", case.task)
        self.assertIn("Do not enter design mode", case.task)
        context = case.additional_system_prompt
        self.assertIn("triangle signal", context)
        self.assertIn("value range from -100 to 100", context)
        self.assertIn("large black chart", context)
        self.assertIn("same full-screen observation", context)
        self.assertIn("checkpoint", case.allowed_actions)
        self.assertIn("wait", case.allowed_actions)
        self.assertIn("terminate", case.allowed_actions)
        self.assertNotIn("answer", case.allowed_actions)
        self.assertTrue(case.verify_mouse_targets)
        self.assertFalse(case.abort_on_mouse_verification_failure)
        self.assertGreaterEqual(case.max_iterations, 45)


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
        report_base = Path(result["report_dir"])
        pre_cleanup_report_dir = str(report_base / "pre_cleanup")
        post_cleanup_report_dir = str(report_base / "post_cleanup")
        self.assertEqual(
            ensure_closed.call_args_list[0].kwargs,
            {
                "screenshot_dir": str(Path(pre_cleanup_report_dir) / "screenshots"),
                "report_dir": pre_cleanup_report_dir,
            },
        )
        self.assertEqual(
            ensure_closed.call_args_list[1].kwargs,
            {
                "screenshot_dir": str(Path(post_cleanup_report_dir) / "screenshots"),
                "check_connection": False,
                "report_dir": post_cleanup_report_dir,
            },
        )
        kwargs = agent_class.call_args.kwargs
        case = load_test_case("TF-00")
        self.assertEqual(
            kwargs["max_executed_mouse_actions"],
            case.max_executed_mouse_actions,
        )
        self.assertEqual(kwargs["additional_system_prompt"], IBAPDA_UI_CONTEXT)
        self.assertEqual(kwargs["screenshot_dir"], str(Path(kwargs["report_dir"]) / "screenshots"))
        self.assertEqual(kwargs["verify_mouse_targets"], case.verify_mouse_targets)
        self.assertEqual(
            kwargs["abort_on_mouse_verification_failure"],
            case.abort_on_mouse_verification_failure,
        )
        self.assertEqual(kwargs["save_action_overlays"], case.save_action_overlays)
        self.assertIn(
            "ui_tests\\test_cases\\Reports_Masterarbeit\\tf_00\\tf_00_",
            kwargs["report_dir"],
        )
        minimize.assert_called_once_with()
        restore.assert_called_once_with()
        self.assertTrue(result["success"])
        self.assertEqual(result["report_dir"], kwargs["report_dir"])

    def test_default_report_dir_is_next_to_test_case_module(self):
        report_dir = default_report_dir_for_case(load_test_case("TF-00"))

        self.assertIn("ui_tests\\test_cases\\Reports_Masterarbeit\\tf_00\\tf_00_", report_dir)

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
            "ui_tests\\test_cases\\Reports_Masterarbeit\\tf_01\\tf_01_",
            kwargs["report_dir"],
        )
        minimize.assert_called_once_with()
        restore.assert_called_once_with()
        self.assertEqual(result["post_cleanup"]["status"], "not_required")

    @patch("ui_tests.run_test_case.print")
    @patch("ui_tests.run_test_case.time.perf_counter", side_effect=[10.0, 12.5, 20.0, 23.0])
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
    def test_preparation_and_measurement_runs_are_separated(
        self, _ensure_closed, agent_class, _minimize, _restore, _time, _output
    ):
        preparation_agent = Mock()
        preparation_agent.ollama_client.test_connection.return_value = True
        preparation_agent.run.return_value = {
            "success": True,
            "status": "success",
            "iterations": 3,
            "elapsed_time": 30.0,
        }
        first_run_agent = Mock()
        first_run_agent.run.return_value = {
            "success": True,
            "status": "success",
            "iterations": 4,
            "elapsed_time": 99.0,
        }
        second_run_agent = Mock()
        second_run_agent.run.return_value = {
            "success": True,
            "status": "success",
            "iterations": 5,
            "elapsed_time": 99.0,
        }
        first_report = Mock()
        second_report = Mock()
        first_run_agent.report = first_report
        second_run_agent.report = second_report
        agent_class.side_effect = [preparation_agent, first_run_agent, second_run_agent]
        case = UiTestCase(
            case_id="TF-04",
            description="Measured layout navigation.",
            prepare_task="Prepare ibaPDA and start Data Recording.",
            task="Navigate the tabs once.",
            additional_system_prompt=None,
            allowed_actions=frozenset({"left_click", "wait", "checkpoint", "terminate"}),
            measurement_repetitions=2,
        )

        result = run_test_case(case)

        self.assertTrue(result["success"])
        workflow = result["workflow"]
        self.assertEqual(workflow["status"], "success")
        self.assertEqual(workflow["preparation"]["status"], "success")
        self.assertEqual(workflow["measurement_repetitions"], 2)
        self.assertEqual(len(workflow["measurement_runs"]), 2)
        self.assertEqual(workflow["measurement_runs"][0]["measured_elapsed_time"], 2.5)
        self.assertEqual(workflow["measurement_runs"][1]["measured_elapsed_time"], 3.0)
        first_report.finish.assert_called_once_with(workflow["measurement_runs"][0])
        second_report.finish.assert_called_once_with(workflow["measurement_runs"][1])
        self.assertEqual(workflow["iterations"], 9)
        preparation_agent.run.assert_called_once_with(case.prepare_task)
        first_run_agent.run.assert_called_once_with(case.task)
        second_run_agent.run.assert_called_once_with(case.task)
        self.assertIn("preparation", agent_class.call_args_list[0].kwargs["report_dir"])
        self.assertIn("measurement_run_01", agent_class.call_args_list[1].kwargs["report_dir"])
        self.assertIn("measurement_run_02", agent_class.call_args_list[2].kwargs["report_dir"])
        for call in agent_class.call_args_list:
            self.assertEqual(
                call.kwargs["screenshot_dir"],
                str(Path(call.kwargs["report_dir"]) / "screenshots"),
            )

    @patch("ui_tests.run_test_case.SeeThinkActAgent")
    @patch(
        "ui_tests.run_test_case.ensure_ibapda_closed",
        return_value={"success": False, "status": "window_focus_failed"},
    )
    def test_failed_pre_cleanup_prevents_test_start(self, ensure_closed, agent_class):
        result = run_test_case(load_test_case("TF-00"))

        cleanup_kwargs = ensure_closed.call_args.kwargs
        self.assertTrue(cleanup_kwargs["screenshot_dir"].endswith("pre_cleanup\\screenshots"))
        self.assertTrue(cleanup_kwargs["report_dir"].endswith("pre_cleanup"))
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
