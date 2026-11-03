"""Unit tests for the LLM provider abstraction layer."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional
from PIL import Image

from utils.llm_providers import (
    LLMProvider,
    LLMProviderType,
    DEFAULT_MODEL_BY_PROVIDER,
    create_provider,
    create_provider_from_string,
    OllamaProvider,
)
from utils.llm_providers.base import LLMProvider as BaseLLMProvider


class TestLLMProviderType(unittest.TestCase):
    """Tests for LLMProviderType enum."""

    def test_provider_types_exist(self):
        self.assertEqual(LLMProviderType.OLLAMA.value, "ollama")
        self.assertEqual(LLMProviderType.OPENROUTER.value, "openrouter")
        self.assertEqual(LLMProviderType.OPENAI.value, "openai")

    def test_default_models_defined(self):
        self.assertIn(LLMProviderType.OLLAMA, DEFAULT_MODEL_BY_PROVIDER)
        self.assertIn(LLMProviderType.OPENROUTER, DEFAULT_MODEL_BY_PROVIDER)
        self.assertIn(LLMProviderType.OPENAI, DEFAULT_MODEL_BY_PROVIDER)
        self.assertEqual(DEFAULT_MODEL_BY_PROVIDER[LLMProviderType.OLLAMA], "qwen3.5:397b-cloud")
        self.assertEqual(
            DEFAULT_MODEL_BY_PROVIDER[LLMProviderType.OPENROUTER], "qwen/qwen2.5-vl-72b-instruct"
        )
        self.assertEqual(DEFAULT_MODEL_BY_PROVIDER[LLMProviderType.OPENAI], "gpt-4o")


class TestProviderFactory(unittest.TestCase):
    """Tests for the provider factory functions."""

    def test_create_provider_ollama(self):
        provider = create_provider(LLMProviderType.OLLAMA, model="test-model")
        self.assertIsInstance(provider, OllamaProvider)
        self.assertEqual(provider.model, "test-model")

    def test_create_provider_ollama_default_model(self):
        provider = create_provider(LLMProviderType.OLLAMA)
        self.assertEqual(provider.model, "qwen3.5:397b-cloud")

    def test_create_provider_openrouter_requires_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                create_provider(LLMProviderType.OPENROUTER, model="test-model")
            self.assertIn("API key required", str(ctx.exception))

    def test_create_provider_openai_requires_api_key(self):
        with self.assertRaises(ValueError) as ctx:
            create_provider(LLMProviderType.OPENAI, model="test-model")
        self.assertIn("API key required", str(ctx.exception))

    def test_create_provider_unknown_type(self):
        with self.assertRaises(ValueError) as ctx:
            create_provider("unknown", model="test-model")
        self.assertIn("Unknown provider type", str(ctx.exception))

    def test_create_provider_from_string(self):
        provider = create_provider_from_string("ollama", model="test-model")
        self.assertIsInstance(provider, OllamaProvider)

    def test_create_provider_from_string_case_insensitive(self):
        for name in ["ollama", "OLLAMA", "Ollama", "openrouter", "OPENROUTER", "OpenRouter"]:
            try:
                provider = create_provider_from_string(name, model="test-model")
                self.assertIsNotNone(provider)
            except ValueError:
                if name.lower() not in ["openrouter", "openai"]:
                    self.fail(f"Should not fail for {name}")

    def test_create_provider_from_string_invalid(self):
        with self.assertRaises(ValueError) as ctx:
            create_provider_from_string("invalid", model="test-model")
        self.assertIn("Unknown provider", str(ctx.exception))


class TestOllamaProvider(unittest.TestCase):
    """Tests for OllamaProvider wrapper."""

    def setUp(self):
        self.mock_vision_client = Mock()
        self.mock_vision_client.model = "qwen3.5:397b-cloud"
        self.mock_vision_client.options = {"temperature": 0.1}

    @patch("utils.llm_providers.ollama_provider.OllamaVisionClient")
    def test_initialization(self, mock_client_class):
        mock_client_class.return_value = self.mock_vision_client
        provider = OllamaProvider(model="qwen3.5:397b-cloud", options={"temperature": 0.1})
        self.assertEqual(provider.model, "qwen3.5:397b-cloud")
        self.assertEqual(provider.options, {"temperature": 0.1})
        mock_client_class.assert_called_once_with(
            model="qwen3.5:397b-cloud", options={"temperature": 0.1}
        )

    @patch("utils.llm_providers.ollama_provider.OllamaVisionClient")
    def test_chat_with_image_delegates(self, mock_client_class):
        mock_client_class.return_value = self.mock_vision_client
        self.mock_vision_client.chat_with_image.return_value = {"message": {"content": "OK"}}

        provider = OllamaProvider(model="test-model")
        image = Image.new("RGB", (100, 100))
        result = provider.chat_with_image("test query", image, system_prompt="sys prompt")

        self.mock_vision_client.chat_with_image.assert_called_once_with(
            user_query="test query", image=image, system_prompt="sys prompt", tools=None
        )
        self.assertEqual(result, {"message": {"content": "OK"}})

    @patch("utils.llm_providers.ollama_provider.OllamaVisionClient")
    def test_extract_tool_calls_delegates(self, mock_client_class):
        mock_client_class.return_value = self.mock_vision_client
        self.mock_vision_client.extract_tool_calls.return_value = [{"function": {"name": "test"}}]

        provider = OllamaProvider(model="test-model")
        result = provider.extract_tool_calls(
            {"message": {"tool_calls": [{"function": {"name": "test"}}]}}
        )

        self.mock_vision_client.extract_tool_calls.assert_called_once()
        self.assertEqual(result, [{"function": {"name": "test"}}])

    @patch("utils.llm_providers.ollama_provider.OllamaVisionClient")
    def test_parse_computer_use_action_delegates(self, mock_client_class):
        mock_client_class.return_value = self.mock_vision_client
        self.mock_vision_client.parse_computer_use_action.return_value = {
            "function": {"name": "computer_use"}
        }

        provider = OllamaProvider(model="test-model")
        result = provider.parse_computer_use_action(
            {"message": {"tool_calls": [{"function": {"name": "computer_use"}}]}}
        )

        self.mock_vision_client.parse_computer_use_action.assert_called_once()
        self.assertEqual(result, {"function": {"name": "computer_use"}})

    @patch("utils.llm_providers.ollama_provider.OllamaVisionClient")
    def test_test_connection_delegates(self, mock_client_class):
        mock_client_class.return_value = self.mock_vision_client
        self.mock_vision_client.test_connection.return_value = True

        provider = OllamaProvider(model="test-model")
        result = provider.test_connection()

        self.mock_vision_client.test_connection.assert_called_once()
        self.assertTrue(result)


class TestLLMProviderInterface(unittest.TestCase):
    """Tests verifying LLMProvider abstract interface."""

    def test_abstract_methods_defined(self):
        abstract_methods = BaseLLMProvider.__abstractmethods__
        expected = {
            "chat_with_image",
            "extract_tool_calls",
            "parse_computer_use_action",
            "test_connection",
        }
        self.assertEqual(abstract_methods, expected)

    def test_ollama_provider_implements_interface(self):
        # Verify OllamaProvider implements all abstract methods
        for method in BaseLLMProvider.__abstractmethods__:
            self.assertTrue(hasattr(OllamaProvider, method), f"Missing method: {method}")
            self.assertTrue(callable(getattr(OllamaProvider, method)), f"Not callable: {method}")


class TestOpenRouterProviderMocked(unittest.TestCase):
    """Tests for OpenRouterProvider with mocked OpenAI client."""

    def setUp(self):
        self.mock_openai = Mock()

    @patch("utils.llm_providers.openrouter_provider.OpenAI")
    def test_initialization_with_api_key_param(self, mock_openai_class):
        mock_openai_class.return_value = self.mock_openai
        from utils.llm_providers.openrouter_provider import OpenRouterProvider

        provider = OpenRouterProvider(
            model="qwen/qwen2.5-vl-72b-instruct", api_key="test-key", options={"temperature": 0.1}
        )

        self.assertEqual(provider.model, "qwen/qwen2.5-vl-72b-instruct")
        self.assertEqual(provider.options, {"temperature": 0.1})
        mock_openai_class.assert_called_once()

    @patch("utils.llm_providers.openrouter_provider.OpenAI")
    def test_initialization_with_env_var(self, mock_openai_class):
        mock_openai_class.return_value = self.mock_openai
        from utils.llm_providers.openrouter_provider import OpenRouterProvider

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "env-key"}):
            provider = OpenRouterProvider(model="test-model")
            self.assertEqual(provider.api_key, "env-key")

    @patch("utils.llm_providers.openrouter_provider.OpenAI")
    def test_initialization_fails_without_key(self, mock_openai_class):
        from utils.llm_providers.openrouter_provider import OpenRouterProvider

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                OpenRouterProvider(model="test-model")
            self.assertIn("API key required", str(ctx.exception))

    @patch("utils.llm_providers.openrouter_provider.OpenAI")
    def test_chat_with_image_builds_correct_messages(self, mock_openai_class):
        mock_openai_class.return_value = self.mock_openai
        from utils.llm_providers.openrouter_provider import OpenRouterProvider

        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="OK", tool_calls=None))]
        self.mock_openai.chat.completions.create.return_value = mock_response

        provider = OpenRouterProvider(model="test-model", api_key="test-key")
        image = Image.new("RGB", (100, 100))
        result = provider.chat_with_image("test query", image, system_prompt="sys prompt")

        # Verify call was made
        self.mock_openai.chat.completions.create.assert_called_once()
        call_kwargs = self.mock_openai.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "test-model")
        self.assertEqual(len(call_kwargs["messages"]), 2)  # system + user
        self.assertEqual(call_kwargs["messages"][0]["role"], "system")
        self.assertEqual(call_kwargs["messages"][1]["role"], "user")

        # Verify result format
        self.assertIn("message", result)
        self.assertEqual(result["message"]["content"], "OK")


class TestOpenAIProviderMocked(unittest.TestCase):
    """Tests for OpenAIProvider with mocked OpenAI client."""

    @patch("utils.llm_providers.openai_provider.OpenAI")
    def test_initialization_with_api_key_param(self, mock_openai_class):
        mock_openai_class.return_value = Mock()
        from utils.llm_providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(model="gpt-4o", api_key="test-key")
        self.assertEqual(provider.model, "gpt-4o")

    @patch("utils.llm_providers.openai_provider.OpenAI")
    def test_initialization_fails_without_key(self, mock_openai_class):
        from utils.llm_providers.openai_provider import OpenAIProvider

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                OpenAIProvider(model="gpt-4o")
            self.assertIn("API key required", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
