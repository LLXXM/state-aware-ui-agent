"""Definitions for executable UI test cases."""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import config


@dataclass(frozen=True)
class UiTestCase:
    """Configuration and task description for one UI test case."""

    case_id: str
    description: str
    task: str
    prepare_task: Optional[str] = config.TEST_CASE_DEFAULT_PREPARE_TASK
    measurement_repetitions: int = config.TEST_CASE_DEFAULT_MEASUREMENT_REPETITIONS
    app_context: Optional[str] = config.TEST_CASE_DEFAULT_ADDITIONAL_SYSTEM_PROMPT
    allowed_actions: Optional[frozenset[str]] = config.TEST_CASE_DEFAULT_ALLOWED_ACTIONS
    max_iterations: int = config.TEST_CASE_DEFAULT_MAX_ITERATIONS
    max_task_duration: float = config.TEST_CASE_DEFAULT_MAX_TASK_DURATION
    max_repeated_actions: int = config.TEST_CASE_DEFAULT_MAX_REPEATED_ACTIONS
    max_consecutive_failures: int = config.TEST_CASE_DEFAULT_MAX_CONSECUTIVE_FAILURES
    max_executed_mouse_actions: Optional[int] = config.TEST_CASE_DEFAULT_MAX_EXECUTED_MOUSE_ACTIONS
    verify_mouse_targets: bool = config.VERIFY_MOUSE_TARGETS
    abort_on_mouse_verification_failure: bool = config.ABORT_ON_MOUSE_VERIFICATION_FAILURE
    save_action_overlays: bool = config.SAVE_ACTION_OVERLAYS
    iteration_delay: float = config.ITERATION_DELAY
    post_action_delay: float = config.POST_ACTION_DELAY
    model_options: dict[str, Any] = field(default_factory=lambda: dict(config.MODEL_OPTIONS))
    # LLM Provider settings
    provider_type: str = config.LLM_PROVIDER
    model: Optional[str] = None
    # Monitor settings
    monitor_number: int = 1
    pre_run_setup: Optional[Callable[[], dict]] = None
    post_run_cleanup: Optional[Callable[[], dict]] = None
    report_dir_name: str = config.TEST_CASE_REPORTS_DIR_NAME
