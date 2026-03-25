"""Tests for memory module."""

import pytest
from llmops_demo.memory import (
    load_personas, get_persona, load_products,
    get_products_for_store, inject_memory_into_prompt,
)


def test_load_personas_count():
    personas = load_personas()
    assert len(personas) == 5


def test_personas_have_required_fields():
    personas = load_personas()
    required = {"persona_id", "name", "store_preferences", "budget_band",
                "preferred_categories", "past_purchases", "upsell_tolerance",
                "cross_sell_interest", "notes"}
    for p in personas:
        assert required.issubset(p.keys()), f"Missing fields in {p['persona_id']}"


def test_get_persona_budget():
    p = get_persona("budget_shopper")
    assert p["name"] == "Budget Shopper"
    assert p["budget_band"] == "low"


def test_get_persona_not_found():
    with pytest.raises(ValueError):
        get_persona("nonexistent_id")


def test_load_products():
    products = load_products()
    assert len(products) >= 12
    stores = {p["store"] for p in products}
    assert "Kmart" in stores
    assert "Officeworks" in stores
    assert "Bunnings" in stores


def test_get_products_for_store():
    kmart = get_products_for_store("Kmart")
    assert len(kmart) >= 3
    assert all(p["store"] == "Kmart" for p in kmart)


def test_inject_memory_into_prompt():
    prompt = "You are a retail assistant."
    persona = get_persona("budget_shopper")
    products = load_products()
    enriched = inject_memory_into_prompt(prompt, "test query", persona, products)
    assert "CUSTOMER PERSONA" in enriched
    assert "Budget Shopper" in enriched
    assert "APPROVED PRODUCT CATALOG" in enriched
    assert len(enriched) > len(prompt)
