"""Definitions for executable UI test cases."""

from dataclasses import dataclass
from typing import Any, Optional

import config


@dataclass(frozen=True)
class UiTestCase:
    """Configuration and task description for one UI test case."""

    case_id: str
    description: str
    task: str
    additional_system_prompt: Optional[str] = None
    allowed_actions: frozenset[str] = frozenset(
        {"double_click", "left_click", "wait", "checkpoint", "terminate"}
    )
    max_iterations: int = 12
    max_task_duration: float = 240
    max_repeated_actions: int = 2
    max_consecutive_failures: int = 2
    max_executed_mouse_actions: Optional[int] = None
    verify_mouse_targets: bool = config.VERIFY_MOUSE_TARGETS
    abort_on_mouse_verification_failure: bool = (
        config.ABORT_ON_MOUSE_VERIFICATION_FAILURE
    )
    save_action_overlays: bool = config.SAVE_ACTION_OVERLAYS
    iteration_delay: float = config.ITERATION_DELAY
    post_action_delay: float = config.POST_ACTION_DELAY
    model_options: Optional[dict[str, Any]] = None
    minimize_windows_before: bool = True
    cleanup_ibapda_before: bool = True
    cleanup_ibapda_after: bool = True
