import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image

from see_think_act_agent import SeeThinkActAgent
from utils.agent_function_call import ComputerUse


class AgentOverlayTests(unittest.TestCase):
    @patch("see_think_act_agent.create_provider")
    @patch("see_think_act_agent.ActionExecutor")
    @patch("see_think_act_agent.ScreenshotCapture")
    def setUp(self, mock_screenshot_capture, mock_action_executor, mock_create_provider):
        mock_screenshot_capture.return_value.get_screen_size.return_value = (1280, 720)
        mock_action_executor.return_value = Mock()
        mock_create_provider.return_value = Mock()

        self.temp_dir = tempfile.TemporaryDirectory(dir=".")
        self.addCleanup(self.temp_dir.cleanup)

        self.agent = SeeThinkActAgent(
            provider_type="ollama",
            model="test-model",
            dry_run=True,
            save_screenshots=True,
            save_action_overlays=True,
        )
        self.agent.llm_provider = Mock()
        self.agent.action_executor = Mock()
        self.agent.computer_use = ComputerUse()
        self.agent.task_completed = False
        self.agent.task_status = None
        self.agent.iteration_count = 1
        self.agent.action_history = []
        self.agent.dry_run = True
        self.agent.dry_run_action = None
        self.agent.last_action_overlay = None
        self.agent.save_screenshots = True
        self.agent.save_action_overlays = True
        self.agent.screenshot_dir = Path(self.temp_dir.name)
        self.agent.current_screenshot = Image.new("RGB", (1000, 1000), "white")

    def test_dry_run_saves_marked_mouse_target_before_execution(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "left_click", "coordinate": [500, 500]},
        }

        result = self.agent._execute_action({"message": {}})

        overlay_path = Path(self.agent.last_action_overlay)
        self.assertTrue(result)
        self.assertTrue(overlay_path.exists())
        self.assertEqual(self.agent.action_history[0]["overlay_path"], str(overlay_path))
        with Image.open(overlay_path) as overlay:
            self.assertEqual(overlay.getpixel((500, 500)), (255, 0, 0))
            self.assertEqual(overlay.getpixel((505, 505)), (255, 255, 255))
            self.assertEqual(overlay.getpixel((509, 500)), (255, 255, 255))
        self.agent.action_executor.execute_computer_use_action.assert_not_called()

    def test_non_mouse_action_does_not_save_overlay(self):
        self.agent.llm_provider.parse_computer_use_action.return_value = {
            "name": "computer_use",
            "arguments": {"action": "type", "text": "hello"},
        }

        self.agent._execute_action({"message": {}})

        self.assertIsNone(self.agent.last_action_overlay)
        self.assertEqual(list(Path(self.temp_dir.name).glob("*.png")), [])


if __name__ == "__main__":
    unittest.main()
