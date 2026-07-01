"""Definitions for executable UI test cases."""

from dataclasses import dataclass, field
from typing import Any, Optional

import config


@dataclass(frozen=True)
class UiTestCase:
    """Configuration and task description for one UI test case."""

    case_id: str
    description: str
    task: str
    prepare_task: Optional[str] = config.TEST_CASE_DEFAULT_PREPARE_TASK
    measurement_repetitions: int = config.TEST_CASE_DEFAULT_MEASUREMENT_REPETITIONS
    additional_system_prompt: Optional[str] = (
        config.TEST_CASE_DEFAULT_ADDITIONAL_SYSTEM_PROMPT
    )
    allowed_actions: Optional[frozenset[str]] = config.TEST_CASE_DEFAULT_ALLOWED_ACTIONS
    max_iterations: int = config.TEST_CASE_DEFAULT_MAX_ITERATIONS
    max_task_duration: float = config.TEST_CASE_DEFAULT_MAX_TASK_DURATION
    max_repeated_actions: int = config.TEST_CASE_DEFAULT_MAX_REPEATED_ACTIONS
    max_consecutive_failures: int = config.TEST_CASE_DEFAULT_MAX_CONSECUTIVE_FAILURES
    max_executed_mouse_actions: Optional[int] = (
        config.TEST_CASE_DEFAULT_MAX_EXECUTED_MOUSE_ACTIONS
    )
    verify_mouse_targets: bool = config.VERIFY_MOUSE_TARGETS
    abort_on_mouse_verification_failure: bool = (
        config.ABORT_ON_MOUSE_VERIFICATION_FAILURE
    )
    save_action_overlays: bool = config.SAVE_ACTION_OVERLAYS
    iteration_delay: float = config.ITERATION_DELAY
    post_action_delay: float = config.POST_ACTION_DELAY
    model_options: dict[str, Any] = field(
        default_factory=lambda: dict(config.MODEL_OPTIONS)
    )
    minimize_windows_before: bool = config.TEST_CASE_MINIMIZE_WINDOWS_BEFORE
    minimize_vscode_before: bool = False
    cleanup_ibapda_before: bool = config.TEST_CASE_CLEANUP_IBAPDA_BEFORE
    cleanup_ibapda_after: bool = config.TEST_CASE_CLEANUP_IBAPDA_AFTER
