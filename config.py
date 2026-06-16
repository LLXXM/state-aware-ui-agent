"""Active runtime defaults for the See-Think-Act agent."""

MODEL_NAME = "qwen3.5:397b-cloud"
MODEL_OPTIONS = {
    "temperature": 0.1,
    "num_ctx": 32768,
    "num_predict": 512,
}
MAX_ITERATIONS = 30
SAVE_SCREENSHOTS = True
SAVE_ACTION_OVERLAYS = True
VERIFY_MOUSE_TARGETS = True
SCREENSHOT_DIR = "agent_screenshots"
REPORT_DIR = "Reports"
LOG_LEVEL = "INFO"
DRY_RUN = True
ALLOWED_ACTIONS = None  # None allows every validated computer_use action.
MAX_EXECUTED_MOUSE_ACTIONS = None  # None does not impose a mouse-action budget.

# Delays in seconds.
ITERATION_DELAY = 0.5
POST_ACTION_DELAY = 1.0

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
- Be precise with mouse coordinates - aim for the center of buttons/links
- Wait after actions that might take time (opening apps, loading pages)
- If an action fails, try adjusting your approach
- When the task is complete, use the 'terminate' action with status 'success'
- If the task cannot be completed, use 'terminate' with status 'failure'
- Use the 'answer' action only when giving a textual answer completes the entire user task
- For an intermediate visual check in a multi-step workflow, use 'checkpoint' to record the observation and continue with the next required action
- Use the execution history provided with later screenshots to avoid repeating completed actions

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
