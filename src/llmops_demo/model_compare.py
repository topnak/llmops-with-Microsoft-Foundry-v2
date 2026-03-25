"""Multi-model comparison for the LLMOps optimization loop."""

from __future__ import annotations

import logging
from typing import Any

from llmops_demo.config import COMPARISON_MODELS, PRIMARY_MODEL
from llmops_demo.agent_runner import run_query
from llmops_demo.foundry_client import InvocationResult

logger = logging.getLogger(__name__)


def compare_models(
    user_input: str,
    prompt_name: str = "baseline",
    persona_id: str | None = None,
    models: list[str] | None = None,
) -> dict[str, Any]:
    """Run the same scenario across multiple model configurations.

    Returns a comparison summary dict.
    """
    models = models or COMPARISON_MODELS
    logger.info("Comparing models %s for prompt '%s'.", models, prompt_name)

    results: list[dict[str, Any]] = []
    for model in models:
        logger.info("Running model: %s", model)
        try:
            inv: InvocationResult = run_query(
                user_input,
                prompt_name=prompt_name,
                model=model,
                persona_id=persona_id,
            )
            results.append({
                "model": model,
                "prompt_variant": prompt_name,
                "persona": inv.persona,
                "status": inv.status,
                "response_text": inv.response_text,
                "elapsed_seconds": inv.elapsed_seconds,
                "error": inv.error,
            })
        except Exception as exc:
            logger.error("Model '%s' failed: %s", model, exc)
            results.append({
                "model": model,
                "prompt_variant": prompt_name,
                "persona": persona_id or "",
                "status": "error",
                "response_text": "",
                "elapsed_seconds": 0.0,
                "error": str(exc),
            })

    return {
        "user_input": user_input,
        "prompt_variant": prompt_name,
        "persona_id": persona_id,
        "comparisons": results,
    }
