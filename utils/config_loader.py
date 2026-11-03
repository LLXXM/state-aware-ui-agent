"""Configuration loader utilities for the See-Think-Act agent.

Provides helpers for loading, validating, and accessing configuration
from environment variables and .env files.
"""

import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load .env on module import
load_dotenv()


def get_env(key: str, default: Any = None, required: bool = False) -> Any:
    """Get environment variable with optional default and required check."""
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get environment variable as boolean."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def get_env_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get environment variable as float."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_env_list(key: str, default: Optional[List[str]] = None, separator: str = ",") -> List[str]:
    """Get environment variable as list of strings."""
    value = os.getenv(key)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


def validate_provider_config(provider: str) -> Dict[str, Any]:
    """Validate provider-specific configuration and return dict of settings."""
    provider = provider.lower()
    config = {"provider": provider}

    if provider == "openrouter":
        api_key = get_env("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY required for openrouter provider")
        config.update(
            {
                "api_key": api_key,
                "base_url": get_env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                "referer": get_env(
                    "OPENROUTER_REFERER", "https://github.com/LLXXM/state-aware-ui-agent"
                ),
                "app_title": get_env("OPENROUTER_APP_TITLE", "State-aware-UI-agent"),
            }
        )

    elif provider == "openai":
        api_key = get_env("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY required for openai provider")
        config.update(
            {
                "api_key": api_key,
                "base_url": get_env("OPENAI_BASE_URL"),
            }
        )

    elif provider == "ollama":
        config.update(
            {
                "host": get_env("OLLAMA_HOST", "http://localhost:11434"),
                "max_retries": get_env_int("OLLAMA_CHAT_MAX_RETRIES", 3),
                "retry_delay": get_env_float("OLLAMA_CHAT_RETRY_DELAY", 2.0),
            }
        )

    else:
        raise ValueError(f"Unknown provider: {provider}. Valid: ollama, openrouter, openai")

    return config


def get_model_options() -> Dict[str, Any]:
    """Get model generation options from environment."""
    return {
        "temperature": get_env_float("MODEL_TEMPERATURE", 0.1),
        "num_ctx": get_env_int("MODEL_NUM_CTX", 32768),
        "num_predict": get_env_int("MODEL_NUM_PREDICT", 512),
        "top_p": get_env_float("MODEL_TOP_P", 1.0),
        "top_k": get_env_int("MODEL_TOP_K", 0),
    }


def get_agent_config() -> Dict[str, Any]:
    """Get agent behavior configuration from environment."""
    return {
        "max_iterations": get_env_int("MAX_ITERATIONS", 30),
        "save_screenshots": get_env_bool("SAVE_SCREENSHOTS", True),
        "save_action_overlays": get_env_bool("SAVE_ACTION_OVERLAYS", True),
        "verify_mouse_targets": get_env_bool("VERIFY_MOUSE_TARGETS", True),
        "abort_on_mouse_verification_failure": get_env_bool(
            "ABORT_ON_MOUSE_VERIFICATION_FAILURE", False
        ),
        "screenshot_dir": get_env("SCREENSHOT_DIR", "agent_screenshots"),
        "report_dir": get_env("REPORT_DIR", "Reports"),
        "log_level": get_env("LOG_LEVEL", "INFO"),
        "dry_run": get_env_bool("DRY_RUN", True),
        "max_task_duration": get_env_int("MAX_TASK_DURATION", 600),
        "max_repeated_actions": get_env_int("MAX_REPEATED_ACTIONS", 3),
        "max_consecutive_failures": get_env_int("MAX_CONSECUTIVE_FAILURES", 3),
        "iteration_delay": get_env_float("ITERATION_DELAY", 0.5),
        "post_action_delay": get_env_float("POST_ACTION_DELAY", 1.0),
        "drag_duration": get_env_float("DRAG_DURATION", 1.5),
    }
