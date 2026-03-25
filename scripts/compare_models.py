#!/usr/bin/env python3
"""Compare model outputs for the same scenario."""

from __future__ import annotations

import argparse
import json
import sys

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import SAMPLE_QUERIES, RESULTS_DIR
from llmops_demo.model_compare import compare_models
from llmops_demo.reporting import save_json, save_markdown


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="Compare models on a single scenario.")
    parser.add_argument(
        "--query", default=SAMPLE_QUERIES[0],
        help="User query to send.",
    )
    parser.add_argument("--prompt", default="baseline", help="Prompt variant.")
    parser.add_argument("--persona", default=None, help="Persona ID (optional).")
    args = parser.parse_args()

    print("Model Comparison")
    print(f"Prompt: {args.prompt}")
    print(f"Query: {args.query}")
    print("-" * 50)

    result = compare_models(
        args.query,
        prompt_name=args.prompt,
        persona_id=args.persona,
    )

    # Print comparison
    for c in result["comparisons"]:
        print(f"\n=== {c['model']} ===")
        print(f"Status: {c['status']}")
        print(f"Latency: {c['elapsed_seconds']}s")
        print(f"Response: {c['response_text'][:300]}")
        if c["error"]:
            print(f"Error: {c['error']}")

    # Save outputs
    save_json(result, "model_comparison.json")

    md_lines = ["# Model Comparison\n"]
    md_lines.append(f"**Query**: {result['user_input']}\n")
    md_lines.append(f"**Prompt**: {result['prompt_variant']}\n")
    md_lines.append("| Model | Status | Latency (s) | Response Preview |")
    md_lines.append("|-------|--------|-------------|------------------|")
    for c in result["comparisons"]:
        preview = c["response_text"][:100].replace("\n", " ")
        md_lines.append(f"| {c['model']} | {c['status']} | {c['elapsed_seconds']} | {preview} |")
    save_markdown("\n".join(md_lines), "model_comparison.md")

    print("\nComparison saved to results/")


if __name__ == "__main__":
    main()
