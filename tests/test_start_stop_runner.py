import unittest
from unittest.mock import Mock, patch

from ui_contexts import IBAPDA_UI_CONTEXT
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
        self.assertEqual(kwargs["save_action_overlays"], case.save_action_overlays)
        self.assertIn("ui_tests\\test_cases\\Reports\\tf_00_", kwargs["report_dir"])
        minimize.assert_called_once_with()
        restore.assert_called_once_with()
        self.assertTrue(result["success"])
        self.assertEqual(result["report_dir"], kwargs["report_dir"])

    def test_default_report_dir_is_next_to_test_case_module(self):
        report_dir = default_report_dir_for_case(load_test_case("TF-00"))

        self.assertIn("ui_tests\\test_cases\\Reports\\tf_00_", report_dir)

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
        self.assertFalse(kwargs["save_action_overlays"])
        self.assertEqual(kwargs["iteration_delay"], 0.1)
        self.assertEqual(kwargs["post_action_delay"], 0.2)
        self.assertEqual(kwargs["model_options"], {"temperature": 0})
        self.assertIn("ui_tests\\test_cases\\Reports\\tf_01_", kwargs["report_dir"])
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
