"""Active runtime defaults for the See-Think-Act agent."""

MODEL_NAME = "qwen3.5:397b-cloud"
MODEL_OPTIONS = {
    "temperature": 0.1,
    "num_ctx": 32768,
    "num_predict": 512,
}
OLLAMA_CHAT_MAX_RETRIES = 3
OLLAMA_CHAT_RETRY_DELAY = 2.0
OLLAMA_CHAT_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_ITERATIONS = 30
SAVE_SCREENSHOTS = True
SAVE_ACTION_OVERLAYS = True
VERIFY_MOUSE_TARGETS = True
ABORT_ON_MOUSE_VERIFICATION_FAILURE = False
SCREENSHOT_DIR = "agent_screenshots"
REPORT_DIR = "Reports"
LOG_LEVEL = "INFO"
DRY_RUN = True
ALLOWED_ACTIONS = None  # None allows every validated computer_use action.
MAX_EXECUTED_MOUSE_ACTIONS = None  # None does not impose a mouse-action budget.

# UI test case defaults. Individual tf_XX.py files should only override values
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
TEST_CASE_MINIMIZE_WINDOWS_BEFORE = True
TEST_CASE_CLEANUP_IBAPDA_BEFORE = True
TEST_CASE_CLEANUP_IBAPDA_AFTER = True

# Delays in seconds.
ITERATION_DELAY = 0.5
POST_ACTION_DELAY = 1.0
DRAG_DURATION = 1.5

# Safety limits. Set MAX_TASK_DURATION to 0 to disable the runtime limit.
MAX_TASK_DURATION = 600
MAX_REPEATED_ACTIONS = 3
MAX_CONSECUTIVE_FAILURES = 3

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
