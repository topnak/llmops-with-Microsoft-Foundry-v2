"""Tests for demo story and step metadata."""

import pytest
from llmops_demo.utils import load_demo_story, load_demo_steps


def test_demo_story_has_stages():
    story = load_demo_story()
    assert story["agent_name"] == "RetailPersonlisedAgent"
    assert story["primary_model"] == "gpt-4.1-mini"
    assert len(story["stages"]) == 10


def test_demo_steps_count():
    steps = load_demo_steps()
    assert len(steps) == 13


def test_demo_steps_have_required_fields():
    steps = load_demo_steps()
    required = {"step_number", "title", "llmops_stage", "foundry_capability",
                "speaker_note", "action_label", "expected_output", "fallback_note"}
    for s in steps:
        assert required.issubset(s.keys()), f"Missing fields in step {s.get('step_number')}"


def test_demo_steps_sequential():
    steps = load_demo_steps()
    numbers = [s["step_number"] for s in steps]
    assert numbers == list(range(1, 14))


def test_demo_story_brands():
    story = load_demo_story()
    assert set(story["brands"]) == {"Kmart", "Officeworks", "Bunnings"}
