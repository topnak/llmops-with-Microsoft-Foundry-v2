# Microsoft Foundry LLMOps Demo — Scenario & Architecture

## 1. Demo Overview

This repository is a **20-minute guided demo** that simulates a day in the life
of an **LLMOps engineer** using **Microsoft Foundry** (Azure AI Foundry NextGen v2).

### The Business Scenario

A retail organization wants an **intelligent assistant** that can personalise
product recommendations across Australian brands:

| Brand | Category |
|---|---|
| **Kmart** | Budget retail, homewares, clothing |
| **Officeworks** | Office supplies, technology |
| **Bunnings** | Hardware, DIY, garden |

The agent — **RetailPersonlisedAgent** — must:

- Recommend products based on customer persona and preferences
- Stay grounded in an approved product catalogue (no hallucinations)
- Adapt tone and suggestions for different budget bands
- Be evaluated, monitored, and governed through a repeatable LLMOps loop

### Why LLMOps?

Traditional software ships code. AI-powered applications ship **prompts + models + data + orchestration**. LLMOps applies engineering discipline to every artifact:

```
Prompt Management → Agent Versioning → Testing → Evaluation → Monitoring → Governance → CI/CD
```

### Does This Demo Connect to Microsoft Foundry?

**Yes — the demo is live-connected to Microsoft Foundry.**

| Capability | Connection |
|---|---|
| **Authentication** | Service Principal (`DefaultAzureCredential`) via `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID` stored in `.env` |
| **Project** | `llm-ops-foundry-demo` on `llmops-foundry.services.ai.azure.com` (Australia East) |
| **Agent Creation** | `AIProjectClient.agents.create_version()` — creates/updates `RetailPersonlisedAgent` in Foundry |
| **Model Invocation** | `project_client.get_openai_client()` → standard `chat.completions.create()` using `gpt-4.1-mini` |
| **Model Comparison** | Live calls to multiple deployed models (e.g. `gpt-4.1-mini`, `gpt-4.1`, `retail-mini`) |
| **RBAC** | Service principal assigned `Azure AI User` role at resource + project scope |

