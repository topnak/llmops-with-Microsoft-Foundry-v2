"""Agent lifecycle management — create, version, and describe agents."""

from __future__ import annotations

import logging
from typing import Any

from llmops_demo.config import AGENT_NAME, PRIMARY_MODEL, AGENT_INSTRUCTIONS
from llmops_demo.foundry_client import create_project_client, create_prompt_agent_version
from llmops_demo.prompt_manager import load_prompt

logger = logging.getLogger(__name__)


def create_or_update_agent(
    model: str = PRIMARY_MODEL,
    instructions: str | None = None,
) -> dict[str, Any]:
    """Create or update RetailPersonlisedAgent in Foundry."""
    instructions = instructions or AGENT_INSTRUCTIONS
    client = create_project_client()
    return create_prompt_agent_version(
        client,
        model=model,
        instructions=instructions,
        agent_name=AGENT_NAME,
    )


def create_agent_version_from_prompt(
    prompt_name: str,
    model_name: str = PRIMARY_MODEL,
) -> dict[str, Any]:
    """Create a new agent version using a specific prompt variant."""
    prompt_text = load_prompt(prompt_name)
    logger.info(
        "Creating agent version from prompt '%s' with model '%s'.",
        prompt_name, model_name,
    )
    return create_or_update_agent(model=model_name, instructions=prompt_text)


def get_agent_reference_payload() -> dict[str, str]:
    """Return the agent_reference payload for OpenAI-compatible calls."""
    return {
        "name": AGENT_NAME,
        "type": "agent_reference",
    }
