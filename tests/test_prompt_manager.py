"""Tests for prompt_manager module."""

import pytest
from llmops_demo.prompt_manager import list_prompts, load_prompt, validate_prompt, prompt_checksum


def test_list_prompts_returns_all():
    prompts = list_prompts()
    assert "baseline" in prompts
    assert "cost_optimized" in prompts
    assert "quality_optimized" in prompts
    assert "grounded_retail" in prompts


def test_load_prompt_baseline():
    text = load_prompt("baseline")
    assert len(text) > 20
    assert "Retail" in text or "retail" in text


def test_load_prompt_not_found():
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent_prompt")


def test_validate_prompt_baseline():
    is_valid, issues = validate_prompt("baseline")
    assert is_valid is True
    assert len(issues) == 0


def test_validate_prompt_nonexistent():
    is_valid, issues = validate_prompt("does_not_exist")
    assert is_valid is False
    assert len(issues) > 0


def test_prompt_checksum_consistent():
    c1 = prompt_checksum("baseline")
    c2 = prompt_checksum("baseline")
    assert c1 == c2
    assert len(c1) == 64  # SHA-256 hex


def test_prompt_checksums_differ():
    c_baseline = prompt_checksum("baseline")
    c_cost = prompt_checksum("cost_optimized")
    assert c_baseline != c_cost
