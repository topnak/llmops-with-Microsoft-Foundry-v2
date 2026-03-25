"""Persona memory and product context management."""

from __future__ import annotations

import json
import logging
from typing import Any

from llmops_demo.config import DATA_DIR

logger = logging.getLogger(__name__)


def load_personas() -> list[dict[str, Any]]:
    """Load all personas from data/personas.json."""
    path = DATA_DIR / "personas.json"
    with open(path, encoding="utf-8") as f:
        personas = json.load(f)
    logger.debug("Loaded %d personas.", len(personas))
    return personas


def get_persona(persona_id: str) -> dict[str, Any]:
    """Return a single persona by ID. Raises ValueError if not found."""
    for p in load_personas():
        if p["persona_id"] == persona_id:
            return p
    raise ValueError(f"Persona '{persona_id}' not found.")


def load_products() -> list[dict[str, Any]]:
    """Load all products from data/products.json."""
    path = DATA_DIR / "products.json"
    with open(path, encoding="utf-8") as f:
        products = json.load(f)
    logger.debug("Loaded %d products.", len(products))
    return products


def get_products_for_store(store: str) -> list[dict[str, Any]]:
    """Filter products by store name (case-insensitive)."""
    return [p for p in load_products() if p["store"].lower() == store.lower()]


def inject_memory_into_prompt(
    prompt_text: str,
    user_input: str,
    persona: dict[str, Any],
    product_context: list[dict[str, Any]],
) -> str:
    """Combine prompt, persona context, and product catalog into an enriched system prompt."""
    # Build persona section
    persona_section = (
        f"\n\n--- CUSTOMER PERSONA ---\n"
        f"Name: {persona.get('name', 'Unknown')}\n"
        f"Budget band: {persona.get('budget_band', 'unknown')}\n"
        f"Store preferences: {', '.join(persona.get('store_preferences', []))}\n"
        f"Preferred categories: {', '.join(persona.get('preferred_categories', []))}\n"
        f"Past purchases: {', '.join(persona.get('past_purchases', []))}\n"
        f"Upsell tolerance: {persona.get('upsell_tolerance', 'unknown')}\n"
        f"Cross-sell interest: {persona.get('cross_sell_interest', 'unknown')}\n"
        f"Notes: {persona.get('notes', '')}\n"
        f"--- END PERSONA ---"
    )

    # Build product catalog section (limit to relevant stores)
    stores = {s.lower() for s in persona.get("store_preferences", [])}
    relevant = [p for p in product_context if p["store"].lower() in stores] if stores else product_context
    product_lines = []
    for p in relevant:
        product_lines.append(
            f"- [{p['store']}] {p['name']} | ${p['price_aud']:.2f} | {', '.join(p.get('tags', []))}"
        )
    product_section = (
        "\n\n--- APPROVED PRODUCT CATALOG ---\n"
        + "\n".join(product_lines)
        + "\n--- END CATALOG ---"
    )

    return prompt_text + persona_section + product_section
