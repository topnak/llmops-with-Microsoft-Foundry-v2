"""Reporting helpers — save artifacts to results/ in various formats."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from llmops_demo.config import RESULTS_DIR

logger = logging.getLogger(__name__)


def save_json(data: Any, filename: str) -> str:
    """Save data as JSON to results/. Returns the file path."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved JSON: %s", path)
    return str(path)


def save_markdown(content: str, filename: str) -> str:
    """Save Markdown content to results/. Returns the file path."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / filename
    path.write_text(content, encoding="utf-8")
    logger.info("Saved Markdown: %s", path)
    return str(path)


def generate_demo_report(
    baseline_result: dict | None = None,
    comparison_result: dict | None = None,
    eval_summary: dict | None = None,
    monitoring_summary: dict | None = None,
) -> str:
    """Generate a final presentation-friendly report in Markdown."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections = [
        f"# LLMOps Demo Report\n\nGenerated: {now}\n",
    ]

    if baseline_result:
        sections.append("## Baseline Run\n")
        sections.append(f"- **Model**: {baseline_result.get('model_name', 'N/A')}")
        sections.append(f"- **Prompt**: {baseline_result.get('prompt_variant', 'N/A')}")
        sections.append(f"- **Latency**: {baseline_result.get('elapsed_seconds', 'N/A')}s")
        sections.append(f"- **Status**: {baseline_result.get('status', 'N/A')}\n")

    if comparison_result:
        sections.append("## Model Comparison\n")
        for c in comparison_result.get("comparisons", []):
            sections.append(f"### {c['model']}")
            sections.append(f"- Status: {c['status']}")
            sections.append(f"- Latency: {c['elapsed_seconds']}s")
            sections.append(f"- Response preview: {c['response_text'][:150]}...\n")

    if eval_summary:
        sections.append("## Evaluation Summary\n")
        sections.append(f"- **Cases**: {eval_summary.get('count', 0)}")
        for dim, score in eval_summary.get("averages", {}).items():
            sections.append(f"- **{dim}**: {score}")
        sections.append("")

    if monitoring_summary:
        sections.append("## Monitoring Summary\n")
        sections.append(f"- **Total events**: {monitoring_summary.get('total_events', 0)}")
        sections.append(f"- **Successes**: {monitoring_summary.get('successes', 0)}")
        sections.append(f"- **Errors**: {monitoring_summary.get('errors', 0)}")
        sections.append(f"- **Avg latency**: {monitoring_summary.get('avg_latency_seconds', 0)}s\n")

    sections.append("---\n*LLMOps loop complete.*")
    return "\n".join(sections)
