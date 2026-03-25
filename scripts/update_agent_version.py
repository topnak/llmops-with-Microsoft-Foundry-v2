#!/usr/bin/env python3
"""Create a new agent version from a selected prompt variant and model."""

from __future__ import annotations

import argparse
import json
import sys

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import PRIMARY_MODEL, RESULTS_DIR
from llmops_demo.agent_manager import create_agent_version_from_prompt
from llmops_demo.prompt_manager import list_prompts


def main() -> None:
    setup_logging()

    available = list_prompts()
    parser = argparse.ArgumentParser(
        description="Create a new agent version from a prompt variant."
    )
    parser.add_argument(
        "--prompt", required=True, choices=available,
        help="Prompt variant name.",
    )
    parser.add_argument("--model", default=PRIMARY_MODEL, help="Model deployment name.")
    args = parser.parse_args()

    print(f"Creating new agent version from prompt: {args.prompt}")
    print(f"Model: {args.model}")
    print("-" * 50)

    result = create_agent_version_from_prompt(args.prompt, args.model)
    print(json.dumps(result, indent=2))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "agent_version_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nResult saved to {out_path}")

    if result.get("status") == "error":
        print(f"\nERROR: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
