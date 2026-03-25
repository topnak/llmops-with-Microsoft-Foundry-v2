"""Configuration loader for the LLMOps demo.

Loads settings from environment variables (with .env support) and provides
sensible defaults for demo use.
"""

from __future__ import annotations

import os
import pathlib
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Paths -----------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
APP_ASSETS_DIR = PROJECT_ROOT / "app" / "assets"


def _require_env(name: str) -> str:
    """Return env var value or raise with a helpful message."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            f"Copy .env.example to .env and fill in the value."
        )
    return value


# Azure / Foundry --------------------------------------------------------------
AZURE_EXISTING_AIPROJECT_ENDPOINT: str = os.getenv(
    "AZURE_EXISTING_AIPROJECT_ENDPOINT",
    "https://llmops-foundry.services.ai.azure.com/api/projects/llm-ops-foundry-demo",
)

# Agent -----------------------------------------------------------------------
AGENT_NAME: str = "RetailPersonlisedAgent"

# Models ----------------------------------------------------------------------
PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "gpt-4.1-mini")
COMPARISON_MODELS: list[str] = [
    m.strip()
    for m in os.getenv("COMPARISON_MODELS", "gpt-4.1-mini,gpt-4.1").split(",")
    if m.strip()
]

# App -------------------------------------------------------------------------
APP_TITLE: str = "Microsoft Foundry LLMOps Demo"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# Sample queries ---------------------------------------------------------------
SAMPLE_QUERIES: list[str] = [
    "Recommend three products for a budget-conscious customer shopping at Kmart, including one upsell and one cross-sell.",
    "Suggest premium desk setup items for an Officeworks customer who already bought a monitor.",
    "Recommend two DIY items from Bunnings for a returning customer, but do not exceed a mid-range budget.",
    "If a requested product is not in the approved list, say so clearly and do not invent it.",
]

# Agent instructions -----------------------------------------------------------
AGENT_INSTRUCTIONS: str = (
    "You are a Retail Personalization Assistant for Australia. "
    "You support Kmart, Officeworks, and Bunnings.\n\n"
    "Your responsibilities:\n"
    "- personalize recommendations based on customer context and retail preferences\n"
    "- provide helpful retail suggestions grounded in the approved inventory and scenario context\n"
    "- suggest relevant upsell and cross-sell items when appropriate\n"
    "- avoid hallucinating products, pricing, stock levels, or policies\n"
    "- keep responses concise, practical, and suitable for retail operations use\n"
    "- if information is missing, say so clearly instead of inventing details\n"
    "- prefer safe, factual, and business-friendly responses"
)
