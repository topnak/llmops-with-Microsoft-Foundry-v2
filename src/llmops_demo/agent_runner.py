"""Agent runner — high-level helpers to invoke the agent with prompt/persona."""

from __future__ import annotations

import logging

from llmops_demo.config import AGENT_NAME, PRIMARY_MODEL
from llmops_demo.foundry_client import (
    create_project_client,
    invoke_agent,
    InvocationResult,
)
from llmops_demo.prompt_manager import load_prompt
from llmops_demo.memory import inject_memory_into_prompt, get_persona, load_products

logger = logging.getLogger(__name__)


def run_query(
    user_input: str,
    *,
    prompt_name: str = "baseline",
    model: str = PRIMARY_MODEL,
    persona_id: str | None = None,
) -> InvocationResult:
    """Run a single query through the agent with optional persona context."""
    prompt_text = load_prompt(prompt_name)

    persona_label = ""
    if persona_id:
        persona = get_persona(persona_id)
        products = load_products()
        prompt_text = inject_memory_into_prompt(prompt_text, user_input, persona, products)
        persona_label = persona.get("name", persona_id)

    client = create_project_client()
    return invoke_agent(
        client,
        user_message=user_input,
        model=model,
        agent_name=AGENT_NAME,
        prompt_variant=prompt_name,
        persona=persona_label,
        system_prompt=prompt_text,
    )
