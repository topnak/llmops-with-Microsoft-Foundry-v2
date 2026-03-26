#!/usr/bin/env python3
"""Run cloud evaluation via the OpenAI Evals API on the Foundry project.

Uses the correct Foundry cloud evaluation API (client.evals.create +
client.evals.runs.create) so that results appear under the Agent's
Evaluation tab in the Microsoft Foundry portal.

Reference: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation

Supports two modes:
  Agent Target — sends queries to the RetailPersonlisedAgent at runtime and
                 evaluates its responses (default).
  Dataset      — evaluates pre-computed query+response pairs from a JSONL.

Usage:
    # Agent target evaluation (runs agent live, results appear under Agent)
    python scripts/foundry_eval.py --prompt aussie_mate

    # Dataset evaluation (pre-computed responses)
    python scripts/foundry_eval.py --prompt aussie_mate --mode dataset

    # Dry-run (just prints config, no Foundry calls)
    python scripts/foundry_eval.py --prompt aussie_mate --dry-run
"""

from __future__ import annotations

import argparse
import json
import time

from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
    SourceFileID,
)

from llmops_demo.logging_config import setup_logging
from llmops_demo.config import (
    AZURE_EXISTING_AIPROJECT_ENDPOINT,
    PRIMARY_MODEL,
    AGENT_NAME,
    RESULTS_DIR,
)
from llmops_demo.evaluation import load_eval_cases
from llmops_demo.foundry_client import create_project_client, get_openai_client


