#!/usr/bin/env python3
"""Run evaluation using azure-ai-evaluation SDK and upload results to Foundry portal.

This script creates evaluations that appear under the Agent's Evaluation tab
in the Microsoft Foundry portal. It uses Foundry built-in evaluators
(RelevanceEvaluator, CoherenceEvaluator, FluencyEvaluator) which are
LLM-as-judge evaluators backed by an Azure OpenAI deployment.

Usage:
    # Full run: invoke agent + evaluate + upload to Foundry
    python scripts/foundry_eval.py --prompt aussie_mate

    # Dry-run: generate data only (no Foundry calls, no upload)
    python scripts/foundry_eval.py --prompt aussie_mate --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

from azure.identity import DefaultAzureCredential

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import (
    AZURE_EXISTING_AIPROJECT_ENDPOINT,
    PRIMARY_MODEL,
    RESULTS_DIR,
)
from llmops_demo.evaluation import load_eval_cases
from llmops_demo.agent_runner import run_query


def build_eval_dataset(
    cases: list[dict],
    prompt_name: str,
    model: str,
    dry_run: bool = False,
) -> list[dict]:
    """Invoke the agent for each eval case and build the evaluation dataset.

    Returns a list of dicts with keys: query, response, context.
    """
    rows = []
    for i, case in enumerate(cases, 1):
        query = case["user_input"]
        print(f"[{i}/{len(cases)}] {case['id']}: {query[:60]}...")

        if dry_run:
            response_text = "(dry-run — no agent call)"
        else:
            try:
                result = run_query(
                    query,
                    prompt_name=prompt_name,
                    model=model,
                    persona_id=case.get("persona_id"),
                )
                response_text = result.response_text
            except Exception as exc:
                print(f"   Error: {exc}")
                response_text = f"(error: {exc})"

        # Build context from expected traits for grounding evaluators
        context = "; ".join(case.get("expected_traits", []))

        rows.append({
            "query": query,
            "response": response_text,
            "context": context,
        })
    return rows


def run_foundry_evaluation(
    dataset_rows: list[dict],
    prompt_name: str,
    model: str,
    dry_run: bool = False,
) -> dict | None:
    """Run azure-ai-evaluation evaluate() with Foundry built-in evaluators.

    When not in dry-run mode, results are uploaded to the Foundry portal
    and will appear under the Agent's Evaluation tab.
    """
    from azure.ai.evaluation import (
        evaluate,
        RelevanceEvaluator,
        CoherenceEvaluator,
        FluencyEvaluator,
        AzureOpenAIModelConfiguration,
    )

    # Write dataset to a temporary JSONL file
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    data_path = RESULTS_DIR / "foundry_eval_data.jsonl"
    with open(data_path, "w", encoding="utf-8") as f:
        for row in dataset_rows:
            f.write(json.dumps(row) + "\n")
    print(f"\nDataset written: {data_path} ({len(dataset_rows)} rows)")

    if dry_run:
        print("Dry-run mode — skipping Foundry evaluation upload.")
        return None

    # Azure OpenAI endpoint for the LLM judge
    base_endpoint = AZURE_EXISTING_AIPROJECT_ENDPOINT.split("/api/projects/")[0]

    # Get a bearer token for Azure OpenAI — works around a Python 3.11
    # compatibility issue with passing credential objects to the model config.
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default").token

    model_config = AzureOpenAIModelConfiguration(
        azure_deployment=model,
        azure_endpoint=base_endpoint,
        api_key=token,
    )

    # Set up built-in evaluators (LLM-as-judge)
    evaluators = {
        "relevance": RelevanceEvaluator(model_config),
        "coherence": CoherenceEvaluator(model_config),
        "fluency": FluencyEvaluator(model_config),
    }

    evaluation_name = f"prompt-release-{prompt_name}"

    print(f"\nRunning Foundry evaluation: {evaluation_name}")
    print(f"  Evaluators: {', '.join(evaluators.keys())}")
    print(f"  Judge model: {model}")
    print(f"  Uploading to: {AZURE_EXISTING_AIPROJECT_ENDPOINT}")

    eval_result = evaluate(
        data=str(data_path),
        evaluators=evaluators,
        evaluation_name=evaluation_name,
        azure_ai_project=AZURE_EXISTING_AIPROJECT_ENDPOINT,
        tags={
            "prompt_variant": prompt_name,
            "model": model,
            "pipeline": "prompt-release",
        },
    )

    # Save results locally
    result_path = RESULTS_DIR / "foundry_eval_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "evaluation_name": evaluation_name,
                "prompt_variant": prompt_name,
                "model": model,
                "metrics": dict(eval_result.get("metrics", {})),
            },
            f,
            indent=2,
            default=str,
        )
    print(f"\nResults saved: {result_path}")

    # Print summary
    metrics = eval_result.get("metrics", {})
    print("\n" + "=" * 50)
    print("FOUNDRY EVALUATION RESULTS")
    print("=" * 50)
    for name, value in metrics.items():
        print(f"  {name}: {value}")

    return eval_result


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Run Foundry portal evaluation (appears under Agent > Evaluation tab)."
    )
    parser.add_argument("--prompt", default="baseline", help="Prompt variant name.")
    parser.add_argument("--model", default=PRIMARY_MODEL, help="Model deployment for agent & judge.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate dataset only, no Foundry calls or upload.",
    )
    args = parser.parse_args()

    cases = load_eval_cases()
    print(f"Loaded {len(cases)} evaluation cases.")
    print(f"Prompt: {args.prompt} | Model: {args.model}")
    print("-" * 50)

    # Step 1: Generate agent responses
    dataset = build_eval_dataset(cases, args.prompt, args.model, args.dry_run)

    # Step 2: Run Foundry evaluation with built-in evaluators
    run_foundry_evaluation(dataset, args.prompt, args.model, args.dry_run)


if __name__ == "__main__":
    main()
