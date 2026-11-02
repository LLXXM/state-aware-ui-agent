import logging
import unittest
from unittest.mock import Mock

import config
from see_think_act_agent import SeeThinkActAgent


class AgentPromptTests(unittest.TestCase):
    def setUp(self):
        self.agent = SeeThinkActAgent.__new__(SeeThinkActAgent)
        self.agent.logger = logging.getLogger(__name__)
        self.agent.ollama_client = Mock()
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}
        self.agent._prepare_tools = Mock(return_value=[])
        self.agent.action_history = []
        self.agent.additional_system_prompt = None

    def test_first_iteration_asks_for_first_action(self):
        self.agent.iteration_count = 1

        self.agent._think_and_decide("Open Notepad", screenshot=object())

        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs["user_query"]
        self.assertIn("What should I do first", prompt)
        self.assertNotIn("after the previous action", prompt)

    def test_later_iteration_refers_to_previous_action(self):
        self.agent.iteration_count = 2

        self.agent._think_and_decide("Open Notepad", screenshot=object())

        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs["user_query"]
        self.assertIn("after the previous action", prompt)
        self.assertIn("What should I do next", prompt)

    def test_later_iteration_includes_action_history(self):
        self.agent.iteration_count = 2
        self.agent.action_history = [{
            "iteration": 1,
            "timestamp": "2026-06-16T18:30:00",
            "arguments": {"action": "left_click", "coordinate": [100, 200]},
            "intent": "Click the GO button to start recording.",
            "outcome": "executed",
        }]

        self.agent._think_and_decide("Continue workflow", screenshot=object())

        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs["user_query"]
        self.assertIn("Execution history from this task", prompt)
        self.assertIn('"action": "left_click"', prompt)
        self.assertIn("2026-06-16T18:30:00", prompt)
        self.assertIn("Click the GO button to start recording.", prompt)
        self.assertIn("executed", prompt)
        self.assertIn("verify effects", prompt)
        self.assertIn("repeat successful steps", prompt)

    def test_system_prompt_reserves_answer_for_terminal_response(self):
        system_prompt = self.agent._get_system_prompt()

        self.assertIn("entire user task", system_prompt)
        self.assertIn("intermediate visual check", system_prompt)
        self.assertIn("checkpoint", system_prompt)
        self.assertIn("intent", system_prompt)

    def test_additional_system_prompt_is_sent_separately_from_general_source(self):
        self.agent.iteration_count = 1
        self.agent.additional_system_prompt = "The green Go button starts the recording."

        self.agent._think_and_decide("Start the operation", screenshot=object())

        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs[
            "system_prompt"
        ]
        self.assertEqual(self.agent._get_system_prompt(), config.SYSTEM_PROMPT)
        self.assertIn("Application-specific UI context:", prompt)
        self.assertIn("The green Go button starts the recording.", prompt)

    def test_checkpoint_observation_is_included_in_later_prompt(self):
        self.agent.iteration_count = 3
        self.agent.action_history = [{
            "iteration": 2,
            "arguments": {
                "action": "checkpoint",
                "text": "Recording indicator is green",
            },
            "outcome": "observed",
        }]

        self.agent._think_and_decide("Finish workflow", screenshot=object())

        prompt = self.agent.ollama_client.chat_with_image.call_args.kwargs["user_query"]
        self.assertIn("Recording indicator is green", prompt)
        self.assertIn("observed", prompt)


if __name__ == "__main__":
    unittest.main()
