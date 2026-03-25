"""Governance checklist and guardrail explanations for the demo."""

from __future__ import annotations

from typing import Any


GOVERNANCE_CHECKLIST: list[dict[str, Any]] = [
    {
        "control": "Approved Prompts Only",
        "description": "Only prompts stored in the /prompts directory and validated by CI are used in production.",
        "scope": "local_demo",
        "enterprise_equivalent": "Prompt registry with approval workflow in Foundry.",
    },
    {
        "control": "Agent Versioning",
        "description": "Every change to the agent creates a new version. No overwriting of production agents.",
        "scope": "foundry",
        "enterprise_equivalent": "Foundry managed agent versioning with rollback capability.",
    },
    {
        "control": "Evaluation Before Promotion",
        "description": "Evaluation must pass a minimum quality threshold before a new version is promoted.",
        "scope": "local_demo",
        "enterprise_equivalent": "Quality gates in CI/CD pipeline with automated evaluation.",
    },
    {
        "control": "Least-Privilege Credentials",
        "description": "Service Principal with minimal required permissions. No shared secrets.",
        "scope": "foundry",
        "enterprise_equivalent": "Azure RBAC with Managed Identity and conditional access.",
    },
    {
        "control": "CI Validation on Every Push",
        "description": "GitHub Actions run tests, prompt validation, and smoke checks on every push.",
        "scope": "local_demo",
        "enterprise_equivalent": "Enterprise CI/CD with mandatory review gates.",
    },
    {
        "control": "Safety and Content Policy",
        "description": "Agent instructions prohibit hallucination, enforce grounding, and require factual responses.",
        "scope": "both",
        "enterprise_equivalent": "Azure AI Content Safety filters and responsible AI policies.",
    },
    {
        "control": "Audit Trail via Monitoring",
        "description": "Every invocation is logged with timestamp, model, prompt, persona, and result.",
        "scope": "local_demo",
        "enterprise_equivalent": "Foundry tracing, Azure Monitor, and Application Insights.",
    },
    {
        "control": "Change Control via Git",
        "description": "All prompt, code, and config changes tracked in Git with PR review.",
        "scope": "both",
        "enterprise_equivalent": "Branch policies, required reviews, and signed commits.",
    },
]


def get_governance_checklist() -> list[dict[str, Any]]:
    """Return the full governance checklist."""
    return GOVERNANCE_CHECKLIST


def get_presenter_governance_notes() -> str:
    """Return formatted presenter notes for the governance section."""
    lines = [
        "## Governance — What to Say in the Demo\n",
        "Key talking points:\n",
        "1. **Prompts are controlled assets** — not ad-hoc strings. They're versioned, validated, and approved.",
        "2. **Agent versions are immutable** — changes create new versions, never overwrite production.",
        "3. **Evaluation is mandatory** — no promotion without passing quality and safety thresholds.",
        "4. **Credentials follow least-privilege** — Service Principal with scoped permissions, never shared keys.",
        "5. **CI catches regressions** — every push validates prompts, runs tests, and optionally runs eval.",
        "6. **Safety is built in** — content policy, grounding requirements, and responsible AI guardrails.",
        "\nDistinguish for the audience:",
        "- **Local demo constructs**: prompt directory, heuristic eval, local monitoring log",
        "- **Enterprise Foundry features**: managed agent versioning, Azure RBAC, AI Content Safety, Foundry tracing",
        "- **Both**: Git-based change control, CI/CD automation, evaluation-gated promotion",
    ]
    return "\n".join(lines)
