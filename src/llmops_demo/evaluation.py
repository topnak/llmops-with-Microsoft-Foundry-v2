"""Evaluation framework — heuristic scoring of agent responses."""

from __future__ import annotations

import json
import logging
from typing import Any

from llmops_demo.config import DATA_DIR, RESULTS_DIR
from llmops_demo.memory import load_products

logger = logging.getLogger(__name__)


def load_eval_cases() -> list[dict[str, Any]]:
    """Load evaluation cases from data/eval_cases.jsonl."""
    path = DATA_DIR / "eval_cases.jsonl"
    cases = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    logger.info("Loaded %d evaluation cases.", len(cases))
    return cases


def _score_relevance(response: str, case: dict) -> int:
    """Score 0-5 based on mention of expected traits."""
    traits = case.get("expected_traits", [])
    if not traits:
        return 3
    matches = sum(1 for t in traits if any(w.lower() in response.lower() for w in t.split()))
    return min(5, round(matches / len(traits) * 5))


def _score_personalization(response: str, case: dict) -> int:
    """Score 0-5 based on persona-aligned content."""
    persona_id = case.get("persona_id")
    if not persona_id:
        return 3  # neutral when no persona expected
    keywords = {
        "budget_shopper": ["budget", "affordable", "value", "kmart"],
        "premium_shopper": ["premium", "quality", "upgrade", "officeworks"],
        "diy_customer": ["diy", "project", "bunnings", "tool"],
        "office_worker": ["office", "desk", "productivity", "officeworks"],
        "seasonal_buyer": ["seasonal", "outdoor", "garden", "summer"],
    }
    kws = keywords.get(persona_id, [])
    if not kws:
        return 3
    hits = sum(1 for kw in kws if kw.lower() in response.lower())
    return min(5, round(hits / len(kws) * 5))


def _score_grounding(response: str, _case: dict) -> int:
    """Score 0-5 based on mention of known products/stores."""
    products = load_products()
    known_names = {p["name"].lower() for p in products}
    known_stores = {"kmart", "officeworks", "bunnings"}
    store_hits = sum(1 for s in known_stores if s in response.lower())
    product_hits = sum(1 for n in known_names if n.lower() in response.lower())
    return min(5, store_hits + product_hits)


def _score_policy_safety(response: str, case: dict) -> int:
    """Score 0-5 based on absence of prohibited behavior."""
    must_not_do = case.get("must_not_do", [])
    if not must_not_do:
        return 5
    violations = sum(1 for rule in must_not_do if any(w.lower() in response.lower() for w in rule.split()))
    return max(0, 5 - violations)


def score_response(response: str, case: dict) -> dict[str, int]:
    """Score a single response across all dimensions."""
    relevance = _score_relevance(response, case)
    personalization = _score_personalization(response, case)
    grounding = _score_grounding(response, case)
    policy_safety = _score_policy_safety(response, case)
    total = min(5, round((relevance + personalization + grounding + policy_safety) / 4))
    return {
        "relevance": relevance,
        "personalization": personalization,
        "grounding": grounding,
        "policy_safety": policy_safety,
        "total": total,
    }


def run_evaluation(responses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Score a list of {case, response_text} dicts.

    Each item should have 'case' (eval case dict) and 'response_text'.
    """
    results = []
    for item in responses:
        case = item["case"]
        text = item.get("response_text", "")
        scores = score_response(text, case)
        results.append({
            "id": case.get("id", ""),
            "user_input": case.get("user_input", ""),
            "persona_id": case.get("persona_id"),
            "scores": scores,
            "response_preview": text[:200],
        })
    return results


def generate_eval_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate evaluation results into a summary."""
    if not results:
        return {"count": 0, "averages": {}, "results": []}

    dims = ["relevance", "personalization", "grounding", "policy_safety", "total"]
    avgs = {}
    for dim in dims:
        values = [r["scores"][dim] for r in results]
        avgs[dim] = round(sum(values) / len(values), 2)

    return {
        "count": len(results),
        "averages": avgs,
        "results": results,
    }


def save_eval_reports(summary: dict[str, Any]) -> tuple[str, str]:
    """Save evaluation summary as JSON and Markdown to results/."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = RESULTS_DIR / "eval_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    md_lines = [
        "# Evaluation Summary\n",
        f"**Total cases**: {summary['count']}\n",
        "## Average Scores\n",
        "| Dimension | Score |",
        "|-----------|-------|",
    ]
    for dim, score in summary.get("averages", {}).items():
        md_lines.append(f"| {dim} | {score} |")

    md_lines.append("\n## Per-Case Results\n")
    md_lines.append("| ID | Relevance | Personal. | Grounding | Policy | Total |")
    md_lines.append("|----|-----------|-----------|-----------|--------|-------|")
    for r in summary.get("results", []):
        s = r["scores"]
        md_lines.append(
            f"| {r['id']} | {s['relevance']} | {s['personalization']} "
            f"| {s['grounding']} | {s['policy_safety']} | {s['total']} |"
        )

    md_path = RESULTS_DIR / "eval_summary.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    logger.info("Eval reports saved: %s, %s", json_path, md_path)
    return str(json_path), str(md_path)
