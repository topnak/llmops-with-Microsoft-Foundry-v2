"""Prompt management — load, list, validate, and version prompts."""

from __future__ import annotations

import hashlib
import logging
import pathlib

from llmops_demo.config import PROMPTS_DIR

logger = logging.getLogger(__name__)


def list_prompts() -> list[str]:
    """Return sorted list of prompt variant names (without extension)."""
    return sorted(p.stem for p in PROMPTS_DIR.glob("*.txt"))


def load_prompt(name: str) -> str:
    """Load prompt text by variant name. Raises FileNotFoundError if missing."""
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt variant '{name}' not found at {path}")
    text = path.read_text(encoding="utf-8").strip()
    logger.debug("Loaded prompt '%s' (%d chars).", name, len(text))
    return text


def validate_prompt(name: str) -> tuple[bool, list[str]]:
    """Validate a prompt variant. Returns (is_valid, list_of_issues)."""
    issues: list[str] = []
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        return False, [f"File not found: {path}"]

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        issues.append("Prompt file is empty.")
    if len(text) < 20:
        issues.append("Prompt is very short (< 20 chars). May not be meaningful.")
    if len(text) > 10_000:
        issues.append("Prompt exceeds 10 000 chars. Consider trimming.")

    return len(issues) == 0, issues


def prompt_checksum(name: str) -> str:
    """Return a SHA-256 checksum of the prompt content for versioning."""
    text = load_prompt(name)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def all_prompt_checksums() -> dict[str, str]:
    """Return checksums for every prompt variant."""
    return {name: prompt_checksum(name) for name in list_prompts()}
