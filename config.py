"""Active runtime defaults for the See-Think-Act agent.

Configuration priority (highest to lowest):
1. Constructor arguments (explicit override)
2. Environment variables (.env file)
3. Default values defined below
"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# LLM Provider Configuration
# ──────────────────────────────────────────────────────────────────────────────

# Provider selection: "ollama" | "openrouter" | "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()

# Default models per provider (can be overridden via MODEL_NAME env var)
DEFAULT_MODEL_BY_PROVIDER = {
    "ollama": "qwen3.5:397b-cloud",
    "openrouter": "nvidia/nemotron-3.5-super-vl",
    "openai": "gpt-4o",
}

# Active model (defaults to provider's default if not explicitly set)
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL_BY_PROVIDER.get(LLM_PROVIDER, "gpt-4o"))

# Model generation options (shared across providers where applicable)
MODEL_OPTIONS = {
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.1")),
    "num_ctx": int(os.getenv("MODEL_NUM_CTX", "32768")),
    "num_predict": int(os.getenv("MODEL_NUM_PREDICT", "512")),
    "top_p": float(os.getenv("MODEL_TOP_P", "1.0")),
    "top_k": int(os.getenv("MODEL_TOP_K", "0")),
}

# Ollama-specific retry settings
OLLAMA_CHAT_MAX_RETRIES = int(os.getenv("OLLAMA_CHAT_MAX_RETRIES", "3"))
OLLAMA_CHAT_RETRY_DELAY = float(os.getenv("OLLAMA_CHAT_RETRY_DELAY", "2.0"))
OLLAMA_CHAT_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

# ──────────────────────────────────────────────────────────────────────────────
# Secrets / Environment-Specific Overrides (from .env only)
# ──────────────────────────────────────────────────────────────────────────────

# OpenRouter - REQUIRED for openrouter provider
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_REFERER = os.getenv(
    "OPENROUTER_REFERER", "https://github.com/LLXXM/state-aware-ui-agent"
)
OPENROUTER_APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "State-aware-UI-agent")

# OpenAI - REQUIRED for openai provider
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # Optional, for Azure/custom endpoints

# Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ──────────────────────────────────────────────────────────────────────────────
# Agent Behavior Configuration (overridable via .env)
# ──────────────────────────────────────────────────────────────────────────────

MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "30"))
SAVE_SCREENSHOTS = os.getenv("SAVE_SCREENSHOTS", "true").lower() == "true"
SAVE_ACTION_OVERLAYS = os.getenv("SAVE_ACTION_OVERLAYS", "true").lower() == "true"
VERIFY_MOUSE_TARGETS = os.getenv("VERIFY_MOUSE_TARGETS", "true").lower() == "true"
ABORT_ON_MOUSE_VERIFICATION_FAILURE = (
    os.getenv("ABORT_ON_MOUSE_VERIFICATION_FAILURE", "false").lower() == "true"
)
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "agent_screenshots")
REPORT_DIR = os.getenv("REPORT_DIR", "Reports")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
ALLOWED_ACTIONS = None  # None allows every validated computer_use action.
MAX_EXECUTED_MOUSE_ACTIONS = None  # None does not impose a mouse-action budget.

# UI test case defaults. Individual test case files should only override values
# that are intentionally different for that specific test case.
TEST_CASE_DEFAULT_PREPARE_TASK = None
TEST_CASE_DEFAULT_MEASUREMENT_REPETITIONS = 1
TEST_CASE_DEFAULT_ADDITIONAL_SYSTEM_PROMPT = None
TEST_CASE_DEFAULT_ALLOWED_ACTIONS = None  # None allows every validated action.
TEST_CASE_DEFAULT_MAX_ITERATIONS = 12
TEST_CASE_DEFAULT_MAX_TASK_DURATION = 240
TEST_CASE_DEFAULT_MAX_REPEATED_ACTIONS = 2
TEST_CASE_DEFAULT_MAX_CONSECUTIVE_FAILURES = 2
TEST_CASE_DEFAULT_MAX_EXECUTED_MOUSE_ACTIONS = None
TEST_CASE_REPORTS_DIR_NAME = "Reports"

# Delays in seconds.
ITERATION_DELAY = float(os.getenv("ITERATION_DELAY", "0.5"))
POST_ACTION_DELAY = float(os.getenv("POST_ACTION_DELAY", "1.0"))
DRAG_DURATION = float(os.getenv("DRAG_DURATION", "1.5"))

# Safety limits. Set MAX_TASK_DURATION to 0 to disable the runtime limit.
MAX_TASK_DURATION = int(os.getenv("MAX_TASK_DURATION", "600"))
MAX_REPEATED_ACTIONS = int(os.getenv("MAX_REPEATED_ACTIONS", "3"))
MAX_CONSECUTIVE_FAILURES = int(os.getenv("MAX_CONSECUTIVE_FAILURES", "3"))

SYSTEM_PROMPT = """You are a helpful AI assistant that can see, think, and act on a Windows 11 computer.

Your capabilities:
1. SEE: You receive screenshots of the current desktop state
2. THINK: You analyze what you see and plan the next action
3. ACT: You can control the mouse, keyboard, and perform various actions

When given a task:
1. First, look at the screenshot to understand the current state
2. Think about what needs to be done to accomplish the task
3. Take ONE action at a time
4. After each action, you'll get a new screenshot to see the result
5. Continue until the task is complete

Important guidelines:
- Be precise with mouse coordinates: click the visual center of the intended button, not its edge, label neighbor, icon neighbor, border, or surrounding toolbar area
- Wait after actions that might take time (opening apps, loading pages)
- If an action fails, try adjusting your approach
- When the task is complete, use the 'terminate' action with status 'success'
- If the task cannot be completed, use 'terminate' with status 'failure'
- Use the 'answer' action only when giving a textual answer completes the entire user task
- For an intermediate visual check in a multi-step workflow, use 'checkpoint' to record the observation and continue with the next required action
- Use the execution history provided with later screenshots to avoid repeating completed actions
- Every 'computer_use' tool call must include an 'intent' field: one concise sentence explaining what this specific action is meant to accomplish next. The execution history and HTML report rely on this field.

You have access to a 'computer_use' tool that allows you to:
- Click (left, right, double, middle)
- Type text
- Press keys
- Move mouse
- Scroll
- Wait for changes
- Record a checkpoint for a verified intermediate visual state
- Terminate when done
"""
