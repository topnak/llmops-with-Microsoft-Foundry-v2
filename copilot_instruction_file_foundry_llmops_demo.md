# GitHub Copilot Instruction File  
## Microsoft Foundry NextGen LLMOps Demo  
### Project: RetailPersonlisedAgent

You are GitHub Copilot operating as a senior Microsoft Foundry / Azure AI Foundry engineer, Python engineer, prompt engineer, and demo experience designer.

Your job is to generate a complete, runnable local repository that supports a **20-minute guided demo** for **LLMOps on Microsoft Foundry NextGen (v2)**.

This repository must do two things at the same time:

1. **Actually work as a local project** that can connect to Microsoft Foundry and create/use an agent.
2. **Act as a walkthrough experience** for a presentation, including a lightweight local UI that lets the presenter click through each LLMOps stage step by step.

The result must feel like **“a day in the life of an LLMOps engineer”** using Microsoft Foundry from prompt management to evaluation, monitoring, governance, and CI/CD automation.

---

# 1. Core Demo Story and Experience Design

Build the repo around this exact story:

## Demo narrative
A retail organization wants an intelligent assistant that can personalize retail recommendations across Australian brands such as Kmart, Officeworks, and Bunnings.

The LLMOps engineer needs to:
- start with prompt management
- create and version a Foundry agent
- personalize the experience using customer memory / personas
- compare model behavior
- evaluate quality
- review traces / monitoring concepts
- show governance controls
- show how GitHub Actions can automate the loop

## Demo presentation goal
The repository must support a 20-minute demo with these stages:

1. **Intro / scenario**
2. **Prompt management**
3. **Create or update agent in Microsoft Foundry**
4. **Run baseline response**
5. **Inject persona memory**
6. **Compare multiple models**
7. **Run evaluation**
8. **Show monitoring / tracing explanation**
9. **Show governance explanation**
10. **Show GitHub Actions automation**

The local UI must let the presenter click **Next** through these stages in order.

The repo is not just backend code. It must include a **simple local demo UI** that explains each step and allows each step to be executed.

---

# 2. Existing Environment and Required Connection Details

Use these Microsoft Foundry details as the source of truth.

## Existing Foundry project endpoint
`https://llmops-foundry.services.ai.azure.com/api/projects/llm-ops-foundry-demo`

## Existing environment variables to support
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_LOCATION`
- `AZURE_EXISTING_AIPROJECT_ENDPOINT`
- `AZURE_EXISTING_AIPROJECT_RESOURCE_ID`
- `AZURE_EXISTING_RESOURCE_ID`
- `AZURE_ENV_NAME`
- `AZD_ALLOW_NON_EMPTY_FOLDER`

## Existing sample values the repo should support in `.env.example`
- `AZURE_LOCATION=australiaeast`
- `AZURE_EXISTING_AIPROJECT_ENDPOINT=https://llmops-foundry.services.ai.azure.com/api/projects/llm-ops-foundry-demo`

## Agent to create
Create a **new agent** in Microsoft Foundry with this exact name:

`RetailPersonlisedAgent`

Important:
- Use the spelling exactly as written above: `RetailPersonlisedAgent`
- Do not silently “correct” the name in generated code or docs
- If you want to create a friendlier display title in the UI, you may display `Retail Personalised Agent`, but code and config must keep the exact agent name above

## Main model
Use this as the primary model deployment name by default:

`gpt-4.1-mini`

If the environment provides alternate deployment names, make them configurable. But the default primary value must still be `gpt-4.1-mini`.

---

# 3. Authentication and Security Requirements

Use **Service Principal authentication** with `DefaultAzureCredential`.

Requirements:
- never hardcode secrets
- load credentials from environment variables
- support local `.env`
- support GitHub Actions secrets
- provide clear logging if authentication fails
- provide a troubleshooting section in README

