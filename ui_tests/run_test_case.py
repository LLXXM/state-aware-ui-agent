"""Run an individual UI test case with generic preparation and cleanup."""

import argparse
import importlib
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import config
from see_think_act_agent import SeeThinkActAgent
from ui_tests.test_cases import UiTestCase


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
    return str(test_case_dir / case.report_dir_name / module_name / f"{module_name}_{timestamp}")


def _screenshots_dir_for_report(report_dir: str | Path) -> str:
    return str(Path(report_dir) / "screenshots")


def _build_agent(case: UiTestCase, report_dir: str) -> SeeThinkActAgent:
    return SeeThinkActAgent(
        provider_type=case.provider_type,
        model=case.model,
        dry_run=False,
        max_iterations=case.max_iterations,
        save_screenshots=True,
        screenshot_dir=_screenshots_dir_for_report(report_dir),
        max_task_duration=case.max_task_duration,
        max_repeated_actions=case.max_repeated_actions,
        max_consecutive_failures=case.max_consecutive_failures,
        iteration_delay=case.iteration_delay,
        post_action_delay=case.post_action_delay,
        allowed_actions=(None if case.allowed_actions is None else set(case.allowed_actions)),
        max_executed_mouse_actions=case.max_executed_mouse_actions,
        verify_mouse_targets=case.verify_mouse_targets,
        abort_on_mouse_verification_failure=case.abort_on_mouse_verification_failure,
        save_action_overlays=case.save_action_overlays,
        model_options=case.model_options,
        report_dir=report_dir,
        additional_system_prompt=case.app_context,
    )


def _run_case_workflow(
    case: UiTestCase,
    report_dir: str,
) -> dict[str, Any]:
    if not case.prepare_task:
        agent = _build_agent(case, report_dir)
        if not agent.llm_provider.test_connection():
            return {
                "success": False,
                "status": "connection_failed",
                "message": "LLM provider is unavailable or the configured model is missing.",
            }
        return agent.run(case.task)

    report_base = Path(report_dir)
    preparation_agent = _build_agent(
        case,
        str(report_base / "preparation"),
    )
    if not preparation_agent.llm_provider.test_connection():
        return {
            "success": False,
            "status": "connection_failed",
            "message": "LLM provider is unavailable or the configured model is missing.",
        }

    preparation = preparation_agent.run(case.prepare_task)
    if preparation.get("status") != "success":
        return {
            "success": False,
            "status": "preparation_failed",
            "message": "The configured preparation task did not complete successfully.",
            "preparation": preparation,
            "measurement_repetitions": case.measurement_repetitions,
            "measurement_runs": [],
        }

    measurement_runs = []
    repetitions = max(1, case.measurement_repetitions)
    for run_index in range(1, repetitions + 1):
        run_label = f"measurement_run_{run_index:02d}"
        run_agent = _build_agent(
            case,
            str(report_base / run_label),
        )
        started_at = datetime.now().isoformat(timespec="seconds")
        started = time.perf_counter()
        run_result = run_agent.run(case.task)
        measured_elapsed = time.perf_counter() - started
        run_result["measurement_run"] = run_index
        run_result["measured_started_at"] = started_at
        run_result["measured_finished_at"] = datetime.now().isoformat(timespec="seconds")
        run_result["measured_elapsed_time"] = measured_elapsed
        run_report = vars(run_agent).get("report")
        if run_report is not None:
            run_report.finish(run_result)
        measurement_runs.append(run_result)
        if run_result.get("status") != "success":
            break

    measurement_succeeded = len(measurement_runs) == repetitions and all(
        run.get("status") == "success" for run in measurement_runs
    )
    return {
        "success": measurement_succeeded,
        "status": "success" if measurement_succeeded else "measurement_failed",
        "message": (
            f"Completed {len(measurement_runs)} of {repetitions} configured measurement runs."
        ),
        "preparation": preparation,
        "measurement_repetitions": repetitions,
        "measurement_runs": measurement_runs,
        "iterations": sum(run.get("iterations", 0) for run in measurement_runs),
        "elapsed_time": sum(run.get("measured_elapsed_time", 0.0) for run in measurement_runs),
    }


def run_test_case(case: UiTestCase, report_dir: Optional[str] = None) -> dict[str, Any]:
    """Execute one test case using generic setup and cleanup hooks."""
    report_dir = report_dir or default_report_dir_for_case(case)
    report_base = Path(report_dir)

    # Pre-run setup
    if case.pre_run_setup:
        pre_setup_report_dir = str(report_base / "pre_setup")
        pre_setup = case.pre_run_setup()
        # Optionally attach report dir to result for traceability
        if isinstance(pre_setup, dict):
            pre_setup.setdefault("report_dir", pre_setup_report_dir)
    else:
        pre_setup = _not_required_result("No pre-run setup configured.")

    if not pre_setup.get("success"):
        return {
            "success": False,
            "status": "pre_setup_failed",
            "message": "The configured pre-run setup could not be completed.",
            "test_case": case.case_id,
            "pre_setup": pre_setup,
        }

    print(f"Starting UI test case {case.case_id}: {case.description}")
    print("Move the mouse to the top-left corner to trigger pyautogui failsafe.")
    print(f"HTML reports and screenshots will be written to {report_dir}.")

    workflow: dict[str, Any]
    post_cleanup: dict[str, Any]
    try:
        try:
            workflow = _run_case_workflow(case, report_dir)
        except Exception as exc:
            workflow = {
                "success": False,
                "status": "execution_failed",
                "message": str(exc),
            }

        # Post-run cleanup
        if case.post_run_cleanup:
            post_cleanup_report_dir = str(report_base / "post_cleanup")
            post_cleanup = case.post_run_cleanup()
            if isinstance(post_cleanup, dict):
                post_cleanup.setdefault("report_dir", post_cleanup_report_dir)
        else:
            post_cleanup = _not_required_result("No post-run cleanup configured.")
    finally:
        # No automatic window restoration - cleanup hook handles it if needed
        pass

    workflow_succeeded = workflow.get("status") == "success"
    cleanup_succeeded = bool(post_cleanup.get("success"))
    result = {
        "success": workflow_succeeded and cleanup_succeeded,
        "status": "success",
        "message": f"Test case {case.case_id} completed and cleanup succeeded.",
        "test_case": case.case_id,
        "pre_setup": pre_setup,
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
        result["message"] = f"Test case {case.case_id} completed, but cleanup did not succeed."
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
