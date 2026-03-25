#!/usr/bin/env python3
"""Validate persona data and print persona summary."""

from __future__ import annotations

import json

from llmops_demo.logging_config import setup_logging
from llmops_demo.memory import load_personas, load_products


def main() -> None:
    setup_logging()

    print("=== Persona Summary ===\n")
    personas = load_personas()
    for p in personas:
        print(f"  {p['persona_id']}: {p['name']}")
        print(f"    Stores: {', '.join(p['store_preferences'])}")
        print(f"    Budget: {p['budget_band']}")
        print(f"    Categories: {', '.join(p['preferred_categories'])}")
        print(f"    Past purchases: {', '.join(p['past_purchases'])}")
        print()

    print("=== Product Summary ===\n")
    products = load_products()
    stores = {}
    for prod in products:
        stores.setdefault(prod["store"], []).append(prod)

    for store, items in sorted(stores.items()):
        print(f"  {store} ({len(items)} products):")
        for item in items:
            print(f"    - {item['name']} (${item['price_aud']:.2f})")
        print()

    print(f"Total personas: {len(personas)}")
    print(f"Total products: {len(products)}")
    print("Local memory data is valid and ready for demo.")


if __name__ == "__main__":
    main()