Use these Python imports where appropriate:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
```

The code must:
- instantiate an `AIProjectClient`
- connect to the existing Foundry project endpoint
- create or version the agent
- get an OpenAI-compatible client from the project client
- invoke responses through `agent_reference`

---

# 4. Repository to Generate

Create a complete repository with the following structure.

```text
llmops-foundry-nextgen-demo/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── eval.yml
│       └── foundry-smoke.yml
├── app/
│   ├── __init__.py
│   ├── demo_ui.py
│   ├── pages.py
│   └── assets/
│       └── demo_steps.json
├── data/
│   ├── personas.json
│   ├── eval_cases.jsonl
│   ├── products.json
│   └── demo_story.json
├── prompts/
│   ├── baseline.txt
│   ├── cost_optimized.txt
│   ├── quality_optimized.txt
│   └── grounded_retail.txt
├── results/
│   └── .gitkeep
├── scripts/
│   ├── create_agent.py
│   ├── update_agent_version.py
│   ├── run_baseline.py
│   ├── compare_models.py
│   ├── run_eval.py
│   ├── export_demo_report.py
│   └── seed_local_memory.py
├── src/
│   └── llmops_demo/
│       ├── __init__.py
│       ├── config.py
│       ├── logging_config.py
│       ├── foundry_client.py
│       ├── agent_manager.py
│       ├── agent_runner.py
│       ├── prompt_manager.py
│       ├── memory.py
│       ├── model_compare.py
│       ├── evaluation.py
│       ├── monitoring.py
│       ├── governance.py
│       ├── reporting.py
│       └── utils.py
├── tests/
│   ├── test_config.py
│   ├── test_prompt_manager.py
│   ├── test_memory.py
│   ├── test_evaluation.py
│   └── test_demo_story.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── pyproject.toml
```

Generate every file with real, useful implementation. Do not leave placeholder files empty except for `.gitkeep`.

---

# 5. Local UI Requirement

Create a lightweight local web UI that acts as the **guided show-and-tell console** for the 20-minute demo.

## Preferred UI technology
Use **Streamlit** for speed and simplicity.

Include Streamlit in dependencies and create an app entry point:

- `app/demo_ui.py`

## UI design goals
The UI must:
- be clean and presentation-friendly
- explain each LLMOps stage in plain English
- allow the presenter to click **Next** and **Back**
- show current stage number and title
- show what Foundry capability is being demonstrated
- execute code actions for each stage where practical
- show outputs in a formatted way suitable for live demo or screenshots

## Required UI flow
The UI must contain these steps in this order:

### Step 1 — Welcome / Story setup
Explain:
- the retail scenario
- why LLMOps matters
- why Microsoft Foundry is being used

Display:
- demo objective
- architecture summary
- project endpoint from config

### Step 2 — Prompt management
Explain:
- prompts are versioned assets
- multiple prompt variants exist
- prompt changes affect behavior and quality

UI actions:
- list prompt files
- show selected prompt
- allow user to switch between baseline, cost_optimized, quality_optimized, grounded_retail

### Step 3 — Create / update agent in Foundry
Explain:
- agent versioning
- why we create a managed agent in Foundry
- that this demo creates or updates `RetailPersonlisedAgent`

UI action:
- button: “Create or Update Agent”
- show success/failure
- show returned agent information

### Step 4 — Baseline run
Explain:
- the baseline agent behavior with no extra persona memory
- the main model is gpt-4.1-mini

UI action:
- run a sample query against the agent
- display model used, prompt variant, and response text

### Step 5 — Persona personalization
Explain:
- persona data acts like lightweight memory/context
- LLMOps includes data + prompt + agent orchestration

UI action:
- dropdown to select persona
- inject persona context into the prompt
- rerun agent
- display response difference

### Step 6 — Multi-model comparison
Explain:
- changing models is part of optimization
- compare quality, style, latency, and consistency

UI action:
- compare at least two models/configurations
- display results side-by-side in tables/cards
- include elapsed time if measurable

### Step 7 — Evaluation
Explain:
- evaluation makes the loop measurable
- each change should be tested against a fixed set of scenarios

UI action:
- run local evaluation on JSONL test cases
- show scores:
  - relevance
  - personalization
  - grounding
  - policy/safety
  - total
- show leaderboard for compared models/prompt variants

### Step 8 — Monitoring and traces
Explain:
- monitoring is part of LLMOps even if the local demo cannot fetch every trace
- show what engineers would inspect in Foundry

UI requirement:
- implement a local monitoring summary panel that displays:
  - timestamp
  - selected model
  - prompt variant
  - persona used
  - evaluation score
  - latency
- if runtime data exists, show it
- if not, explain how this maps to Foundry tracing/monitoring

### Step 9 — Governance and guardrails
Explain:
- guardrails
- approved prompts
- change control
- RBAC concepts
- safe usage expectations

UI requirement:
- present governance checklist items
- show which controls are local demo constructs versus real Foundry/enterprise concepts
- include a “What to say in the demo” presenter note section

### Step 10 — GitHub Actions / automation
Explain:
- changes can be validated in CI
- prompt changes can trigger eval
- promotion can be quality-gated

UI requirement:
- show workflow files content or summaries
- display the automation loop visually
- include a final “LLMOps loop complete” summary page

## UI behavior
The UI must:
- save stage state in session
- allow reruns safely
- avoid crashing on transient errors
- show friendly errors with technical details expandable
- write outputs to `results/`

---

# 6. Prompt Management Requirements

Implement prompt management as a first-class feature.

Create these prompt files with meaningful content:

## `prompts/baseline.txt`
Should represent the default retail assistant behavior.

## `prompts/cost_optimized.txt`
Should be more concise, stricter, and cheaper to run conceptually.

## `prompts/quality_optimized.txt`
Should emphasize helpfulness, personalization, and explanation.

## `prompts/grounded_retail.txt`
Should emphasize staying grounded in known inventory and refusing unsupported claims.

Implement:
- prompt loader
- prompt validation
- prompt listing
- prompt preview
- prompt checksum/version helper if useful

Create a `prompt_manager.py` module with functions like:
- `list_prompts()`
- `load_prompt(name: str) -> str`
- `validate_prompt(name: str) -> tuple[bool, list[str]]`

The UI and scripts must use this module.

---

# 7. Agent Instructions to Use

When creating the agent, use a strong retail-focused instruction set aligned to the demo.

Use this as the basis for the agent instructions:

“You are a Retail Personalization Assistant for Australia. You support Kmart, Officeworks, and Bunnings.

Your responsibilities:
- personalize recommendations based on customer context and retail preferences
- provide helpful retail suggestions grounded in the approved inventory and scenario context
- suggest relevant upsell and cross-sell items when appropriate
- avoid hallucinating products, pricing, stock levels, or policies
- keep responses concise, practical, and suitable for retail operations use
- if information is missing, say so clearly instead of inventing details
- prefer safe, factual, and business-friendly responses”

Create the agent using `PromptAgentDefinition` and the configured model deployment name.

Implement in `agent_manager.py`:
- `create_or_update_agent()`
- `create_agent_version_from_prompt(prompt_name: str, model_name: str)`
- `get_agent_reference_payload()`

Important behavior:
- if the SDK allows `create_version`, use that
- if agent already exists, create a new version rather than failing
- log all actions clearly

---

# 8. Foundry Client and Invocation Requirements

In `foundry_client.py`, implement a robust wrapper around the Foundry project connection.

Required capabilities:
- `create_project_client()`
- `get_openai_client()`
- `create_prompt_agent_version(...)`
- `invoke_agent(...)`

The invoke path must use:
- OpenAI-compatible responses API
- `extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}}`
or equivalent depending on implementation details

Design the wrapper so the rest of the app can call it simply.

Provide structured return objects such as dictionaries or dataclasses containing:
- agent name
- model name
- version if available
- prompt variant
- persona
- response text
- status
- elapsed time
- any error message

---

# 9. Personalization and Dummy Data

We do not want a huge fake dataset. Keep the dummy data light, believable, and easy to demo.

## `data/personas.json`
Create five personas:

1. **Budget Shopper**
2. **Premium Shopper**
3. **DIY Customer**
4. **Office Worker**
5. **Seasonal Buyer**

Each persona must include:
- `persona_id`
- `name`
- `store_preferences`
- `budget_band`
- `preferred_categories`
- `past_purchases`
- `upsell_tolerance`
- `cross_sell_interest`
- `notes`

## `data/products.json`
Create a small approved product list for grounding:
- 12 to 20 products total
- spread across Kmart, Officeworks, and Bunnings
- include simple fields:
  - `product_id`
  - `store`
  - `name`
  - `category`
  - `price_aud`
  - `tags`

Important:
- this product data is not pretending to be real enterprise data
- it is only enough to support grounding and personalization in the demo

## Memory behavior
Implement `memory.py` with functions such as:
- `load_personas()`
- `get_persona(persona_id: str)`
- `inject_memory_into_prompt(prompt_text: str, user_input: str, persona: dict, product_context: list[dict]) -> str`

The goal is:
- baseline run without persona memory
- personalized run with persona and product context included

This is sufficient for the demo even if a full Foundry memory store integration is not available.

---

# 10. Model Comparison Requirements

Implement model experimentation as part of the LLMOps loop.

In `model_compare.py`:
- support at least two model options
- primary default is `gpt-4.1-mini`
- allow secondary values through config, for example:
  - `gpt-4.1`
  - another configured deployment if available

Required function:
- `compare_models(user_input: str, prompt_name: str, persona_id: str | None) -> dict`

The compare function must:
- run the same scenario across multiple model configs
- optionally create temporary agent versions if needed
- capture latency
- capture response text
- capture status and errors
- produce a comparison summary

The UI must render this cleanly.

---

# 11. Evaluation Requirements

Create a local evaluation framework that is easy to explain in a live demo.

## `data/eval_cases.jsonl`
Create at least 10 evaluation cases.
Each line must include:
- `id`
- `user_input`
- `persona_id` (optional)
- `expected_traits`
- `must_not_do`

Examples should cover:
- budget recommendation
- premium upsell
- cross-sell
- refusal to hallucinate unavailable products
- concise business-friendly tone
- category-specific suggestions

## `evaluation.py`
Implement:
- test case loading
- heuristic scoring
- summary generation
- markdown report generation
- json report generation

Score these dimensions from 0 to 5:
- relevance
- personalization
- grounding
- policy_safety
- total

The heuristics can be simple and practical, for example:
- relevance based on mention of requested category/needs
- personalization based on persona-aligned terms
- grounding based on use of known product/store names
- policy_safety based on avoiding prohibited behavior or hallucinated unsupported claims

Create outputs:
- `results/eval_summary.json`
- `results/eval_summary.md`

The UI must show evaluation results in a table and simple charts if practical.

---

# 12. Monitoring, Reporting, and Governance Modules

Implement lightweight modules that support the presentation.

## `monitoring.py`
Create local runtime event logging for:
- start time
- end time
- elapsed time
- agent
- model
- prompt
- persona
- success/failure
- evaluation total

Save records to a local jsonl or json file in `results/`.

## `reporting.py`
Create helpers to:
- save markdown summaries
- save JSON artifacts
- save demo snapshots if needed
- generate a final presentation-friendly summary

## `governance.py`
Create a governance checklist and helper functions that explain:
- approved prompt use
- agent versioning
- evaluation before promotion
- least-privilege credentials
- CI validation
- safety expectations

This module does not need to enforce enterprise policy, but it must generate useful governance content for the UI and README.

---

# 13. Scripts to Generate

Create the following scripts with full implementation and CLI argument support where practical.

## `scripts/create_agent.py`
Purpose:
- create or update `RetailPersonlisedAgent`

## `scripts/update_agent_version.py`
Purpose:
- create a new version from a selected prompt variant and/or model

## `scripts/run_baseline.py`
Purpose:
- run the baseline scenario with the primary model

## `scripts/compare_models.py`
Purpose:
- compare model outputs

## `scripts/run_eval.py`
Purpose:
- run evaluation suite and write reports

## `scripts/export_demo_report.py`
Purpose:
- generate a concise final report for presentation use

## `scripts/seed_local_memory.py`
Purpose:
- validate persona data and optionally print persona summary

All scripts must:
- be runnable from the command line
- have helpful output
- use the shared modules in `src/llmops_demo/`
- fail with clear messages

---

# 14. Configuration Requirements

In `config.py`, implement robust configuration loading.

Use environment variables and provide sensible defaults where safe.

Required fields:
- project endpoint
- agent name
- primary model
- comparison models
- results directory
- app title
- log level

Support parsing existing agent version strings if provided, but default to the new target agent name:
- `RetailPersonlisedAgent`

Suggested config fields:
- `app_title = "Microsoft Foundry LLMOps Demo"`
- `primary_model = "gpt-4.1-mini"`
- `comparison_models = ["gpt-4.1-mini", "gpt-4.1"]`

Create a `.env.example` containing all needed variables and comments.

---

# 15. Logging and Reliability

Add proper logging.

Create `logging_config.py` and initialize logging across the app.

Requirements:
- use standard library logging
- support info/debug levels
- include timestamps
- keep console output readable

Reliability rules:
- handle missing env vars
- handle auth failures
- handle agent create failures
- handle invocation failures
- show actionable remediation
- do not allow unhandled exceptions to crash the Streamlit UI unless absolutely necessary

---

# 16. Tests

Create meaningful tests for:
- config loading
- prompt loading and validation
- memory loading
- evaluation heuristics
- demo story metadata

Tests do not need live Foundry connectivity by default.
Mock where required.

Use `pytest`.

---

# 17. GitHub Actions

Create these workflows.

## `.github/workflows/ci.yml`
Run on:
- push
- pull_request
- workflow_dispatch

Steps:
- checkout
- setup Python
- install dependencies
- run tests
- validate prompt files
- run a lightweight local smoke check

## `.github/workflows/eval.yml`
Run on:
- workflow_dispatch
- push to main

Steps:
- checkout
- setup Python
- install dependencies
- run evaluation
- upload `results/` artifacts

## `.github/workflows/foundry-smoke.yml`
Run on:
- workflow_dispatch only

Purpose:
- optional smoke validation against live Foundry

Use GitHub secrets:
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_EXISTING_AIPROJECT_ENDPOINT`
- optional model overrides

