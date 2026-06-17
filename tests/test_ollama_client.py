import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import config
from utils.ollama_client import OllamaVisionClient


class OllamaVisionClientConnectionTests(unittest.TestCase):
    def test_connection_requires_model_to_answer_chat(self):
        client = OllamaVisionClient(model="qwen3-vl:235b-cloud")
        client.client = Mock()
        client.client.list.return_value = {
            "models": [{"model": "qwen3-vl:235b-cloud"}]
        }
        client.client.chat.return_value = {"message": {"content": "OK"}}

        self.assertTrue(client.test_connection())
        client.client.chat.assert_called_once()
        self.assertEqual(
            client.client.chat.call_args.kwargs["model"],
            "qwen3-vl:235b-cloud",
        )
        self.assertEqual(
            client.client.chat.call_args.kwargs["options"],
            config.MODEL_OPTIONS,
        )

    def test_connection_fails_when_listed_model_chat_fails(self):
        client = OllamaVisionClient(model="qwen3-vl:235b-cloud")
        client.client = Mock()
        client.client.list.return_value = {
            "models": [{"model": "qwen3-vl:235b-cloud"}]
        }
        client.client.chat.side_effect = RuntimeError("model retired")

        self.assertFalse(client.test_connection())

    def test_connection_fails_when_model_is_not_listed(self):
        client = OllamaVisionClient(model="qwen3-vl:235b-cloud")
        client.client = Mock()
        client.client.list.return_value = {
            "models": [SimpleNamespace(model="qwen3.5:cloud")]
        }
        client.client.show.side_effect = RuntimeError("not found")

        self.assertFalse(client.test_connection())
        client.client.chat.assert_not_called()

    def test_connection_uses_show_when_cloud_model_is_not_listed(self):
        client = OllamaVisionClient(model="qwen3.5:397b-cloud")
        client.client = Mock()
        client.client.list.return_value = {
            "models": [SimpleNamespace(model="qwen3.5:cloud")]
        }
        client.client.show.return_value = {"model": "qwen3.5:397b-cloud"}
        client.client.chat.return_value = {"message": {"content": "OK"}}

        self.assertTrue(client.test_connection())
        client.client.show.assert_called_once_with("qwen3.5:397b-cloud")
        client.client.chat.assert_called_once()

    def test_chat_sends_configured_model_options(self):
        options = {"temperature": 0.1, "num_ctx": 32768, "num_predict": 512}
        client = OllamaVisionClient(model="qwen3.5:397b-cloud", options=options)
        client.client = Mock()
        client.client.chat.return_value = {"message": {"content": "OK"}}

        client.chat(messages=[{"role": "user", "content": "hello"}])

        client.client.chat.assert_called_once()
        self.assertEqual(client.client.chat.call_args.kwargs["options"], options)

    def test_chat_normalizes_ollama_response_objects(self):
        response = Mock()
        response.model_dump.return_value = {
            "message": {
                "content": "",
                "thinking": "I can see the ibaPDA icon.",
                "tool_calls": [{
                    "function": {
                        "name": "computer_use",
                        "arguments": {"action": "double_click"},
                    }
                }],
            }
        }
        client = OllamaVisionClient(model="qwen3.5:397b-cloud")
        client.client = Mock()
        client.client.chat.return_value = response

        result = client.chat(messages=[{"role": "user", "content": "hello"}])

        self.assertEqual(result["message"]["thinking"], "I can see the ibaPDA icon.")
        self.assertEqual(
            result["message"]["tool_calls"][0]["function"]["arguments"]["action"],
            "double_click",
        )


if __name__ == "__main__":
    unittest.main()
