"""Tests for config module."""

import os
import pytest


def test_config_loads_defaults():
    from llmops_demo.config import (
        AGENT_NAME, PRIMARY_MODEL, COMPARISON_MODELS,
        APP_TITLE, PROMPTS_DIR, DATA_DIR, RESULTS_DIR,
    )
    assert AGENT_NAME == "RetailPersonlisedAgent"
    assert PRIMARY_MODEL == "gpt-4.1-mini"
    assert isinstance(COMPARISON_MODELS, list)
    assert len(COMPARISON_MODELS) >= 1
    assert APP_TITLE == "Microsoft Foundry LLMOps Demo"
    assert PROMPTS_DIR.exists()
    assert DATA_DIR.exists()


def test_sample_queries_populated():
    from llmops_demo.config import SAMPLE_QUERIES
    assert len(SAMPLE_QUERIES) >= 4
    assert all(isinstance(q, str) for q in SAMPLE_QUERIES)


def test_agent_instructions_not_empty():
    from llmops_demo.config import AGENT_INSTRUCTIONS
    assert len(AGENT_INSTRUCTIONS) > 50
    assert "Kmart" in AGENT_INSTRUCTIONS
