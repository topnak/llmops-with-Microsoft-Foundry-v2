"""Tests for evaluation module."""

import pytest
from llmops_demo.evaluation import (
    load_eval_cases, score_response, run_evaluation, generate_eval_summary,
)


def test_load_eval_cases():
    cases = load_eval_cases()
    assert len(cases) >= 10
    assert all("id" in c for c in cases)
    assert all("user_input" in c for c in cases)


def test_score_response_basic():
    case = {
        "expected_traits": ["mentions Kmart", "affordable"],
        "persona_id": "budget_shopper",
        "must_not_do": ["recommend premium"],
    }
    response = "Here are some affordable Kmart items for your budget."
    scores = score_response(response, case)
    assert "relevance" in scores
    assert "personalization" in scores
    assert "grounding" in scores
    assert "policy_safety" in scores
    assert "total" in scores
    assert all(0 <= v <= 5 for v in scores.values())


def test_score_empty_response():
    case = {
        "expected_traits": ["mentions Kmart"],
        "persona_id": None,
        "must_not_do": [],
    }
    scores = score_response("", case)
    assert scores["relevance"] == 0
    assert scores["policy_safety"] == 5  # no violations in empty response


def test_run_evaluation_and_summary():
    cases = load_eval_cases()[:3]
    responses = [
        {"case": c, "response_text": "Kmart has affordable items for budget shoppers at Bunnings."}
        for c in cases
    ]
    results = run_evaluation(responses)
    assert len(results) == 3

    summary = generate_eval_summary(results)
    assert summary["count"] == 3
    assert "averages" in summary
    assert "relevance" in summary["averages"]
