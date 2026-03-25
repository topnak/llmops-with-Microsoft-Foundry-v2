"""General utilities for the LLMOps demo."""

from __future__ import annotations

import json
from typing import Any

from llmops_demo.config import DATA_DIR, APP_ASSETS_DIR


def load_demo_story() -> dict[str, Any]:
    """Load the demo story metadata."""
    path = DATA_DIR / "demo_story.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_demo_steps() -> list[dict[str, Any]]:
    """Load the demo walkthrough steps for the UI."""
    path = APP_ASSETS_DIR / "demo_steps.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def truncate(text: str, max_len: int = 300) -> str:
    """Truncate text with ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."