Steps 1, 2, 7 (dry run), 8, 9, 10 can run **offline** (local data only).
Steps 3, 4, 5, 6, 7 (live run) require a **live Foundry connection**.

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app/)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ demo_ui  │→ │ pages.py │→ │ assets/  │  │ assets/  │           │
│  │  .py     │  │ (10 step │  │ style.css│  │demo_steps│           │
│  │ (nav)    │  │ renderers│  │          │  │  .json   │           │
│  └────┬─────┘  └────┬─────┘  └──────────┘  └──────────┘           │
│       │              │                                              │
└───────┼──────────────┼──────────────────────────────────────────────┘
        │              │
        ▼              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   Core Library (src/llmops_demo/)                    │
│                                                                      │
│  config.py ─────── loads .env, exposes settings                      │
│  foundry_client.py  creates AIProjectClient, OpenAI client           │
│  agent_manager.py ─ create/version agent in Foundry                  │
│  agent_runner.py ── invoke agent, return structured RunResult        │
│  prompt_manager.py  list / load / validate / checksum prompts        │
│  memory.py ──────── personas, products, inject context               │
│  model_compare.py ─ compare multiple models side-by-side             │
│  evaluation.py ──── score responses on 4 dimensions                  │
│  monitoring.py ──── local event log (mirrors Foundry tracing)        │
│  governance.py ──── checklist of controls                            │
│  reporting.py ───── export results to Markdown                       │
│  utils.py ───────── load demo_story.json / demo_steps.json           │
│                                                                      │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  Microsoft Foundry (Azure)                           │
│                                                                      │
│  ┌──────────────────┐   ┌───────────────────────────────┐            │
│  │ Foundry Project   │   │ Model Deployments              │           │
│  │ llm-ops-foundry-  │   │  • gpt-4.1-mini (primary)     │           │
│  │ demo              │   │  • gpt-4.1                     │           │
│  │                   │   │  • retail-mini                  │           │
│  │ Agent:            │   │  • text-embedding-3-small       │           │
│  │ RetailPersonlised │   └───────────────────────────────┘            │
│  │ Agent  (v1, v2…)  │                                                │
│  └──────────────────┘                                                │
│                                                                      │
│  Authentication: Service Principal → DefaultAzureCredential          │
│  RBAC: Azure AI User at resource + project scope                     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

Data Layer (local files):
  data/personas.json ── 5 customer personas
  data/products.json ── 17 products across 3 brands
  data/demo_story.json  10-step narrative
  data/eval_cases.jsonl  12 evaluation test cases
  prompts/*.txt ──────── 4 prompt variants
  results/ ───────────── outputs, eval reports, monitoring log
```

---

## 3. How Each Menu Works

### Step 1 — Intro / Scenario

| | |
|---|---|
| **Purpose** | Set the scene: what is the retail challenge and why does LLMOps matter |
| **Foundry connection** | None (informational) |
| **What happens** | Displays the agent name, primary model, number of steps, and project name. Presenter note explains talking points. |
| **User interaction** | Read-only overview |

### Step 2 — Prompt Management

| | |
|---|---|
| **Purpose** | Show that prompts are versioned assets, not ad-hoc strings |
| **Foundry connection** | None (local files) |
| **What happens** | Lists all prompt variants from `prompts/` directory. User selects one; the app loads, validates, and displays it. Checksums are computed to prove version integrity. |
| **User interaction** | Dropdown to select prompt → view content + validation result |
| **Prompt variants** | `baseline.txt`, `cost_optimized.txt`, `quality_optimized.txt`, `grounded_retail.txt` |

### Step 3 — Create / Update Agent in Foundry

| | |
|---|---|
| **Purpose** | Demonstrate managed agent creation and versioning |
| **Foundry connection** | **Live** — calls `AIProjectClient.agents.create_version()` |
| **What happens** | Clicking "Create or Update Agent" authenticates to Foundry, creates a new version of `RetailPersonlisedAgent` with a `PromptAgentDefinition`. Returns agent metadata (name, version, model, status). |
| **User interaction** | Button → spinner → success/error result |

### Step 4 — Baseline Run

| | |
|---|---|
| **Purpose** | Establish a baseline: agent response with no persona context |
| **Foundry connection** | **Live** — calls the agent via OpenAI chat completions |
| **What happens** | User picks a sample query (or types a custom one). The app sends it to the agent using the baseline prompt and `gpt-4.1-mini`. The raw response is displayed along with metadata (model, latency, etc.). The event is logged to local monitoring. |
| **User interaction** | Select/type query → "Run Baseline" button → view response |

### Step 5 — Persona Personalization

| | |
|---|---|
| **Purpose** | Show how persona context changes agent behavior |
| **Foundry connection** | **Live** — same invocation path as Step 4, but with persona injected |
| **What happens** | User selects a persona (e.g. "Budget Shopper" or "DIY Customer") and a prompt variant. The persona's preferences, budget band, and past purchases are injected into the prompt. The response is noticeably different from the baseline. |
| **User interaction** | Select persona + prompt + query → "Run with Persona" → compare response |

### Step 6 — Multi-Model Comparison

| | |
|---|---|
| **Purpose** | Compare quality, cost, and latency across models |
| **Foundry connection** | **Live** — parallel calls to multiple model deployments |
| **What happens** | The same query is sent to every model in `COMPARISON_MODELS` (e.g. `gpt-4.1-mini`, `gpt-4.1`). Results are displayed side-by-side with latency metrics. |
| **User interaction** | Select query + prompt → "Compare Models" → side-by-side cards |

### Step 7 — Evaluation

| | |
|---|---|
| **Purpose** | Measure agent quality with structured scoring |
| **Foundry connection** | Optional — supports **dry run** (no Foundry) or **live run** |
| **What happens** | Loads 12 evaluation cases from `data/eval_cases.jsonl`. Each case has an expected dimension profile. The evaluator scores responses on 4 dimensions: **relevance**, **personalization**, **grounding**, **policy/safety**. Averages and per-case results are displayed. Reports saved to `results/`. |
| **User interaction** | Select prompt + dry-run toggle → "Run Evaluation" → scores table |

### Step 8 — Monitoring and Traces

| | |
|---|---|
| **Purpose** | Show what observability looks like in production |
| **Foundry connection** | None (reads local monitoring log) |
| **What happens** | Displays all events recorded during the session: total events, success count, average latency, and a full event log table. Explains how this maps to Foundry's built-in tracing, Azure Monitor, and Application Insights. |
| **User interaction** | Read-only dashboard. Run earlier steps to populate data. |

### Step 9 — Governance and Guardrails

| | |
|---|---|
| **Purpose** | Demonstrate controls that keep AI safe and compliant |
| **Foundry connection** | None (local governance checklist) |
| **What happens** | Presents a checklist of governance controls, each tagged as "Local Demo", "Foundry / Enterprise", or "Both". Includes approved prompts, agent versioning, evaluation gates, RBAC, and safety expectations. Presenter notes provide talking points. |
| **User interaction** | Expand each control for details |

### Step 10 — GitHub Actions / Automation

| | |
|---|---|
| **Purpose** | Show how CI/CD closes the LLMOps loop |
| **Foundry connection** | None (reads workflow YAML files) |
| **What happens** | Displays the unified **LLMOps Pipeline** (`llmops-pipeline.yml`) with its 5 connected stages: (1) Unit Tests on Python 3.11+3.12, (2) Validate Prompts & Data Integrity, (3) Detect Prompt Changes via git diff, (4) Evaluate Quality — 12 eval cases scored on 4 dimensions (relevance, personalization, grounding, policy/safety), (5) Pipeline Report with summary table. Also shows individual workflows (`ci.yml`, `eval.yml`, `foundry-smoke.yml`). Ends with a "LLMOps loop complete" celebration. |
| **User interaction** | Expand each workflow to view YAML |

---

## 4. Overall Workflow

The demo follows a linear progression that mirrors the **LLMOps lifecycle**:

```
 ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
 │  DESIGN │ →  │  BUILD  │ →  │ TEST &  │ →  │ OPERATE │ →  │  GOVERN │
 │         │    │         │    │ EVALUATE│    │         │    │ & AUTO  │
 └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
   Step 1          Step 2         Step 4         Step 8         Step 9
   Step 2          Step 3         Step 5         Step 8         Step 10
                                  Step 6
                                  Step 7
```

Each step builds on the previous one — the agent created in Step 3 is invoked in
Steps 4-6, the events from those invocations appear in Step 8, and the governance
controls in Step 9 reference the prompt management from Step 2 and the evaluation
gates from Step 7.

---

## 5. File Structure Quick Reference

| Path | Purpose |
|---|---|
| `app/demo_ui.py` | Streamlit entry point, navigation, CSS loader |
| `app/pages.py` | 10 step renderers with secret redaction |
| `app/assets/style.css` | Premium stylesheet (Inter font, Microsoft blue) |
| `app/assets/demo_steps.json` | Step metadata (title, LLMOps stage, Foundry capability) |
| `src/llmops_demo/` | Core library (13 modules) |
| `data/` | Personas, products, eval cases, demo story |
| `prompts/` | 4 prompt variants |
| `scripts/` | CLI scripts for each operation |
| `tests/` | 26 unit tests |
| `.github/workflows/` | 3 CI/CD workflow definitions |
| `results/` | Output directory for reports and logs |
