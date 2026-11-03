"""Abstract base class for LLM providers supporting vision and tool calling."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PIL import Image


class LLMProvider(ABC):
    """Abstract base for LLM providers supporting vision + tool calling."""

    @abstractmethod
    def chat_with_image(
        self,
        user_query: str,
        image: Image.Image,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a chat request with image and optional tools."""
        pass

    @abstractmethod
    def extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from provider-specific response format."""
        pass

    @abstractmethod
    def parse_computer_use_action(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse computer_use action from response."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Verify provider connectivity and model availability."""
        pass