"""Unit tests for configuration loader and provider settings."""

import os
import unittest
from unittest.mock import patch

from utils.config_loader import (
    get_env,
    get_env_bool,
    get_env_int,
    get_env_float,
    get_env_list,
    validate_provider_config,
    get_model_options,
    get_agent_config,
)


class TestConfigLoaderHelpers(unittest.TestCase):
    """Tests for basic config loader helper functions."""

    def setUp(self):
        # Save original environment
        self.original_env = dict(os.environ)

    def tearDown(self):
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_get_env_with_default(self):
        self.assertEqual(get_env("NONEXISTENT_KEY", "default_value"), "default_value")

    def test_get_env_without_default(self):
        self.assertIsNone(get_env("NONEXISTENT_KEY"))

    def test_get_env_required_raises(self):
        with self.assertRaises(ValueError) as ctx:
            get_env("NONEXISTENT_KEY", required=True)
        self.assertIn("Required environment variable", str(ctx.exception))

    def test_get_env_bool(self):
        os.environ["TEST_BOOL_TRUE"] = "true"
        os.environ["TEST_BOOL_FALSE"] = "false"
        os.environ["TEST_BOOL_1"] = "1"
        os.environ["TEST_BOOL_0"] = "0"
        os.environ["TEST_BOOL_YES"] = "yes"
        os.environ["TEST_BOOL_NO"] = "no"

        self.assertTrue(get_env_bool("TEST_BOOL_TRUE"))
        self.assertFalse(get_env_bool("TEST_BOOL_FALSE"))
        self.assertTrue(get_env_bool("TEST_BOOL_1"))
        self.assertFalse(get_env_bool("TEST_BOOL_0"))
        self.assertTrue(get_env_bool("TEST_BOOL_YES"))
        self.assertFalse(get_env_bool("TEST_BOOL_NO"))
        self.assertFalse(get_env_bool("NONEXISTENT"))
        self.assertTrue(get_env_bool("NONEXISTENT", default=True))

    def test_get_env_int(self):
        os.environ["TEST_INT"] = "42"
        self.assertEqual(get_env_int("TEST_INT"), 42)
        self.assertEqual(get_env_int("NONEXISTENT", 10), 10)
        self.assertEqual(get_env_int("INVALID_INT", 5), 5)  # Invalid falls back to default

    def test_get_env_float(self):
        os.environ["TEST_FLOAT"] = "3.14"
        self.assertEqual(get_env_float("TEST_FLOAT"), 3.14)
        self.assertEqual(get_env_float("NONEXISTENT", 2.5), 2.5)
        self.assertEqual(get_env_float("INVALID_FLOAT", 1.0), 1.0)

    def test_get_env_list(self):
        os.environ["TEST_LIST"] = "a, b, c"
        self.assertEqual(get_env_list("TEST_LIST"), ["a", "b", "c"])
        self.assertEqual(get_env_list("NONEXISTENT"), [])
        self.assertEqual(get_env_list("NONEXISTENT", ["default"]), ["default"])

    def test_get_env_list_custom_separator(self):
        os.environ["TEST_LIST_PIPE"] = "a|b|c"
        self.assertEqual(get_env_list("TEST_LIST_PIPE", separator="|"), ["a", "b", "c"])


