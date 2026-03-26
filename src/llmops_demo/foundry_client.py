"""Foundry client wrapper.

Centralises the connection to Microsoft Foundry, credential handling, and
invocation of the agent via the OpenAI-compatible responses API.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

from llmops_demo.config import AZURE_EXISTING_AIPROJECT_ENDPOINT, AGENT_NAME

logger = logging.getLogger(__name__)


@dataclass
class InvocationResult:
    """Structured result from an agent invocation."""
    agent_name: str = ""
    model_name: str = ""
    version: str = ""
    prompt_variant: str = ""
    persona: str = ""
    response_text: str = ""
    status: str = "pending"
    elapsed_seconds: float = 0.0
    error: str = ""


def create_project_client() -> AIProjectClient:
    """Create and return an authenticated AIProjectClient."""
    logger.info("Creating AIProjectClient for endpoint: %s", AZURE_EXISTING_AIPROJECT_ENDPOINT)
    credential = DefaultAzureCredential()
    client = AIProjectClient(
        endpoint=AZURE_EXISTING_AIPROJECT_ENDPOINT,
        credential=credential,
    )
    logger.info("AIProjectClient created successfully.")
    return client


def get_openai_client(project_client: AIProjectClient):
    """Get an OpenAI-compatible client from the project client."""
    logger.info("Obtaining OpenAI-compatible client from project client.")
    return project_client.get_openai_client()


def create_prompt_agent_version(
    project_client: AIProjectClient,
    *,
    model: str,
    instructions: str,
    agent_name: str = AGENT_NAME,
) -> dict[str, Any]:
    """Create or update a PromptAgentDefinition in Foundry.

    Returns metadata dict about the created/updated agent.
    """
    logger.info("Creating/updating agent '%s' with model '%s'.", agent_name, model)
    try:
        agent_def = PromptAgentDefinition(
            model=model,
            instructions=instructions,
        )
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=agent_def,
            description=f"Retail Personalised Agent — model={model}",
        )
        meta = {
            "agent_name": agent_name,
            "model": model,
            "version": getattr(agent, "version", ""),
            "agent_id": getattr(agent, "name", ""),
            "status": "created",
        }
        logger.info("Agent created: %s", meta)
        return meta
    except Exception as exc:
        logger.error("Failed to create agent '%s': %s", agent_name, exc)
        return {
            "agent_name": agent_name,
            "model": model,
            "agent_id": "",
            "status": "error",
            "error": str(exc),
        }


def invoke_agent(
    project_client: AIProjectClient,
    *,
    user_message: str,
    model: str,
    agent_name: str = AGENT_NAME,
    prompt_variant: str = "baseline",
    persona: str = "",
    system_prompt: str = "",
) -> InvocationResult:
    """Invoke the Foundry Prompt Agent via the Responses API.

    Uses the OpenAI Responses API with ``store=True`` so that every call
    is recorded in the Foundry portal under the project's stored responses,
    making evaluation runs visible for tracing and monitoring.

    If a *system_prompt* override is supplied it takes precedence over the
    agent's stored instructions.
    """
    result = InvocationResult(
        agent_name=agent_name,
        model_name=model,
        prompt_variant=prompt_variant,
        persona=persona,
    )
    start = time.perf_counter()
    try:
        # Fetch agent definition to get stored instructions & model
        agent_details = project_client.agents.get(agent_name=agent_name)
        latest = agent_details.versions.get("latest", {})
        definition = latest.get("definition", {})
        agent_model = definition.get("model", model)
        agent_instructions = definition.get("instructions", "")

        effective_model = model or agent_model
        effective_system = system_prompt or agent_instructions

        openai_client = get_openai_client(project_client)

        # Use Responses API with store=True for Foundry portal visibility
        response = openai_client.responses.create(
            model=effective_model,
            instructions=effective_system or None,
            input=user_message,
            store=True,
            metadata={
                "agent_name": agent_name,
                "prompt_variant": prompt_variant,
                "persona": persona,
                "version": latest.get("version", ""),
            },
        )
        result.response_text = response.output_text or ""
        result.model_name = effective_model
        result.version = latest.get("version", "")
        result.status = "success"
        logger.info("Agent invocation succeeded for '%s' (response_id=%s).", agent_name, response.id)
    except Exception as exc:
        result.status = "error"
        result.error = str(exc)
        logger.error("Agent invocation failed: %s", exc)
    finally:
        result.elapsed_seconds = round(time.perf_counter() - start, 3)
    return result
