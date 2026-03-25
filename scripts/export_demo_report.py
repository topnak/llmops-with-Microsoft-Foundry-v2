#!/usr/bin/env python3
"""Generate a concise final demo report for presentation use."""

from __future__ import annotations

import json
import sys

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import RESULTS_DIR
from llmops_demo.reporting import generate_demo_report, save_markdown
from llmops_demo.monitoring import get_monitoring_summary


def _load_json_safe(filename: str) -> dict | None:
    path = RESULTS_DIR / filename
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def main() -> None:
    setup_logging()

    print("Generating final demo report...")

    baseline = _load_json_safe("baseline_result.json")
    comparison = _load_json_safe("model_comparison.json")
    eval_summary = _load_json_safe("eval_summary.json")
    monitoring = get_monitoring_summary()

    report = generate_demo_report(
        baseline_result=baseline,
        comparison_result=comparison,
        eval_summary=eval_summary,
        monitoring_summary=monitoring,
    )

    path = save_markdown(report, "demo_report.md")
    print(f"Demo report saved to {path}")
    print("\n" + report)


if __name__ == "__main__":
    main()
