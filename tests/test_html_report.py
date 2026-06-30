import tempfile
import unittest
from pathlib import Path

from utils.html_report import HtmlRunReport


class HtmlRunReportTests(unittest.TestCase):
    def test_report_is_written_incrementally_with_iteration_details(self):
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            screenshot = Path(temp_dir) / "screenshot.png"
            screenshot.write_bytes(b"not a real png, only a link target")

            report = HtmlRunReport(temp_dir, title="Test Report")
            report.start("Run TF-00", metadata={"model": "qwen3.5:397b-cloud"})
            report.add_iteration({
                "iteration": 1,
                "timestamp": "2026-06-16T18:30:00",
                "screenshot_path": str(screenshot),
                "user_prompt": "What should I do first?",
                "system_prompt": "Use computer_use.",
                "response": {
                    "prompt_eval_count": 1200,
                    "eval_count": 80,
                    "total_duration": 3_750_000_000,
                    "message": {
                        "content": "",
                        "thinking": "I will double-click the ibaPDA icon.",
                        "tool_calls": [{
                            "function": {
                                "name": "computer_use",
                                "arguments": {"action": "double_click"},
                            }
                        }],
                    }
                },
                "tool_call": {
                    "function": {
                        "name": "computer_use",
                        "arguments": {"action": "double_click"},
                    }
                },
                "action_record": {
                    "arguments": {"action": "double_click"},
                    "intent": "Open ibaPDA Client from the desktop shortcut.",
                    "outcome": "executed",
                },
            })
            report.finish({
                "success": True,
                "status": "success",
                "iterations": 1,
                "elapsed_time": 12.3456,
            })

            html = report.report_path.read_text(encoding="utf-8")
            self.assertIn("Run TF-00", html)
            self.assertIn("Iteration 1", html)
            self.assertIn("2026-06-16 18:30:00", html)
            self.assertNotIn("2026-06-16T18:30:00", html)
            self.assertIn("Total time", html)
            self.assertIn("12.35 s", html)
            self.assertIn("Input tokens", html)
            self.assertIn("1200 tokens", html)
            self.assertIn("Output tokens", html)
            self.assertIn("80 tokens", html)
            self.assertIn("Model time", html)
            self.assertIn("3.75 s", html)
            self.assertNotIn("Input eval duration", html)
            self.assertNotIn("Output eval duration", html)
            self.assertIn("Iterations", html)
            self.assertIn("Success", html)
            self.assertIn("I will double-click the ibaPDA icon.", html)
            self.assertIn("Open ibaPDA Client from the desktop shortcut.", html)
            self.assertIn("computer_use", html)
            self.assertIn("double_click", html)
            self.assertIn("screenshot.png", html)

    def test_report_summary_keeps_measurement_timing_out_of_visible_summary(self):
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            report = HtmlRunReport(temp_dir, title="Measurement Report")
            report.start("Run TF-04")
            report.finish({
                "success": True,
                "status": "success",
                "iterations": 10,
                "elapsed_time": 301.0,
                "measurement_run": 2,
                "measured_started_at": "2026-06-22T20:00:00",
                "measured_finished_at": "2026-06-22T20:05:00",
                "measured_elapsed_time": 300.25,
            })

            html = report.report_path.read_text(encoding="utf-8")
            self.assertIn("Total time", html)
            self.assertIn("301.00 s", html)
            self.assertNotIn("Measurement run", html)
            self.assertNotIn("Measurement time", html)
            self.assertNotIn("Measurement started", html)
            self.assertNotIn("Measurement finished", html)
            self.assertIn("measured_elapsed_time", html)


if __name__ == "__main__":
    unittest.main()
