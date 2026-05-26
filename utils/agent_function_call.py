class ComputerUse:
    """Schema exposed to the model for desktop actions."""

    name = "computer_use"

    parameters = {
        "properties": {
            "action": {
                "description": """
The action to perform. Available actions:
* `key`: Press one key or a keyboard shortcut using `keys`.
* `type`: Type a string using `text`.
* `mouse_move`: Move the cursor to `coordinate`.
* `left_click`, `right_click`, `middle_click`: Click at `coordinate`.
* `double_click`, `triple_click`: Click multiple times at `coordinate`.
* `left_click_drag`: Drag the cursor to `coordinate`.
* `scroll`: Perform vertical scrolling using `pixels`.
* `hscroll`: Perform horizontal scrolling using `pixels`.
* `wait`: Wait for `time` seconds.
* `terminate`: Finish the task and report `status`.
* `answer`: Return a textual answer using `text`.
""".strip(),
                "enum": [
                    "key",
                    "type",
                    "mouse_move",
                    "left_click",
                    "left_click_drag",
                    "right_click",
                    "middle_click",
                    "double_click",
                    "triple_click",
                    "scroll",
                    "hscroll",
                    "wait",
                    "terminate",
                    "answer",
                ],
                "type": "string",
            },
            "keys": {
                "description": "Keyboard keys for `action=key`, for example [`ctrl`, `l`] or [`enter`].",
                "items": {"type": "string"},
                "type": "array",
            },
            "text": {
                "description": "Text for `action=type` and `action=answer`.",
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
        "required": ["action"],
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
""".strip()

    @property
    def function(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
