"""Ollama provider implementation wrapping existing OllamaVisionClient."""

import json
from typing import List, Dict, Any, Optional
from PIL import Image

from utils.llm_providers.base import LLMProvider
from utils.ollama_client import OllamaVisionClient


class OllamaProvider(LLMProvider):
    """Ollama provider using the existing OllamaVisionClient."""

    def __init__(
        self,
        model: str,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Ollama provider.

        Args:
            model: Model name to use (e.g., "qwen3.5:397b-cloud")
            options: Ollama generation options
        """
        self._client = OllamaVisionClient(model=model, options=options)
        self.model = model
        self.options = options or {}

    def chat_with_image(
        self,
        user_query: str,
        image: Image.Image,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send a chat request with image and optional tools."""
        return self._client.chat_with_image(
            user_query=user_query, image=image, system_prompt=system_prompt, tools=tools
        )

    def extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from model response."""
        return self._client.extract_tool_calls(response)

    def parse_computer_use_action(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse computer use action from model response."""
        return self._client.parse_computer_use_action(response)

    def test_connection(self) -> bool:
        """Verify connection to Ollama and model availability."""
        return self._client.test_connection()
