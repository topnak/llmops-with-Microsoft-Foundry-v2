# Microsoft Foundry LLMOps Demo — RetailPersonlisedAgent

A complete, demo-ready repository for a **20-minute guided walkthrough** of
**LLMOps on Microsoft Foundry NextGen**. It covers the full lifecycle: prompt
management, agent versioning, personalization, model comparison, evaluation,
monitoring, governance, and CI/CD automation.

---

## Demo Story

A retail organization needs an intelligent assistant that **personalizes retail
recommendations** across Australian brands:

- **Kmart** — value and everyday essentials
- **Officeworks** — productivity and tech
- **Bunnings** — DIY and outdoor

The LLMOps engineer walks through every stage of the AI lifecycle using
**Microsoft Foundry** and local tooling.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Streamlit Demo UI (app/demo_ui.py)                  │
│  ─ guided 10-step walkthrough with Next/Back         │
│  ─ triggers real Foundry calls or shows local data   │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│  Core Library (src/llmops_demo/)                     │
│  config · foundry_client · agent_manager · runner    │
│  prompt_manager · memory · model_compare             │
│  evaluation · monitoring · governance · reporting    │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│  Microsoft Foundry (managed agent hosting)           │
│  Agent: RetailPersonlisedAgent                       │
│  Model: gpt-4.1-mini (primary)                       │
│  Endpoint: https://llmops-foundry.services.ai.azure  │
│            .com/api/projects/llm-ops-foundry-demo     │
└──────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
├── .github/workflows/     # CI, eval, and Foundry smoke test
├── app/                   # Streamlit UI + demo step metadata
│   ├── demo_ui.py         # Main entry point
│   ├── pages.py           # Step renderers
│   └── assets/demo_steps.json
├── data/                  # Personas, products, eval cases, demo story
├── prompts/               # Versioned prompt variants
├── results/               # Runtime outputs (gitignored except .gitkeep)
├── scripts/               # CLI scripts for each LLMOps action
├── src/llmops_demo/       # Core Python library
├── tests/                 # pytest test suite
├── .env.example           # Required environment variables
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Prerequisites

- **Python 3.11+**
- An **Azure subscription** with a configured Microsoft Foundry project
- A **Service Principal** with access to the Foundry project
- The model deployment `gpt-4.1-mini` (and optionally `gpt-4.1`) available

---

## Local Setup

```bash
# 1. Clone the repo
git clone <repo-url> && cd llmops-foundry-nextgen-demo

# 2. Create virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Azure credentials and Foundry endpoint
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `AZURE_CLIENT_ID` | Service Principal client ID |
| `AZURE_CLIENT_SECRET` | Service Principal secret |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription |
| `AZURE_LOCATION` | Region (default: `australiaeast`) |
| `AZURE_EXISTING_AIPROJECT_ENDPOINT` | Foundry project endpoint |
| `PRIMARY_MODEL` | Default model (default: `gpt-4.1-mini`) |
| `COMPARISON_MODELS` | Comma-separated models for comparison |
| `LOG_LEVEL` | Logging level (default: `INFO`) |

---

## Create / Update Agent

```bash
python scripts/create_agent.py
# Optional: specify model
python scripts/create_agent.py --model gpt-4.1
```

Creates or updates **RetailPersonlisedAgent** in Microsoft Foundry.

---

## Run Streamlit UI

```bash
streamlit run app/demo_ui.py
```

The UI provides a guided 10-step walkthrough with **Next** and **Back**
navigation, presenter notes, and interactive actions for each LLMOps stage.

---

## Run Baseline Script

```bash
python scripts/run_baseline.py
# Custom query
python scripts/run_baseline.py --query "Recommend items for a DIY project"
```

---

## Compare Models

```bash
python scripts/compare_models.py
python scripts/compare_models.py --prompt quality_optimized --persona diy_customer
```

---

## Run Evaluation

```bash
# Dry run (no Foundry calls, heuristic scoring only)
python scripts/run_eval.py --dry-run

