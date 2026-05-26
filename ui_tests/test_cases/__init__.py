"""Definitions for executable UI test cases."""

from dataclasses import dataclass
from typing import Optional


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
    minimize_windows_before: bool = True
    cleanup_ibapda_before: bool = True
    cleanup_ibapda_after: bool = True