def run_agent_target_evaluation(
    client,
    cases: list[dict],
    prompt_name: str,
    model: str,
    agent_name: str,
) -> dict:
    """Run an Agent Target Evaluation via the cloud Evals API.

    Sends queries to the Foundry agent at runtime and evaluates its
    responses using built-in evaluators.  Results show under the agent's
    Evaluation tab in the Foundry portal.
    """
    # -- 1. Upload eval cases as a dataset ------------------------------------
    data_rows = []
    for case in cases:
        data_rows.append({
            "query": case["user_input"],
        })

    project_client = create_project_client()
    dataset_name = f"eval-{prompt_name}"
    data_path = RESULTS_DIR / "foundry_eval_data.jsonl"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        for row in data_rows:
            f.write(json.dumps(row) + "\n")

    print(f"Uploading dataset '{dataset_name}' ({len(data_rows)} rows)...")
    dataset = project_client.datasets.upload_file(
        name=dataset_name,
        version=str(int(time.time())),
        file_path=str(data_path),
    )
    data_id = dataset.id
    print(f"  Dataset uploaded: {data_id}")

    # -- 2. Define data schema -----------------------------------------------
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
        include_sample_schema=True,
    )

    # -- 3. Define built-in evaluators ----------------------------------------
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "coherence",
            "evaluator_name": "builtin.coherence",
            "initialization_parameters": {
                "deployment_name": model,
            },
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "relevance",
            "evaluator_name": "builtin.relevance",
            "initialization_parameters": {
                "deployment_name": model,
            },
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "fluency",
            "evaluator_name": "builtin.fluency",
            "initialization_parameters": {
                "deployment_name": model,
            },
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "violence",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
    ]

    # -- 4. Create evaluation -------------------------------------------------
    eval_name = f"prompt-release-{prompt_name}"
    print(f"\nCreating evaluation: {eval_name}")
    print(f"  Agent target: {agent_name}")
    print(f"  Judge model: {model}")
    print(f"  Evaluators: coherence, relevance, fluency, violence")

    eval_object = client.evals.create(
        name=eval_name,
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"  Eval created: {eval_object.id}")

    # -- 5. Create a run targeting the agent ----------------------------------
    input_messages = {
        "type": "template",
        "template": [
            {
                "type": "message",
                "role": "user",
                "content": {
                    "type": "input_text",
                    "text": "{{item.query}}",
                },
            }
        ],
    }

    target = {
        "type": "azure_ai_agent",
        "name": agent_name,
    }

    data_source = {
        "type": "azure_ai_target_completions",
        "source": {
            "type": "file_id",
            "id": data_id,
        },
        "input_messages": input_messages,
        "target": target,
    }

    run_name = f"{prompt_name}-run-{int(time.time())}"
    print(f"\nCreating eval run: {run_name}")
    eval_run = client.evals.runs.create(
        eval_id=eval_object.id,
        name=run_name,
        data_source=data_source,
    )
    print(f"  Run created: {eval_run.id}")

    # -- 6. Poll for completion -----------------------------------------------
    print("\nPolling for completion...")
    while True:
        run = client.evals.runs.retrieve(
            run_id=eval_run.id, eval_id=eval_object.id
        )
        if run.status in ("completed", "failed", "cancelled"):
            break
        print(f"  Status: {run.status} — waiting...")
        time.sleep(10)

    if run.status == "failed":
        print(f"\nEvaluation run FAILED: {run.error}")
        return {"status": "failed", "error": str(run.error)}

    # -- 7. Retrieve and display results --------------------------------------
    print(f"\nEvaluation run completed!")
    print(f"  Report URL: {getattr(run, 'report_url', 'N/A')}")

    output_items = list(
        client.evals.runs.output_items.list(
            run_id=run.id, eval_id=eval_object.id
        )
    )

    # Save results locally
    result_path = RESULTS_DIR / "foundry_eval_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "eval_id": eval_object.id,
                "run_id": run.id,
                "eval_name": eval_name,
                "prompt_variant": prompt_name,
                "agent_name": agent_name,
                "model": model,
                "status": run.status,
                "result_counts": getattr(run, "result_counts", None),
                "report_url": getattr(run, "report_url", None),
            },
            f,
            indent=2,
            default=str,
        )
    print(f"\nResults saved: {result_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("FOUNDRY CLOUD EVALUATION RESULTS")
    print("=" * 50)
    print(f"  Eval ID:  {eval_object.id}")
    print(f"  Run ID:   {run.id}")
    print(f"  Status:   {run.status}")
    result_counts = getattr(run, "result_counts", None)
    if result_counts:
        print(f"  Results:  {result_counts}")

    return {
        "eval_id": eval_object.id,
        "run_id": run.id,
        "status": run.status,
    }


def run_dataset_evaluation(
    client,
    project_client,
    cases: list[dict],
    prompt_name: str,
    model: str,
) -> dict:
    """Run a Dataset Evaluation with pre-computed responses.

    Invokes the agent locally, uploads query+response pairs, and runs
    built-in evaluators on the static data.
    """
    from llmops_demo.agent_runner import run_query

    # -- 1. Generate responses ------------------------------------------------
    data_rows = []
    for i, case in enumerate(cases, 1):
        query = case["user_input"]
        print(f"[{i}/{len(cases)}] {case['id']}: {query[:60]}...")
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
        data_rows.append({"query": query, "response": response_text})

    # -- 2. Upload dataset ----------------------------------------------------
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    data_path = RESULTS_DIR / "foundry_eval_data.jsonl"
    with open(data_path, "w", encoding="utf-8") as f:
        for row in data_rows:
            f.write(json.dumps(row) + "\n")

    dataset_name = f"eval-dataset-{prompt_name}"
    print(f"\nUploading dataset '{dataset_name}' ({len(data_rows)} rows)...")
    dataset = project_client.datasets.upload_file(
        name=dataset_name,
        version=str(int(time.time())),
        file_path=str(data_path),
    )
    data_id = dataset.id
    print(f"  Dataset uploaded: {data_id}")

    # -- 3. Define schema and evaluators --------------------------------------
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
            },
            "required": ["query", "response"],
        },
    )

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "coherence",
            "evaluator_name": "builtin.coherence",
            "initialization_parameters": {"deployment_name": model},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "relevance",
            "evaluator_name": "builtin.relevance",
            "initialization_parameters": {"deployment_name": model},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "fluency",
            "evaluator_name": "builtin.fluency",
            "initialization_parameters": {"deployment_name": model},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "violence",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
    ]

    # -- 4. Create eval and run -----------------------------------------------
    eval_name = f"dataset-eval-{prompt_name}"
    print(f"\nCreating dataset evaluation: {eval_name}")

    eval_object = client.evals.create(
        name=eval_name,
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )

    eval_run = client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"{prompt_name}-dataset-{int(time.time())}",
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileID(type="file_id", id=data_id),
        ),
    )

    # -- 5. Poll for completion -----------------------------------------------
    print("\nPolling for completion...")
    while True:
        run = client.evals.runs.retrieve(
            run_id=eval_run.id, eval_id=eval_object.id
        )
        if run.status in ("completed", "failed", "cancelled"):
            break
        print(f"  Status: {run.status} — waiting...")
        time.sleep(10)

    if run.status == "failed":
        print(f"\nEvaluation run FAILED: {run.error}")
        return {"status": "failed", "error": str(run.error)}

    print(f"\nEvaluation completed! Report: {getattr(run, 'report_url', 'N/A')}")

    # Save results
    result_path = RESULTS_DIR / "foundry_eval_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "eval_id": eval_object.id,
                "run_id": run.id,
                "eval_name": eval_name,
                "prompt_variant": prompt_name,
                "status": run.status,
                "report_url": getattr(run, "report_url", None),
            },
            f,
            indent=2,
            default=str,
        )
    print(f"Results saved: {result_path}")
    return {"eval_id": eval_object.id, "run_id": run.id, "status": run.status}


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Run Foundry cloud evaluation (appears under Agent > Evaluation tab)."
    )
    parser.add_argument("--prompt", default="baseline", help="Prompt variant name.")
    parser.add_argument("--model", default=PRIMARY_MODEL, help="Model deployment for judge.")
    parser.add_argument("--agent", default=AGENT_NAME, help="Foundry agent name.")
    parser.add_argument(
        "--mode",
        choices=["agent", "dataset"],
        default="agent",
        help="'agent' = send queries to agent at runtime; 'dataset' = pre-compute responses.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print config only, no Foundry calls.",
    )
    args = parser.parse_args()

    cases = load_eval_cases()
    print(f"Loaded {len(cases)} evaluation cases.")
    print(f"Prompt: {args.prompt} | Model: {args.model} | Mode: {args.mode}")
    print(f"Agent: {args.agent}")
    print("-" * 50)

    if args.dry_run:
        print("Dry-run mode — no Foundry calls will be made.")
        return

    project_client = create_project_client()
    client = get_openai_client(project_client)

    if args.mode == "agent":
        run_agent_target_evaluation(
            client, cases, args.prompt, args.model, args.agent,
        )
    else:
        run_dataset_evaluation(
            client, project_client, cases, args.prompt, args.model,
        )


if __name__ == "__main__":
    main()
