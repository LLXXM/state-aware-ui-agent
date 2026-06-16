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
                "screenshot_path": str(screenshot),
                "user_prompt": "What should I do first?",
                "system_prompt": "Use computer_use.",
                "response": {
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
                    "outcome": "executed",
                },
            })
            report.finish({"status": "success"})

            html = report.report_path.read_text(encoding="utf-8")
            self.assertIn("Run TF-00", html)
            self.assertIn("Iteration 1", html)
            self.assertIn("I will double-click the ibaPDA icon.", html)
            self.assertIn("computer_use", html)
            self.assertIn("double_click", html)
            self.assertIn("screenshot.png", html)


if __name__ == "__main__":
    unittest.main()
