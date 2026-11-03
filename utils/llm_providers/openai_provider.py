"""OpenAI provider implementation using OpenAI API."""
import json
import base64
import io
import os
from typing import List, Dict, Any, Optional
from PIL import Image

from utils.llm_providers.base import LLMProvider

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAIProvider(LLMProvider):
    """OpenAI provider using OpenAI API directly."""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(
        self,
        model: str,
        options: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize OpenAI provider.

        Args:
            model: Model name (e.g., "gpt-4o", "gpt-4o-mini")
            options: Generation options (temperature, max_tokens, etc.)
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: API base URL (defaults to OpenAI default, can be used for Azure/OpenAI-compatible)
        """
        if OpenAI is None:
            raise ImportError(
                "openai package required for OpenAI provider. "
                "Install with: pip install openai"
            )

        self.model = model
        self.options = options or {}

        # Get API key from param or environment
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Pass api_key parameter or set OPENAI_API_KEY environment variable."
            )

        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL") or self.DEFAULT_BASE_URL

        # Initialize OpenAI client
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        # Map common option names to OpenAI format
        self._option_mapping = {
            "temperature": "temperature",
            "num_predict": "max_tokens",
            "num_ctx": "max_tokens",
            "top_p": "top_p",
            "top_k": "top_k",
        }

    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode("utf-8")

    def _build_messages(
        self,
        user_query: str,
        image: Image.Image,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Build messages array for OpenAI API."""
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Encode image
        image_base64 = self._encode_image(image)

        # User message with image
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_query},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                }
            ]
        })

        return messages

    def _convert_tools(self, tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Convert tools to OpenAI function calling format."""
        if not tools:
            return None

        openai_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": func.get("name"),
                        "description": func.get("description"),
                        "parameters": func.get("parameters", {})
                    }
                })
        return openai_tools if openai_tools else None

    def _map_options(self) -> Dict[str, Any]:
        """Map internal options to OpenAI format."""
        mapped = {}
        for key, value in self.options.items():
            openai_key = self._option_mapping.get(key, key)
            if openai_key == "max_tokens" and key == "num_ctx":
                # num_ctx is context window, not max tokens - skip
                continue
            mapped[openai_key] = value
        return mapped

    def chat_with_image(
        self,
        user_query: str,
        image: Image.Image,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a chat request with image and optional tools."""
        messages = self._build_messages(user_query, image, system_prompt)
        openai_tools = self._convert_tools(tools)
        options = self._map_options()

        # Make the request
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=openai_tools,
            **options
        )

        # Convert to Ollama-like response format for compatibility
        message = response.choices[0].message
        result = {
            "message": {
                "role": "assistant",
                "content": message.content or "",
            }
        }

        if message.tool_calls:
            result["message"]["tool_calls"] = [
                {
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]

        return result

    def extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from model response."""
        tool_calls = []
        if "message" in response:
            message = response["message"]
            if "tool_calls" in message:
                tool_calls = message["tool_calls"]
        return tool_calls

    def parse_computer_use_action(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse computer use action from model response."""
        tool_calls = self.extract_tool_calls(response)
        if tool_calls:
            return tool_calls[0]

        # Fallback: try to parse from content
        if "message" in response and "content" in response["message"]:
            content = response["message"]["content"]
            if "FUNCTION" in content and "RETURN" in content:
                try:
                    json_str = content.split("FUNCTION")[1].split("RETURN")[0].strip()
                    action = json.loads(json_str)
                    return action
                except (json.JSONDecodeError, IndexError):
                    pass
        return None

    def test_connection(self) -> bool:
        """Verify connection to OpenAI and model availability."""
        try:
            # Test with a simple chat request
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Connection check. Reply with OK."}
                ],
                max_tokens=10,
                **self._map_options()
            )
            print(f"OK: Model '{self.model}' answered a chat request via OpenAI")
            return True
        except Exception as e:
            print(f"ERROR: Could not connect to OpenAI: {e}")
            return False