#!/usr/bin/env python3
"""Use an AI model via Foundry to analyze evaluation scores and suggest prompt improvements.

Usage:
    python scripts/ai_feedback.py \
        --comparison results/eval_comparison.json \
        --prompt grounded_retail \
        --output results/ai_feedback.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import PRIMARY_MODEL
from llmops_demo.foundry_client import create_project_client, get_openai_client
from llmops_demo.prompt_manager import load_prompt


ANALYSIS_SYSTEM_PROMPT = """\
You are an LLMOps prompt engineering expert. You analyze evaluation scores
for AI agent prompts and provide actionable feedback.

Given:
- A comparison of scores between a baseline prompt and a candidate prompt
- The candidate prompt text
- 4 scoring dimensions: relevance, personalization, grounding, policy_safety (each 0-5)

Provide:
1. A brief summary of what improved and what regressed
2. Specific suggestions to improve dimensions that scored low or regressed
3. An overall recommendation (deploy as-is, revise first, or reject)

Be concise and actionable. Use bullet points.
"""


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="AI-powered prompt feedback.")
    parser.add_argument("--comparison", required=True, help="Path to comparison JSON.")
    parser.add_argument("--prompt", required=True, help="Candidate prompt variant name.")
    parser.add_argument("--model", default=PRIMARY_MODEL, help="Model for analysis.")
    parser.add_argument("--output", default="results/ai_feedback.md", help="Output path.")
    parser.add_argument("--dry-run", action="store_true", help="Skip Foundry call.")
    args = parser.parse_args()

    # Load comparison data
    with open(args.comparison, encoding="utf-8") as f:
        comparison = json.load(f)

    # Load the candidate prompt
    prompt_text = load_prompt(args.prompt)

    # Build the analysis request
    score_table = "| Dimension | Baseline | Candidate | Delta |\n"
    score_table += "|-----------|----------|-----------|-------|\n"
    for dim, data in comparison.get("dimensions", {}).items():
        sign = "+" if data["delta"] > 0 else ""
        score_table += f"| {dim} | {data['baseline']:.2f} | {data['candidate']:.2f} | {sign}{data['delta']:.2f} |\n"

    user_message = f"""## Evaluation Comparison

{score_table}

Recommendation from scoring system: **{comparison.get('recommendation', 'N/A')}**

## Candidate Prompt Text

```
{prompt_text}
```

Please analyze these scores and provide:
1. What improved and what needs work
2. Specific suggestions to improve weak dimensions
3. Your recommendation: deploy, revise, or reject
"""

    if args.dry_run:
        feedback = (
            "# AI Feedback (Dry Run)\n\n"
            "AI analysis skipped (dry-run mode). To get real feedback, "
            "remove --dry-run and ensure Azure credentials are configured.\n\n"
            f"## Score Summary\n\n{score_table}\n"
            f"**Auto-recommendation**: {comparison.get('recommendation', 'N/A')}\n"
        )
    else:
        print(f"Requesting AI analysis via {args.model}...")
        client = create_project_client()
        openai_client = get_openai_client(client)

        response = openai_client.chat.completions.create(
            model=args.model,
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        ai_text = response.choices[0].message.content
        feedback = f"# AI Prompt Analysis\n\n{ai_text}\n"

    print(feedback)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(feedback)
    print(f"\nFeedback saved to {args.output}")


if __name__ == "__main__":
    main()