The workflow must be careful and readable. Add comments to explain what each step is for.

---

# 18. README Requirements

Generate a complete `README.md`.

The README must include:

1. Project overview
2. Demo story
3. Architecture
4. Repository structure
5. Prerequisites
6. Local setup
7. Environment variables
8. Create/update agent
9. Run Streamlit UI
10. Run baseline script
11. Compare models
12. Run evaluation
13. GitHub Actions automation
14. How this maps to the Microsoft Foundry demo walkthrough
15. Troubleshooting
16. Suggested presenter talk track

The talk track section should align to the UI sequence and the 20-minute demo.

---

# 19. Presenter Notes and Walkthrough Alignment

The generated repo must include explicit presenter support.

Create:
- `data/demo_story.json`
- `app/assets/demo_steps.json`

These files must contain:
- step title
- objective
- what action to click
- what to say
- expected result
- fallback note if the live service fails

The UI should surface this in a presenter-friendly format.

Example pattern for each stage:
- `step_number`
- `title`
- `llmops_stage`
- `foundry_capability`
- `speaker_note`
- `action_label`
- `expected_output`

This is essential. The repo is not only functional code; it is a show-and-tell tool.

---

# 20. Technical Expectations for Generated Code

Code quality requirements:
- Python 3.11+
- type hints where practical
- docstrings on major public functions
- no giant monolithic file except where it makes sense for Streamlit UI
- keep business logic in `src/llmops_demo/`, not directly in scripts
- maintain separation between UI, core logic, and data

