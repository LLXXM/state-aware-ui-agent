"""LLM Provider abstraction layer for multi-provider support.

This package provides a unified interface for different LLM providers
(Ollama, OpenRouter, OpenAI) with vision and tool calling support.
"""

from utils.llm_providers.base import LLMProvider
from utils.llm_providers.factory import (
    LLMProviderType,
    DEFAULT_MODEL_BY_PROVIDER,
    create_provider,
    create_provider_from_string,
)
from utils.llm_providers.ollama_provider import OllamaProvider
from utils.llm_providers.openrouter_provider import OpenRouterProvider
from utils.llm_providers.openai_provider import OpenAIProvider

__all__ = [
    "LLMProvider",
    "LLMProviderType",
    "DEFAULT_MODEL_BY_PROVIDER",
    "create_provider",
    "create_provider_from_string",
    "OllamaProvider",
    "OpenRouterProvider",
    "OpenAIProvider",
]
