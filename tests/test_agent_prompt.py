import logging
import unittest
from unittest.mock import Mock

from see_think_act_agent import SeeThinkActAgent


class AgentPromptTests(unittest.TestCase):
    def setUp(self):
        self.agent = SeeThinkActAgent.__new__(SeeThinkActAgent)
        self.agent.logger = logging.getLogger(__name__)
        self.agent.ollama_client = Mock()
        self.agent.ollama_client.chat_with_image.return_value = {"message": {}}
        self.agent._prepare_tools = Mock(return_value=[])

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


if __name__ == "__main__":
    unittest.main()
