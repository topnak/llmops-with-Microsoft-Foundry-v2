#!/usr/bin/env python3
"""Run evaluation suite against eval_cases.jsonl and write reports."""

from __future__ import annotations

import argparse
import json
import sys

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import PRIMARY_MODEL
from llmops_demo.evaluation import (
    load_eval_cases,
    run_evaluation,
    generate_eval_summary,
    save_eval_reports,
)
from llmops_demo.agent_runner import run_query


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="Run evaluation suite.")
    parser.add_argument("--prompt", default="baseline", help="Prompt variant.")
    parser.add_argument("--model", default=PRIMARY_MODEL, help="Model deployment.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Score with empty responses (no Foundry calls).",
    )
    args = parser.parse_args()

    cases = load_eval_cases()
    print(f"Loaded {len(cases)} evaluation cases.")
    print(f"Prompt: {args.prompt} | Model: {args.model}")
    print("-" * 50)

    responses = []
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {case['id']}: {case['user_input'][:60]}...")
        if args.dry_run:
            response_text = ""
        else:
            try:
                result = run_query(
                    case["user_input"],
                    prompt_name=args.prompt,
                    model=args.model,
                    persona_id=case.get("persona_id"),
                )
                response_text = result.response_text
            except Exception as exc:
                print(f"   Error: {exc}")
                response_text = ""
        responses.append({"case": case, "response_text": response_text})

    results = run_evaluation(responses)
    summary = generate_eval_summary(results)

    # Print summary
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    for dim, score in summary["averages"].items():
        print(f"  {dim}: {score}")
    print(f"\n  Total cases: {summary['count']}")

    json_path, md_path = save_eval_reports(summary)
    print(f"\nReports saved:\n  {json_path}\n  {md_path}")


if __name__ == "__main__":
    main()
