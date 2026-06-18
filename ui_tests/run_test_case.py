"""Run an individual UI test case with common preparation and cleanup."""

import argparse
import importlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from see_think_act_agent import SeeThinkActAgent
from ui_tests.support.ibapda_cleanup import ensure_ibapda_closed
from ui_tests.test_cases import UiTestCase
from ui_tests.support.window_setup import (
    minimize_all_windows_for_test,
    restore_minimized_windows_after_test,
)


def load_test_case(case_id: str) -> UiTestCase:
    """Load a test case module such as TF-00 from ui_tests.test_cases."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", case_id):
        raise ValueError(f"Invalid test case id: {case_id!r}")

    module_name = case_id.lower().replace("-", "_")
    module = importlib.import_module(f"ui_tests.test_cases.{module_name}")
    case = getattr(module, "CASE", None)
    if not isinstance(case, UiTestCase):
        raise TypeError(f"Test case module {module_name!r} does not define UiTestCase CASE.")
    return case


def _not_required_result(message: str) -> dict[str, Any]:
    return {"success": True, "status": "not_required", "message": message}


def default_report_dir_for_case(case: UiTestCase) -> str:
    """Return a timestamped report directory grouped by test case module."""
    module_name = case.case_id.lower().replace("-", "_")
    try:
        module = importlib.import_module(f"ui_tests.test_cases.{module_name}")
        test_case_dir = Path(module.__file__).parent
    except ModuleNotFoundError:
        test_case_dir = Path(__file__).parent / "test_cases"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(test_case_dir / "Reports" / module_name / f"{module_name}_{timestamp}")


def run_test_case(case: UiTestCase, report_dir: Optional[str] = None) -> dict[str, Any]:
    """Execute one test case using optional generic ibaPDA safety boundaries."""
    artifact_dir = f"artifacts/ui_tests/{case.case_id.lower().replace('-', '_')}"
    report_dir = report_dir or default_report_dir_for_case(case)

    if case.cleanup_ibapda_before:
        pre_cleanup = ensure_ibapda_closed(
            screenshot_dir=f"{artifact_dir}/pre_cleanup"
        )
    else:
        pre_cleanup = _not_required_result("No ibaPDA pre-cleanup configured.")

    if not pre_cleanup.get("success"):
        return {
            "success": False,
            "status": "pre_cleanup_failed",
            "message": "The configured pre-cleanup could not be completed.",
            "test_case": case.case_id,
            "pre_cleanup": pre_cleanup,
        }

    agent = SeeThinkActAgent(
        dry_run=False,
        max_iterations=case.max_iterations,
        save_screenshots=True,
        screenshot_dir=artifact_dir,
        max_task_duration=case.max_task_duration,
        max_repeated_actions=case.max_repeated_actions,
        max_consecutive_failures=case.max_consecutive_failures,
        iteration_delay=case.iteration_delay,
        post_action_delay=case.post_action_delay,
        allowed_actions=set(case.allowed_actions),
        max_executed_mouse_actions=case.max_executed_mouse_actions,
        verify_mouse_targets=case.verify_mouse_targets,
        abort_on_mouse_verification_failure=case.abort_on_mouse_verification_failure,
        save_action_overlays=case.save_action_overlays,
        model_options=case.model_options,
        report_dir=report_dir,
        additional_system_prompt=case.additional_system_prompt,
    )

    if not agent.ollama_client.test_connection():
        return {
            "success": False,
            "status": "connection_failed",
            "message": "Ollama is unavailable or the configured model is missing.",
            "test_case": case.case_id,
            "pre_cleanup": pre_cleanup,
            "report_dir": report_dir,
        }

    print(f"Starting UI test case {case.case_id}: {case.description}")
    print("Move the mouse to the top-left corner to trigger pyautogui failsafe.")
    print(f"Screenshots are stored in {artifact_dir}.")
    print(f"HTML report will be written to {report_dir}.")

    workflow: dict[str, Any]
    post_cleanup: dict[str, Any]
    if case.minimize_windows_before:
        minimize_all_windows_for_test()
    try:
        try:
            workflow = agent.run(case.task)
        except Exception as exc:
            workflow = {
                "success": False,
                "status": "execution_failed",
                "message": str(exc),
            }

        if case.cleanup_ibapda_after:
            post_cleanup = ensure_ibapda_closed(
                screenshot_dir=f"{artifact_dir}/post_cleanup",
                check_connection=False,
            )
        else:
            post_cleanup = _not_required_result("No ibaPDA post-cleanup configured.")
    finally:
        if case.minimize_windows_before:
            restore_minimized_windows_after_test()

    workflow_succeeded = workflow.get("status") == "success"
    cleanup_succeeded = bool(post_cleanup.get("success"))
    result = {
        "success": workflow_succeeded and cleanup_succeeded,
        "status": "success",
        "message": f"Test case {case.case_id} completed and cleanup succeeded.",
        "test_case": case.case_id,
        "pre_cleanup": pre_cleanup,
        "workflow": workflow,
        "post_cleanup": post_cleanup,
        "report_dir": report_dir,
    }
    if not workflow_succeeded:
        result["status"] = "workflow_failed"
        result["message"] = (
            f"Test case {case.case_id} did not complete successfully; cleanup was attempted."
        )
    elif not cleanup_succeeded:
        result["status"] = "post_cleanup_failed"
        result["message"] = (
            f"Test case {case.case_id} completed, but cleanup did not succeed."
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a configured UI test case.")
    parser.add_argument("case_id", help="Test case id, for example TF-00.")
    parser.add_argument(
        "--report-dir",
        help="Directory for the generated HTML report. Defaults next to the test case.",
    )
    args = parser.parse_args()
    result = run_test_case(load_test_case(args.case_id), report_dir=args.report_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
