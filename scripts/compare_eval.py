#!/usr/bin/env python3
"""Compare two evaluation result files and produce a delta report.

Usage:
    python scripts/compare_eval.py \
        --baseline results/eval_baseline.json \
        --candidate results/eval_candidate.json \
        --output results/eval_comparison.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DIMENSIONS = ["relevance", "personalization", "grounding", "policy_safety", "total"]


def load_summary(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compare(baseline: dict, candidate: dict) -> dict:
    """Compare two evaluation summaries and return structured comparison."""
    b_avg = baseline.get("averages", {})
    c_avg = candidate.get("averages", {})

    deltas = {}
    for dim in DIMENSIONS:
        b_val = b_avg.get(dim, 0)
        c_val = c_avg.get(dim, 0)
        delta = round(c_val - b_val, 2)
        deltas[dim] = {
            "baseline": b_val,
            "candidate": c_val,
            "delta": delta,
            "improved": delta > 0,
            "regressed": delta < 0,
        }

    any_regression = any(d["regressed"] for d in deltas.values())
    overall_improved = deltas.get("total", {}).get("improved", False)

    return {
        "dimensions": deltas,
        "baseline_count": baseline.get("count", 0),
        "candidate_count": candidate.get("count", 0),
        "any_regression": any_regression,
        "overall_improved": overall_improved,
        "recommendation": "APPROVE" if overall_improved and not any_regression else
                          "REVIEW" if overall_improved else "REJECT",
    }


def format_markdown(comparison: dict, baseline_name: str, candidate_name: str) -> str:
    """Format comparison as Markdown."""
    lines = [
        "# Prompt Evaluation Comparison\n",
        f"**Baseline**: `{baseline_name}` ({comparison['baseline_count']} cases)",
        f"**Candidate**: `{candidate_name}` ({comparison['candidate_count']} cases)\n",
        "## Score Comparison\n",
        "| Dimension | Baseline | Candidate | Delta | Status |",
        "|-----------|----------|-----------|-------|--------|",
    ]

    for dim in DIMENSIONS:
        d = comparison["dimensions"][dim]
        if d["improved"]:
            status = "🟢 Improved"
        elif d["regressed"]:
            status = "🔴 Regressed"
        else:
            status = "⚪ No change"
        sign = "+" if d["delta"] > 0 else ""
        lines.append(
            f"| {dim} | {d['baseline']:.2f} | {d['candidate']:.2f} "
            f"| {sign}{d['delta']:.2f} | {status} |"
        )

    lines.append(f"\n## Recommendation: **{comparison['recommendation']}**\n")

    if comparison["recommendation"] == "APPROVE":
        lines.append("All dimensions improved or held steady. Safe to deploy.")
    elif comparison["recommendation"] == "REVIEW":
        lines.append("Overall score improved but some dimensions regressed. Review before deploying.")
    else:
        lines.append("Overall score did not improve. Consider revising the prompt.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two evaluation results.")
    parser.add_argument("--baseline", required=True, help="Path to baseline eval JSON.")
    parser.add_argument("--candidate", required=True, help="Path to candidate eval JSON.")
    parser.add_argument("--baseline-name", default="baseline", help="Display name for baseline.")
    parser.add_argument("--candidate-name", default="candidate", help="Display name for candidate.")
    parser.add_argument("--output", default="results/eval_comparison.md", help="Output markdown path.")
    args = parser.parse_args()

    baseline = load_summary(args.baseline)
    candidate = load_summary(args.candidate)
    comparison = compare(baseline, candidate)

    md = format_markdown(comparison, args.baseline_name, args.candidate_name)
    print(md)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\nComparison saved to {args.output}")

    # Also save structured JSON
    json_path = args.output.replace(".md", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)
    print(f"Structured comparison saved to {json_path}")


if __name__ == "__main__":
    main()
