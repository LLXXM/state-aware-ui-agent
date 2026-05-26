import unittest
from unittest.mock import patch

from utils.action_executor import ActionExecutor
from utils.agent_function_call import ActionValidationError, ComputerUse


class ComputerUseSchemaTests(unittest.TestCase):
    def test_exposes_normalized_desktop_action_schema(self):
        function = ComputerUse().function
        parameters = function["parameters"]["properties"]

        self.assertEqual(function["name"], "computer_use")
        self.assertIn("normalized", parameters["coordinate"]["description"])
        self.assertIn("keys", parameters)
        self.assertIn("pixels", parameters)
        self.assertIn("time", parameters)

    def test_accepts_hotkey_arguments(self):
        arguments = ComputerUse().validate_arguments({
            "action": "key",
            "keys": ["ctrl", "l"],
        })

        self.assertEqual(arguments["keys"], ["ctrl", "l"])

    def test_rejects_mouse_action_without_coordinate(self):
        with self.assertRaises(ActionValidationError):
            ComputerUse().validate_arguments({"action": "left_click"})

    def test_normalizes_click_alias_to_left_click(self):
        arguments = ComputerUse().validate_arguments(
            {"action": "click", "coordinate": [100, 200]}
        )

        self.assertEqual(arguments["action"], "left_click")

    def test_rejects_coordinate_outside_normalized_range(self):
        with self.assertRaises(ActionValidationError):
            ComputerUse().validate_arguments({
                "action": "left_click",
                "coordinate": [1500, 200],
            })

    def test_rejects_termination_without_status(self):
        with self.assertRaises(ActionValidationError):
            ComputerUse().validate_arguments({"action": "terminate"})

    def test_accepts_checkpoint_with_observation_text(self):
        arguments = ComputerUse().validate_arguments({
            "action": "checkpoint",
            "text": "Recording indicator is green",
        })

        self.assertEqual(arguments["action"], "checkpoint")

    def test_rejects_checkpoint_without_observation_text(self):
        with self.assertRaises(ActionValidationError):
            ComputerUse().validate_arguments({"action": "checkpoint"})


class ActionExecutorContractTests(unittest.TestCase):
    def setUp(self):
        size_patcher = patch("utils.action_executor.pyautogui.size", return_value=(1920, 1080))
        self.addCleanup(size_patcher.stop)
        size_patcher.start()
        self.executor = ActionExecutor(screen_width=1920, screen_height=1080)

    @patch("utils.action_executor.pyautogui.click")
    def test_click_uses_normalized_coordinates(self, click):
        result = self.executor._execute_computer_action({
            "action": "left_click",
            "coordinate": [500, 500],
        })

        self.assertTrue(result)
        click.assert_called_once_with(x=960, y=540, button="left", clicks=1)

    @patch("utils.action_executor.pyautogui.click")
    def test_triple_click_is_supported(self, click):
        result = self.executor._execute_computer_action({
            "action": "triple_click",
            "coordinate": [250, 750],
        })

        self.assertTrue(result)
        click.assert_called_once_with(x=480, y=810, button="left", clicks=3)

    @patch("utils.action_executor.pyautogui.hotkey")
    def test_key_sequence_is_executed_as_hotkey(self, hotkey):
        result = self.executor._execute_computer_action({
            "action": "key",
            "keys": ["CTRL", "L"],
        })

        self.assertTrue(result)
        hotkey.assert_called_once_with("ctrl", "l")

    @patch("utils.action_executor.pyautogui.scroll")
    @patch("utils.action_executor.pyautogui.hscroll")
    def test_scroll_actions_use_pixels_argument(self, hscroll, scroll):
        self.assertTrue(self.executor._execute_computer_action({
            "action": "scroll",
            "pixels": -4,
        }))
        self.assertTrue(self.executor._execute_computer_action({
            "action": "hscroll",
            "pixels": 3,
        }))

        scroll.assert_called_once_with(-4)
        hscroll.assert_called_once_with(3)

    @patch("utils.action_executor.time.sleep")
    def test_wait_uses_time_argument(self, sleep):
        result = self.executor._execute_computer_action({
            "action": "wait",
            "time": 2,
        })

        self.assertTrue(result)
        sleep.assert_called_once_with(2)

    @patch("utils.action_executor.pyautogui.click")
    def test_mouse_action_without_coordinate_is_rejected(self, click):
        result = self.executor._execute_computer_action({"action": "left_click"})

        self.assertFalse(result)
        click.assert_not_called()


if __name__ == "__main__":
    unittest.main()