class TestValidateProviderConfig(unittest.TestCase):
    """Tests for provider configuration validation."""

    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_validate_openrouter_requires_api_key(self):
        # Ensure OPENROUTER_API_KEY is not set
        os.environ.pop("OPENROUTER_API_KEY", None)
        with self.assertRaises(ValueError) as ctx:
            validate_provider_config("openrouter")
        self.assertIn("OPENROUTER_API_KEY required", str(ctx.exception))

    def test_validate_openrouter_with_api_key(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test-key"
        config = validate_provider_config("openrouter")
        self.assertEqual(config["provider"], "openrouter")
        self.assertEqual(config["api_key"], "sk-or-test-key")
        self.assertEqual(config["base_url"], "https://openrouter.ai/api/v1")
        self.assertEqual(config["referer"], "https://github.com/LLXXM/state-aware-ui-agent")
        self.assertEqual(config["app_title"], "State-aware-UI-agent")

    def test_validate_openrouter_custom_base_url(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test-key"
        os.environ["OPENROUTER_BASE_URL"] = "https://custom.openrouter.ai/api/v1"
        os.environ["OPENROUTER_REFERER"] = "https://custom.referer"
        os.environ["OPENROUTER_APP_TITLE"] = "Custom App"

        config = validate_provider_config("openrouter")
        self.assertEqual(config["base_url"], "https://custom.openrouter.ai/api/v1")
        self.assertEqual(config["referer"], "https://custom.referer")
        self.assertEqual(config["app_title"], "Custom App")

    def test_validate_openai_requires_api_key(self):
        os.environ.pop("OPENAI_API_KEY", None)
        with self.assertRaises(ValueError) as ctx:
            validate_provider_config("openai")
        self.assertIn("OPENAI_API_KEY required", str(ctx.exception))

    def test_validate_openai_with_api_key(self):
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        config = validate_provider_config("openai")
        self.assertEqual(config["provider"], "openai")
        self.assertEqual(config["api_key"], "sk-test-key")
        self.assertIsNone(config["base_url"])

    def test_validate_openai_custom_base_url(self):
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        os.environ["OPENAI_BASE_URL"] = "https://custom.azure.openai.com/"

        config = validate_provider_config("openai")
        self.assertEqual(config["base_url"], "https://custom.azure.openai.com/")

    def test_validate_ollama(self):
        config = validate_provider_config("ollama")
        self.assertEqual(config["provider"], "ollama")
        self.assertEqual(config["host"], "http://localhost:11434")
        self.assertEqual(config["max_retries"], 3)
        self.assertEqual(config["retry_delay"], 2.0)

    def test_validate_ollama_custom_settings(self):
        os.environ["OLLAMA_HOST"] = "http://remote:11434"
        os.environ["OLLAMA_CHAT_MAX_RETRIES"] = "5"
        os.environ["OLLAMA_CHAT_RETRY_DELAY"] = "3.5"

        config = validate_provider_config("ollama")
        self.assertEqual(config["host"], "http://remote:11434")
        self.assertEqual(config["max_retries"], 5)
        self.assertEqual(config["retry_delay"], 3.5)

    def test_validate_unknown_provider(self):
        with self.assertRaises(ValueError) as ctx:
            validate_provider_config("unknown")
        self.assertIn("Unknown provider", str(ctx.exception))

    def test_validate_provider_case_insensitive(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        for provider in ["OpenRouter", "OPENROUTER", "openrouter"]:
            config = validate_provider_config(provider)
            self.assertEqual(config["provider"], "openrouter")


class TestGetModelOptions(unittest.TestCase):
    """Tests for model options retrieval."""

    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_model_options(self):
        options = get_model_options()
        self.assertEqual(options["temperature"], 0.1)
        self.assertEqual(options["num_ctx"], 32768)
        self.assertEqual(options["num_predict"], 512)
        self.assertEqual(options["top_p"], 1.0)
        self.assertEqual(options["top_k"], 0)

    def test_custom_model_options(self):
        os.environ["MODEL_TEMPERATURE"] = "0.5"
        os.environ["MODEL_NUM_CTX"] = "16384"
        os.environ["MODEL_NUM_PREDICT"] = "1024"
        os.environ["MODEL_TOP_P"] = "0.9"
        os.environ["MODEL_TOP_K"] = "40"

        options = get_model_options()
        self.assertEqual(options["temperature"], 0.5)
        self.assertEqual(options["num_ctx"], 16384)
        self.assertEqual(options["num_predict"], 1024)
        self.assertEqual(options["top_p"], 0.9)
        self.assertEqual(options["top_k"], 40)


class TestGetAgentConfig(unittest.TestCase):
    """Tests for agent configuration retrieval."""

    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_agent_config(self):
        config = get_agent_config()
        self.assertEqual(config["max_iterations"], 30)
        self.assertTrue(config["save_screenshots"])
        self.assertTrue(config["save_action_overlays"])
        self.assertTrue(config["verify_mouse_targets"])
        self.assertFalse(config["abort_on_mouse_verification_failure"])
        self.assertEqual(config["screenshot_dir"], "agent_screenshots")
        self.assertEqual(config["report_dir"], "Reports")
        self.assertEqual(config["log_level"], "INFO")
        self.assertTrue(config["dry_run"])
        self.assertEqual(config["max_task_duration"], 600)
        self.assertEqual(config["max_repeated_actions"], 3)
        self.assertEqual(config["max_consecutive_failures"], 3)
        self.assertEqual(config["iteration_delay"], 0.5)
        self.assertEqual(config["post_action_delay"], 1.0)
        self.assertEqual(config["drag_duration"], 1.5)

    def test_custom_agent_config(self):
        os.environ["MAX_ITERATIONS"] = "50"
        os.environ["SAVE_SCREENSHOTS"] = "false"
        os.environ["VERIFY_MOUSE_TARGETS"] = "false"
        os.environ["DRY_RUN"] = "false"
        os.environ["MAX_TASK_DURATION"] = "1200"
        os.environ["ITERATION_DELAY"] = "1.0"

        config = get_agent_config()
        self.assertEqual(config["max_iterations"], 50)
        self.assertFalse(config["save_screenshots"])
        self.assertFalse(config["verify_mouse_targets"])
        self.assertFalse(config["dry_run"])
        self.assertEqual(config["max_task_duration"], 1200)
        self.assertEqual(config["iteration_delay"], 1.0)


class TestConfigModuleIntegration(unittest.TestCase):
    """Integration tests for config module with environment variables."""

    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
        # Reload config module to pick up changes
        import importlib
        import config

        importlib.reload(config)

    def test_config_reads_env_vars(self):
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["MODEL_NAME"] = "gpt-4o-mini"
        os.environ["MAX_ITERATIONS"] = "20"
        os.environ["DRY_RUN"] = "false"

        import importlib
        import config

        importlib.reload(config)

        self.assertEqual(config.LLM_PROVIDER, "openai")
        self.assertEqual(config.MODEL_NAME, "gpt-4o-mini")
        self.assertEqual(config.MAX_ITERATIONS, 20)
        self.assertFalse(config.DRY_RUN)

    def test_config_defaults_when_no_env(self):
        # Clear all relevant env vars
        for key in list(os.environ.keys()):
            if key.startswith(
                (
                    "LLM_",
                    "MODEL_",
                    "OPENROUTER_",
                    "OPENAI_",
                    "OLLAMA_",
                    "MAX_",
                    "SAVE_",
                    "VERIFY_",
                    "ABORT_",
                    "SCREENSHOT_",
                    "REPORT_",
                    "LOG_",
                    "DRY_",
                    "ITERATION_",
                    "POST_",
                    "DRAG_",
                    "ALLOWED_",
                    "TEST_",
                )
            ):
                del os.environ[key]

        import importlib
        import config

        importlib.reload(config)

        self.assertEqual(config.LLM_PROVIDER, "openrouter")
        self.assertEqual(config.MODEL_NAME, "qwen/qwen2.5-vl-72b-instruct")
        self.assertEqual(config.MAX_ITERATIONS, 30)
        self.assertTrue(config.DRY_RUN)


class TestProviderDefaultModels(unittest.TestCase):
    """Tests that default models are correctly set per provider."""

    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
        import importlib
        import config

        importlib.reload(config)

    def test_openrouter_default_model(self):
        os.environ["LLM_PROVIDER"] = "openrouter"
        import importlib
        import config

        importlib.reload(config)
        self.assertEqual(config.MODEL_NAME, "qwen/qwen2.5-vl-72b-instruct")

    def test_openai_default_model(self):
        os.environ["LLM_PROVIDER"] = "openai"
        import importlib
        import config

        importlib.reload(config)
        self.assertEqual(config.MODEL_NAME, "gpt-4o")

    def test_ollama_default_model(self):
        os.environ["LLM_PROVIDER"] = "ollama"
        import importlib
        import config

        importlib.reload(config)
        self.assertEqual(config.MODEL_NAME, "qwen3.5:397b-cloud")

    def test_explicit_model_overrides_provider_default(self):
        os.environ["LLM_PROVIDER"] = "openrouter"
        os.environ["MODEL_NAME"] = "custom/model-name"
        import importlib
        import config

        importlib.reload(config)
        self.assertEqual(config.MODEL_NAME, "custom/model-name")


if __name__ == "__main__":
    unittest.main()