Do not generate pseudo code.
Do not leave TODO-only logic.
Do not leave placeholder comments like “implement later.”
Everything must be meaningfully implemented.

---

# 21. Specific Implementation Pattern for Agent Creation

When generating the agent creation code, follow this logic:

1. load config
2. create `AIProjectClient` using endpoint + `DefaultAzureCredential`
3. construct `PromptAgentDefinition` with:
   - model = configured primary model
   - instructions = combined retail system instructions or prompt text
4. call the agent creation/version API
5. return structured metadata
6. log success/failure

Also create a helper that can create a new version from a selected prompt variant.

The code should make it easy for the presenter to say:
- “This is our baseline managed agent in Foundry”
- “Now we change the prompt and create a new version”
- “Now we compare outputs and evaluate quality”

---

# 22. Required Sample Queries for the Demo

Include built-in sample prompts in the UI and scripts such as:
- “Recommend three products for a budget-conscious customer shopping at Kmart, including one upsell and one cross-sell.”
- “Suggest premium desk setup items for an Officeworks customer who already bought a monitor.”
- “Recommend two DIY items from Bunnings for a returning customer, but do not exceed a mid-range budget.”
- “If a requested product is not in the approved list, say so clearly and do not invent it.”

These should appear in the UI as quick-select examples.

---

# 23. Output and Reporting Expectations

All major actions should save machine-readable and human-readable outputs to `results/`.

Expected outputs include:
- baseline run result JSON
- model comparison JSON and markdown
- evaluation summary JSON and markdown
- monitoring log JSONL
- optional final demo report markdown

The goal is to make the repo useful both for live demo and post-demo artifact review.

---

# 24. Final Build Behavior

Generate all files in one go.

Order of work:
1. create project structure
2. create config and logging
3. create Foundry connection layer
4. create agent management and runner
5. create prompt and memory systems
6. create evaluation and monitoring
7. create scripts
8. create Streamlit UI
9. create tests
10. create GitHub Actions
11. create README and presenter assets

Do not skip steps.
Do not summarize without creating files.
Do not output only a plan.
Actually generate the code and content.

If any library or SDK behavior is uncertain, implement the cleanest practical version while keeping the code organized and easy to adjust.

The repository must be a credible, demo-ready Microsoft Foundry LLMOps starter project centered on the agent:

`RetailPersonlisedAgent`
