#!/usr/bin/env python3
"""Quick setup verification — run this after setting up your .env file."""

from __future__ import annotations

import sys
import os

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def main() -> None:
    checks = []

    # 1. Python version
    v = sys.version_info
    ok = v >= (3, 11)
    checks.append(("Python >= 3.11", ok, f"{v.major}.{v.minor}.{v.micro}"))

    # 2. Required packages
    for pkg in ["streamlit", "azure.identity", "azure.ai.projects", "openai", "dotenv"]:
        try:
            __import__(pkg)
            checks.append((f"Package: {pkg}", True, "installed"))
        except ImportError:
            checks.append((f"Package: {pkg}", False, "MISSING - run: pip install -r requirements.txt"))

    # 3. .env file exists
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_exists = os.path.isfile(env_path)
    checks.append((".env file", env_exists, "found" if env_exists else "MISSING - copy .env.example to .env"))

    # 4. Config loads
    try:
        from llmops_demo.config import AZURE_EXISTING_AIPROJECT_ENDPOINT, PRIMARY_MODEL, AGENT_NAME
        checks.append(("Config loads", True, f"endpoint={AZURE_EXISTING_AIPROJECT_ENDPOINT[:40]}..."))
        checks.append(("Primary model", True, PRIMARY_MODEL))
        checks.append(("Agent name", True, AGENT_NAME))
    except Exception as exc:
        checks.append(("Config loads", False, str(exc)))

    # 5. Prompts
    try:
        from llmops_demo.prompt_manager import list_prompts
        prompts = list_prompts()
        checks.append(("Prompt files", len(prompts) >= 4, f"{len(prompts)} prompts found"))
    except Exception as exc:
        checks.append(("Prompt files", False, str(exc)))

    # 6. Data files
    try:
        from llmops_demo.memory import load_personas, load_products
        personas = load_personas()
        products = load_products()
        checks.append(("Personas", len(personas) == 5, f"{len(personas)} personas"))
        checks.append(("Products", len(products) >= 12, f"{len(products)} products"))
    except Exception as exc:
        checks.append(("Data files", False, str(exc)))

    # 7. Tests directory
    tests_dir = os.path.join(os.path.dirname(__file__), "..", "tests")
    test_files = [f for f in os.listdir(tests_dir) if f.startswith("test_")] if os.path.isdir(tests_dir) else []
    checks.append(("Test files", len(test_files) > 0, f"{len(test_files)} test files"))

    # Print results
    print()
    print("=" * 60)
    print("  LLMOps Developer Setup Verification")
    print("=" * 60)
    print()

    passed = 0
    failed = 0
    for name, ok, detail in checks:
        icon = "[PASS]" if ok else "[FAIL]"
        print(f"  {icon} {name}: {detail}")
        if ok:
            passed += 1
        else:
            failed += 1

    print()
    print("-" * 60)
    if failed == 0:
        print(f"  All {passed} checks passed! You're ready to start.")
        print("  Next: Open developer-experience/LAB_GUIDE.md")
    else:
        print(f"  {passed} passed, {failed} failed. Fix the issues above.")
    print()


if __name__ == "__main__":
    main()
