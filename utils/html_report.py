"""Incremental HTML report writer for agent runs."""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class HtmlRunReport:
    """Write a self-contained index page that references generated artifacts."""

    def __init__(self, report_dir: str | Path, title: str = "Computer Use Agent Report"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_path = self.report_dir / f"report_{timestamp}.html"
        self.title = title
        self.started_at = datetime.now()
        self.task = ""
        self.metadata: dict[str, Any] = {}
        self.iterations: list[dict[str, Any]] = []
        self.result: Optional[dict[str, Any]] = None

    def start(self, task: str, metadata: Optional[dict[str, Any]] = None) -> None:
        self.task = task
        self.metadata = dict(metadata or {})
        self.write()

    def add_iteration(self, record: dict[str, Any]) -> None:
        self.iterations.append(record)
        self.write()

    def finish(self, result: dict[str, Any]) -> None:
        self.result = dict(result)
        self.write()

    def write(self) -> None:
        self.report_path.write_text(self._render(), encoding="utf-8")

    def _artifact_href(self, path_value: Any) -> Optional[str]:
        if not path_value:
            return None
        path = Path(str(path_value))
        if not path.is_absolute():
            path = Path.cwd() / path
        try:
            return path.relative_to(self.report_path.parent).as_posix()
        except ValueError:
            return path.resolve().as_uri()

    @staticmethod
    def _json_block(value: Any) -> str:
        return html.escape(json.dumps(value, ensure_ascii=True, indent=2, default=str))

    @staticmethod
    def _text(value: Any) -> str:
        return html.escape("" if value is None else str(value))

    def _render_image(self, label: str, path_value: Any) -> str:
        href = self._artifact_href(path_value)
        if href is None:
            return ""
        return f"""
        <figure>
          <figcaption>{self._text(label)}: <code>{self._text(path_value)}</code></figcaption>
          <a href="{self._text(href)}"><img src="{self._text(href)}" alt="{self._text(label)}"></a>
        </figure>
        """

    def _render_iteration(self, record: dict[str, Any]) -> str:
        response = record.get("response") or {}
        message = response.get("message", {}) if isinstance(response, dict) else {}
        reasoning = (
            message.get("thinking")
            or message.get("reasoning")
            or message.get("content")
            or ""
        )
        action_record = record.get("action_record")
        tool_call = record.get("tool_call")
        verification = record.get("mouse_verification")

        return f"""
        <section class="iteration">
          <h2>Iteration {self._text(record.get("iteration"))}</h2>
          <div class="grid">
            <div>
              <h3>Screenshot</h3>
              {self._render_image("Screenshot", record.get("screenshot_path"))}
              {self._render_image("Action overlay", record.get("overlay_path"))}
            </div>
            <div>
              <h3>Reasoning / Response Text</h3>
              <pre>{self._text(reasoning)}</pre>
              <h3>Tool Call</h3>
              <pre>{self._json_block(tool_call)}</pre>
              <h3>Action Outcome</h3>
              <pre>{self._json_block(action_record)}</pre>
              <h3>Mouse Verification</h3>
              <pre>{self._json_block(verification)}</pre>
            </div>
          </div>
          <details>
            <summary>Prompt</summary>
            <h3>User Prompt</h3>
            <pre>{self._text(record.get("user_prompt"))}</pre>
            <h3>System Prompt</h3>
            <pre>{self._text(record.get("system_prompt"))}</pre>
          </details>
          <details>
            <summary>Raw Model Response</summary>
            <pre>{self._json_block(response)}</pre>
          </details>
        </section>
        """

    def _render(self) -> str:
        iterations = "\n".join(self._render_iteration(item) for item in self.iterations)
        result = self._json_block(self.result) if self.result is not None else "Run in progress"
        metadata = self._json_block(self.metadata)
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{self._text(self.title)}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; color: #202124; background: #f6f7f9; }}
    header {{ background: #18202a; color: white; padding: 24px 32px; }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
    h1, h2, h3 {{ margin: 0 0 12px; }}
    section, details {{ background: white; border: 1px solid #d9dde3; border-radius: 6px; margin: 16px 0; padding: 16px; }}
    .grid {{ display: grid; grid-template-columns: minmax(320px, 1fr) minmax(320px, 1fr); gap: 18px; }}
    img {{ max-width: 100%; border: 1px solid #c8cdd5; border-radius: 4px; background: white; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #f1f3f5; padding: 12px; border-radius: 4px; }}
    code {{ overflow-wrap: anywhere; }}
    figcaption {{ margin-bottom: 8px; color: #3f4854; }}
    @media (max-width: 850px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{self._text(self.title)}</h1>
    <div>Started: {self._text(self.started_at.isoformat(timespec="seconds"))}</div>
  </header>
  <main>
    <section>
      <h2>Task</h2>
      <pre>{self._text(self.task)}</pre>
      <h2>Metadata</h2>
      <pre>{metadata}</pre>
      <h2>Result</h2>
      <pre>{result}</pre>
    </section>
    {iterations}
  </main>
</body>
</html>
"""
