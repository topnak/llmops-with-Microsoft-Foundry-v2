#!/usr/bin/env python3
"""Run the baseline scenario with the primary model and default prompt."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import PRIMARY_MODEL, SAMPLE_QUERIES, RESULTS_DIR
from llmops_demo.agent_runner import run_query
from llmops_demo.monitoring import record_event


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="Run baseline agent query.")
    parser.add_argument(
        "--query", default=SAMPLE_QUERIES[0],
        help="User query to send to the agent.",
    )
    parser.add_argument("--model", default=PRIMARY_MODEL, help="Model deployment name.")
    args = parser.parse_args()

    print("Running baseline query")
    print(f"Model: {args.model}")
    print(f"Query: {args.query}")
    print("-" * 50)

    result = run_query(args.query, prompt_name="baseline", model=args.model)
    result_dict = asdict(result)

    print(json.dumps(result_dict, indent=2))

    # Record monitoring event
    record_event(result)

    # Save result
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "baseline_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2)
    print(f"\nResult saved to {out_path}")

    if result.status == "error":
        print(f"\nERROR: {result.error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
