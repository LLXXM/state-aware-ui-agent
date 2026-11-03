"""Factory for creating LLM provider instances."""

from enum import Enum
from typing import Optional, Dict, Any

from utils.llm_providers.base import LLMProvider


class LLMProviderType(Enum):
    """Supported LLM provider types."""

    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    OPENAI = "openai"


# Default models per provider
DEFAULT_MODEL_BY_PROVIDER = {
    LLMProviderType.OLLAMA: "qwen3.5:397b-cloud",
    LLMProviderType.OPENROUTER: "qwen/qwen2.5-vl-72b-instruct",
    LLMProviderType.OPENAI: "gpt-4o",
}


def create_provider(
    provider_type: LLMProviderType,
    model: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> LLMProvider:
    """
    Factory to create provider instances.

    Args:
        provider_type: Type of provider to create
        model: Model name (defaults to provider's default)
        options: Generation options
        **kwargs: Additional provider-specific arguments (api_key, base_url, etc.)

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider_type is unknown
        ImportError: If required package for provider is not installed
    """
    # Use default model if not specified
    if model is None:
        model = DEFAULT_MODEL_BY_PROVIDER[provider_type]

    if provider_type == LLMProviderType.OLLAMA:
        from utils.llm_providers.ollama_provider import OllamaProvider

        return OllamaProvider(model=model, options=options)

    elif provider_type == LLMProviderType.OPENROUTER:
        from utils.llm_providers.openrouter_provider import OpenRouterProvider

        return OpenRouterProvider(model=model, options=options, **kwargs)

    elif provider_type == LLMProviderType.OPENAI:
        from utils.llm_providers.openai_provider import OpenAIProvider

        return OpenAIProvider(model=model, options=options, **kwargs)

    raise ValueError(f"Unknown provider type: {provider_type}")


def create_provider_from_string(
    provider_name: str,
    model: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> LLMProvider:
    """
    Create provider from string name (case-insensitive).

    Args:
        provider_name: Provider name ("ollama", "openrouter", "openai")
        model: Model name
        options: Generation options
        **kwargs: Additional provider-specific arguments

    Returns:
        LLMProvider instance
    """
    try:
        provider_type = LLMProviderType(provider_name.lower())
    except ValueError:
        valid = [p.value for p in LLMProviderType]
        raise ValueError(f"Unknown provider: '{provider_name}'. Valid options: {valid}")
    return create_provider(provider_type, model, options, **kwargs)
