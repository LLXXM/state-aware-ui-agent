import inspect
import unittest
from unittest.mock import patch

import config
from see_think_act_agent import SeeThinkActAgent


class AgentConfigTests(unittest.TestCase):
    def test_constructor_defaults_come_from_config(self):
        parameters = inspect.signature(SeeThinkActAgent.__init__).parameters

        expected_defaults = {
            "model": config.MODEL_NAME,
            "max_iterations": config.MAX_ITERATIONS,
            "save_screenshots": config.SAVE_SCREENSHOTS,
            "save_action_overlays": config.SAVE_ACTION_OVERLAYS,
            "verify_mouse_targets": config.VERIFY_MOUSE_TARGETS,
            "abort_on_mouse_verification_failure": (
                config.ABORT_ON_MOUSE_VERIFICATION_FAILURE
            ),
            "screenshot_dir": config.SCREENSHOT_DIR,
            "log_level": config.LOG_LEVEL,
            "max_task_duration": config.MAX_TASK_DURATION,
            "max_repeated_actions": config.MAX_REPEATED_ACTIONS,
            "max_consecutive_failures": config.MAX_CONSECUTIVE_FAILURES,
            "iteration_delay": config.ITERATION_DELAY,
            "post_action_delay": config.POST_ACTION_DELAY,
            "dry_run": config.DRY_RUN,
            "allowed_actions": config.ALLOWED_ACTIONS,
            "max_executed_mouse_actions": config.MAX_EXECUTED_MOUSE_ACTIONS,
            "model_options": None,
            "report_dir": config.REPORT_DIR,
        }

        for name, default in expected_defaults.items():
            self.assertEqual(parameters[name].default, default)

    def test_system_prompt_comes_from_config(self):
        agent = SeeThinkActAgent.__new__(SeeThinkActAgent)

        self.assertEqual(agent._get_system_prompt(), config.SYSTEM_PROMPT)
        self.assertIn("checkpoint", config.SYSTEM_PROMPT)
        self.assertIn("computer_use", config.SYSTEM_PROMPT)

    def test_prepare_tools_filters_action_enum_to_allowed_actions(self):
        agent = SeeThinkActAgent.__new__(SeeThinkActAgent)
        from utils.agent_function_call import ComputerUse

        agent.computer_use = ComputerUse()
        agent.allowed_actions = {"checkpoint", "terminate"}

        tools = agent._prepare_tools()

        action_enum = tools[0]["function"]["parameters"]["properties"]["action"]["enum"]
        self.assertEqual(action_enum, ["checkpoint", "terminate"])
        self.assertNotIn("answer", action_enum)
        self.assertIn(
            "only these actions are allowed",
            tools[0]["function"]["parameters"]["properties"]["action"]["description"],
        )

    @patch("see_think_act_agent.ActionExecutor")
    @patch("see_think_act_agent.OllamaVisionClient")
    @patch("see_think_act_agent.ScreenshotCapture")
    def test_constructor_arguments_override_config(
        self, screenshot_capture, ollama_client, action_executor
    ):
        screenshot_capture.return_value.get_screen_size.return_value = (1280, 720)

        agent = SeeThinkActAgent(
            model="custom-model",
            max_iterations=7,
            save_screenshots=False,
            save_action_overlays=False,
            verify_mouse_targets=False,
            abort_on_mouse_verification_failure=True,
            screenshot_dir="custom-screens",
            log_level="DEBUG",
            max_task_duration=25,
            max_repeated_actions=1,
            max_consecutive_failures=2,
            iteration_delay=0.1,
            post_action_delay=0.2,
            dry_run=False,
            allowed_actions={"left_click", "terminate"},
            max_executed_mouse_actions=2,
            model_options={"temperature": 0},
            report_dir="custom-reports",
            additional_system_prompt="Application controls",
        )

        ollama_client.assert_called_once_with(
            model="custom-model",
            options={"temperature": 0},
        )
        action_executor.assert_called_once_with(screen_width=1280, screen_height=720)
        self.assertEqual(agent.max_iterations, 7)
        self.assertEqual(agent.max_task_duration, 25)
        self.assertEqual(agent.max_repeated_actions, 1)
        self.assertEqual(agent.max_consecutive_failures, 2)
        self.assertEqual(agent.iteration_delay, 0.1)
        self.assertEqual(agent.post_action_delay, 0.2)
        self.assertFalse(agent.dry_run)
        self.assertFalse(agent.save_action_overlays)
        self.assertFalse(agent.verify_mouse_targets)
        self.assertTrue(agent.abort_on_mouse_verification_failure)
        self.assertEqual(agent.allowed_actions, {"left_click", "terminate"})
        self.assertEqual(agent.max_executed_mouse_actions, 2)
        self.assertEqual(agent.additional_system_prompt, "Application controls")


if __name__ == "__main__":
    unittest.main()