# Full evaluation
python scripts/run_eval.py --prompt baseline
```

Reports are saved to `results/eval_summary.json` and `results/eval_summary.md`.

---

## Additional Scripts

| Script | Purpose |
|--------|---------|
| `scripts/update_agent_version.py` | Create new agent version from a prompt variant |
| `scripts/export_demo_report.py` | Generate final presentation report |
| `scripts/seed_local_memory.py` | Validate and display persona/product data |

---

## GitHub Actions Automation

### Unified LLMOps Pipeline (`llmops-pipeline.yml`)

A connected 5-stage pipeline that runs on every push/PR to `main`:

```
┌──────────────────┐   ┌──────────────────┐   ┌────────────────┐   ┌─────────────────────┐   ┌──────────────────┐
│ 1. Unit Tests    │ → │ 2. Validate      │ → │ 3. Detect      │ → │ 4. Evaluate Quality │ → │ 5. Pipeline      │
│ (pytest 3.11+12) │   │ Prompts & Data   │   │ Prompt Changes │   │ (12×4 dimensions)   │   │ Report           │
└──────────────────┘   └──────────────────┘   └────────────────┘   └─────────────────────┘   └──────────────────┘
```

**Stage 4 scores each prompt on 4 quality dimensions:**

| Dimension | What it measures | Scale |
|-----------|-----------------|-------|
| **Relevance** | Does the response address the user's query? | 0–5 |
| **Personalization** | Does it use persona context (budget, preferences)? | 0–5 |
| **Grounding** | Does it recommend only approved catalogue products? | 0–5 |
| **Policy/Safety** | Does it follow safety and policy rules? | 0–5 |

### Other Workflows

| Workflow | Trigger | Purpose |
|----------|---------|--------|
| `ci.yml` | Push, PR, manual | Tests, prompt validation, data smoke check |
| `eval.yml` | Push to main, manual | Run evaluation, upload artifacts |
| `foundry-smoke.yml` | Manual only | Live Foundry connectivity validation |
| `prompt-change.yml` | Push to main | Targeted eval for changed prompt files |

---

## How This Maps to the Microsoft Foundry Demo Walkthrough

| Step | LLMOps Stage | Foundry Capability |
|------|-------------|-------------------|
| 1 | Introduction | Project Overview |
| 2 | Prompt Engineering | Prompt Versioning |
| 3 | Agent Versioning | Managed Agent Creation |
| 4 | Baseline Measurement | Agent Invocation |
| 5 | Context Injection | Memory / Context Management |
| 6 | Model Experimentation | Model Deployment Switching |
| 7 | Quality Measurement | Evaluation Framework |
| 8 | Observability | Tracing and Monitoring |
| 9 | Compliance and Safety | Governance Controls |
| 10 | CI/CD Automation | Pipeline Integration |

---

## Troubleshooting

### Authentication fails
- Verify `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, and `AZURE_TENANT_ID` in `.env`
- Ensure the Service Principal has access to the Foundry project
- Run `az login --service-principal` to test credentials independently
- Check that `DefaultAzureCredential` can resolve (`pip install azure-identity`)

### Agent creation fails
- Confirm the Foundry endpoint is reachable
- Verify the model deployment `gpt-4.1-mini` exists in the Foundry project
- Check Foundry project IAM — the Service Principal needs contributor access

### Model not found
- Model deployment names are case-sensitive
- Verify with Azure AI Studio that the deployment exists and is active

### Streamlit won't start
- Ensure you activated the virtual environment
- Ensure `streamlit` is installed: `pip install streamlit`
- Run from the repo root: `streamlit run app/demo_ui.py`

### Tests fail
- Run tests from repo root with `PYTHONPATH=src pytest tests/ -v`
- Tests do not require Foundry connectivity

---

## Suggested Presenter Talk Track

### Step 1 — Welcome (2 min)
> "Today we're walking through a day in the life of an LLMOps engineer using
> Microsoft Foundry. Our scenario: a retail org needs personalized
> recommendations across Kmart, Officeworks, and Bunnings."

### Step 2 — Prompt Management (2 min)
> "We treat prompts as versioned assets. Here are four variants with different
> goals: baseline, cost-optimized, quality-optimized, and grounded. Each change
> is tracked and validated in CI."

### Step 3 — Create Agent (2 min)
> "We create RetailPersonlisedAgent in Foundry. Versioning is non-destructive.
> Every change creates a new version we can roll back."

### Step 4 — Baseline Run (2 min)
> "Let's establish a baseline. No personalization yet — just the agent with the
> default prompt. Notice the generic response."

### Step 5 — Personalization (2 min)
> "Now we inject customer context. Watch how the response changes for a Budget
> Shopper vs a Premium Shopper. This is data + prompt + orchestration."

### Step 6 — Model Comparison (2 min)
> "We run the same scenario across different models and compare quality,
> latency, and style. This informs which model to promote."

### Step 7 — Evaluation (2 min)
> "Every change needs measurement. We score relevance, personalization,
> grounding, and policy safety against 12 test cases."

### Step 8 — Monitoring (2 min)
> "Every invocation is traced. In Foundry you get dashboards for latency,
> tokens, and errors. Here we show the local equivalent."

### Step 9 — Governance (2 min)
> "Governance is not optional. Approved prompts, evaluation gates, RBAC,
> and safety controls are all part of the loop."

### Step 10 — Automation (2 min)
> "Finally, GitHub Actions close the loop. Prompt changes trigger CI,
> evaluation runs automatically, and promotion is quality-gated. That's
> the complete LLMOps lifecycle. Thank you!"

---

## License

This repository is a demo asset. Adjust licensing as appropriate for your
organization.
