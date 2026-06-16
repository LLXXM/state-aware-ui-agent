class ActionValidationError(ValueError):
    """Raised when a model action does not match the desktop action contract."""


class ComputerUse:
    """Schema exposed to the model for desktop actions."""

    name = "computer_use"
    MOUSE_ACTIONS = {
        "mouse_move",
        "left_click",
        "left_click_drag",
        "right_click",
        "middle_click",
        "double_click",
        "triple_click",
    }
    ACTIONS = MOUSE_ACTIONS | {
        "key",
        "type",
        "scroll",
        "hscroll",
        "wait",
        "checkpoint",
        "terminate",
        "answer",
    }

    parameters = {
        "properties": {
            "action": {
                "description": """
The action to perform. Available actions:
* `key`: Press one key or a keyboard shortcut using `keys`.
* `type`: Type a string using `text`.
* `mouse_move`: Move the cursor to `coordinate`.
* `left_click` or `click`, `right_click`, `middle_click`: Click at `coordinate`.
* `double_click`, `triple_click`: Click multiple times at `coordinate`.
* `left_click_drag`: Drag the cursor to `coordinate`.
* `scroll`: Perform vertical scrolling using `pixels`.
* `hscroll`: Perform horizontal scrolling using `pixels`.
* `wait`: Wait for `time` seconds.
* `checkpoint`: Record a visually confirmed intermediate workflow state using `text` and continue the task.
* `terminate`: Finish the task and report `status`.
* `answer`: Return a final textual answer using `text` only when answering completes the full user task, not for an intermediate workflow check.
""".strip(),
                "enum": [
                    "key",
                    "type",
                    "mouse_move",
                    "left_click",
                    "click",
                    "left_click_drag",
                    "right_click",
                    "middle_click",
                    "double_click",
                    "triple_click",
                    "scroll",
                    "hscroll",
                    "wait",
                    "checkpoint",
                    "terminate",
                    "answer",
                ],
                "type": "string",
            },
            "intent": {
                "description": (
                    "Required. Short purpose of this specific action, for reporting and action history. "
                    "Use one concise sentence that explains what this action is meant to accomplish, "
                    "for example: 'Click STOP to stop active Data Recording.'"
                ),
                "type": "string",
            },
            "keys": {
                "description": "Keyboard keys for `action=key`, for example [`ctrl`, `l`] or [`enter`].",
                "items": {"type": "string"},
                "type": "array",
            },
            "text": {
                "description": "Text for `action=type`, `action=checkpoint`, and `action=answer`.",
                "type": "string",
            },
            "coordinate": {
                "description": "A normalized [x, y] position on a 0-1000 scale, required for mouse actions.",
                "items": {"type": "number", "minimum": 0, "maximum": 1000},
                "maxItems": 2,
                "minItems": 2,
                "type": "array",
            },
            "pixels": {
                "description": "Scroll amount for `action=scroll` and `action=hscroll`; positive scrolls up/right and negative down/left.",
                "type": "number",
            },
            "time": {
                "description": "Seconds to wait for `action=wait`.",
                "maximum": 30,
                "minimum": 0,
                "type": "number",
            },
            "status": {
                "description": "Completion status for `action=terminate`.",
                "enum": ["success", "failure"],
                "type": "string",
            },
        },
        "required": ["action", "intent"],
        "type": "object",
    }

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.display_width_px = cfg.get("display_width_px", 1000)
        self.display_height_px = cfg.get("display_height_px", 1000)

    @property
    def description(self):
        return f"""
Use a mouse and keyboard to interact with a computer.
* Coordinates are normalized to a virtual {self.display_width_px}x{self.display_height_px} display.
* Inspect the latest screenshot before clicking an element.
* Take one action at a time and use `wait` when the interface needs time to update.
* Always include `intent` with every tool call as one concise sentence explaining why this action is next.
""".strip()

    @property
    def function(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    def validate_arguments(self, arguments: dict) -> dict:
        """Validate arguments produced by the model before execution."""
        if not isinstance(arguments, dict):
            raise ActionValidationError("Action arguments must be an object")

        action = arguments.get("action")
        if action == "click":
            arguments = dict(arguments)
            arguments["action"] = "left_click"
            action = "left_click"
        if action not in self.ACTIONS:
            raise ActionValidationError(f"Unsupported action: {action!r}")

        if "intent" in arguments:
            if not isinstance(arguments["intent"], str) or not arguments["intent"].strip():
                raise ActionValidationError("Intent must be a non-empty string")

        if action in self.MOUSE_ACTIONS:
            self._validate_coordinate(arguments.get("coordinate"))
        elif action == "key":
            keys = arguments.get("keys")
            if not isinstance(keys, list) or not keys:
                raise ActionValidationError("Key action requires non-empty keys")
            if not all(isinstance(key, str) and key for key in keys):
                raise ActionValidationError("Each key must be a non-empty string")
        elif action in {"type", "checkpoint", "answer"}:
            if not isinstance(arguments.get("text"), str):
                raise ActionValidationError(f"{action} action requires text")
        elif action in {"scroll", "hscroll"}:
            if not self._is_number(arguments.get("pixels")):
                raise ActionValidationError(f"{action} action requires numeric pixels")
        elif action == "wait":
            seconds = arguments.get("time")
            if not self._is_number(seconds) or not 0 <= seconds <= 30:
                raise ActionValidationError("Wait time must be between 0 and 30 seconds")
        elif action == "terminate":
            if arguments.get("status") not in {"success", "failure"}:
                raise ActionValidationError(
                    "Terminate action requires success or failure status"
                )

        return arguments

    @staticmethod
    def _is_number(value) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @classmethod
    def _validate_coordinate(cls, coordinate) -> None:
        if not isinstance(coordinate, list) or len(coordinate) != 2:
            raise ActionValidationError("Mouse action requires coordinate [x, y]")

        if not all(cls._is_number(value) and 0 <= value <= 1000 for value in coordinate):
            raise ActionValidationError("Coordinate values must be between 0 and 1000")
