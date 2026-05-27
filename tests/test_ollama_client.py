import unittest
from unittest.mock import Mock, patch

from utils.ollama_client import OllamaVisionClient


class OllamaVisionClientTests(unittest.TestCase):
    @patch("utils.ollama_client.ollama.Client")
    def test_uses_configured_remote_endpoint(self, client_class):
        client = OllamaVisionClient(
            model="qwen3.5:9b", host="http://192.168.1.20:11434", num_ctx=16384
        )

        client_class.assert_called_once_with(host="http://192.168.1.20:11434")
        self.assertEqual(client.model, "qwen3.5:9b")
        self.assertEqual(client.host, "http://192.168.1.20:11434")
        self.assertEqual(client.num_ctx, 16384)

    @patch("utils.ollama_client.ollama.Client")
    def test_connection_lists_models_from_remote_client(self, client_class):
        client_class.return_value.list.return_value = {
            "models": [{"model": "qwen3.5:9b"}]
        }
        client = OllamaVisionClient(
            model="qwen3.5:9b", host="http://192.168.1.20:11434"
        )

        self.assertTrue(client.test_connection())
        client_class.return_value.list.assert_called_once_with()

    @patch("utils.ollama_client.ollama.Client")
    def test_chat_passes_configured_context_window(self, client_class):
        client = OllamaVisionClient(model="qwen3.5:9b", num_ctx=16384)

        client.chat(messages=[{"role": "user", "content": "Act"}])

        self.assertEqual(
            client_class.return_value.chat.call_args.kwargs["options"],
            {"num_ctx": 16384},
        )


if __name__ == "__main__":
    unittest.main()
