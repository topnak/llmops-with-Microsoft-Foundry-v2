# COPILOT_TASK_CHECKLIST.md
## Microsoft Foundry LLMOps Demo Build Checklist

Use this checklist together with `copilot_instruction_file_foundry_llmops_demo.md`.

## Where this file goes

Place this file in the **root of your repo**, next to:
- `README.md`
- `.env.example`
- `requirements.txt`
- `pyproject.toml`

Recommended layout:

```text
llmops-foundry-nextgen-demo/
├── COPILOT_TASK_CHECKLIST.md
├── copilot_instruction_file_foundry_llmops_demo.md
├── README.md
├── .env.example
├── requirements.txt
├── pyproject.toml
├── app/
├── data/
├── prompts/
├── results/
├── scripts/
├── src/
└── tests/
```

---

## How to use this checklist

Work through the repo in this order. After Copilot generates each section, verify it before moving to the next one.

Mark each item complete only when:
- files exist
- code runs
- imports resolve
- names match the instruction file
- outputs are written correctly

---

# Phase 1 — Create the repository skeleton

- [ ] Create the main project folder: `llmops-foundry-nextgen-demo`
- [ ] Copy `copilot_instruction_file_foundry_llmops_demo.md` into the project root
- [ ] Copy this file `COPILOT_TASK_CHECKLIST.md` into the project root
- [ ] Open the folder in VS Code
- [ ] Initialize Git
- [ ] Create Python virtual environment
- [ ] Confirm GitHub Copilot Chat is available in VS Code

Expected result:
- repo opens cleanly
- root folder is ready for Copilot-driven generation

---

# Phase 2 — Ask Copilot to generate the repo

Primary action:
- [ ] Open Copilot Chat in Agent/Edit mode if available
- [ ] Attach or paste `copilot_instruction_file_foundry_llmops_demo.md`
- [ ] Ask Copilot to generate the project from the instruction file
- [ ] Let it create folders and files in the repo
- [ ] Review generated files before accepting all changes

Prompt to use with Copilot:
```text
Read `copilot_instruction_file_foundry_llmops_demo.md` in this repository and generate the full project exactly as specified. Follow the repository structure, create all files, and build the Streamlit demo UI, Foundry integration, scripts, tests, workflows, data files, and README.
```

Expected result:
- all major folders created
- initial code and docs generated

---

# Phase 3 — Verify root files

- [ ] `README.md` exists
- [ ] `.env.example` exists
- [ ] `requirements.txt` exists
- [ ] `pyproject.toml` exists
- [ ] `.gitignore` exists

Check content:
- [ ] README includes setup, demo story, architecture, troubleshooting, presenter talk track
- [ ] `.env.example` includes Foundry endpoint and auth variables
- [ ] dependencies include Streamlit, Azure SDK, dotenv, pytest, rich
- [ ] `.gitignore` excludes `.env`, `.venv`, `__pycache__`, `.pytest_cache`, `results/*`

Expected result:
- root project files are complete and usable

---

# Phase 4 — Verify folder structure

- [ ] `app/` exists
- [ ] `app/assets/` exists
- [ ] `data/` exists
- [ ] `prompts/` exists
- [ ] `results/` exists
- [ ] `scripts/` exists
- [ ] `src/llmops_demo/` exists
- [ ] `tests/` exists
- [ ] `.github/workflows/` exists

Expected result:
- structure matches the instruction file closely

---

# Phase 5 — Verify prompt assets

- [ ] `prompts/baseline.txt` exists
- [ ] `prompts/cost_optimized.txt` exists
- [ ] `prompts/quality_optimized.txt` exists
- [ ] `prompts/grounded_retail.txt` exists

Quality check:
- [ ] prompts are meaningful and different from each other
- [ ] baseline prompt matches retail assistant behavior
- [ ] grounded prompt explicitly discourages hallucinations
- [ ] cost prompt is shorter and stricter
- [ ] quality prompt emphasizes personalization and reasoning

Expected result:
- prompt management is demo-ready

---

# Phase 6 — Verify dummy data

- [ ] `data/personas.json` exists
- [ ] `data/products.json` exists
- [ ] `data/eval_cases.jsonl` exists
- [ ] `data/demo_story.json` exists
- [ ] `app/assets/demo_steps.json` exists

Quality check:
- [ ] 5 personas exist
- [ ] products cover Kmart, Officeworks, and Bunnings
- [ ] eval cases include at least 10 cases
- [ ] demo steps align to the 20-minute walkthrough
- [ ] presenter notes are included

Expected result:
- demo data supports personalization, grounding, and presenter flow

---

# Phase 7 — Verify core Python modules

- [ ] `src/llmops_demo/config.py`
- [ ] `src/llmops_demo/logging_config.py`
- [ ] `src/llmops_demo/foundry_client.py`
- [ ] `src/llmops_demo/agent_manager.py`
- [ ] `src/llmops_demo/agent_runner.py`
- [ ] `src/llmops_demo/prompt_manager.py`
- [ ] `src/llmops_demo/memory.py`
- [ ] `src/llmops_demo/model_compare.py`
- [ ] `src/llmops_demo/evaluation.py`
- [ ] `src/llmops_demo/monitoring.py`
- [ ] `src/llmops_demo/governance.py`
- [ ] `src/llmops_demo/reporting.py`
- [ ] `src/llmops_demo/utils.py`

Quality check:
- [ ] imports resolve
- [ ] type hints are present where practical
- [ ] logging is used
- [ ] modules are separated cleanly
- [ ] there is no obvious placeholder-only logic

Expected result:
- backend is organized and maintainable

---

# Phase 8 — Verify Foundry config and auth

- [ ] `.env` created from `.env.example`
- [ ] `AZURE_CLIENT_ID` set
- [ ] `AZURE_CLIENT_SECRET` set
- [ ] `AZURE_TENANT_ID` set
- [ ] `AZURE_EXISTING_AIPROJECT_ENDPOINT` set
- [ ] endpoint points to `https://llmops-foundry.services.ai.azure.com/api/projects/llm-ops-foundry-demo`

Quality check:
- [ ] `config.py` loads values successfully
- [ ] missing env vars produce clear error messages
- [ ] `DefaultAzureCredential` is used
- [ ] no secrets are hardcoded

Expected result:
- project can authenticate safely

---

# Phase 9 — Verify agent creation logic

- [ ] `scripts/create_agent.py` exists
- [ ] code targets agent name exactly: `RetailPersonlisedAgent`
- [ ] primary model defaults to `gpt-4.1-mini`
- [ ] agent uses `PromptAgentDefinition`
- [ ] create/update logic is implemented
- [ ] versioning logic is implemented if possible

Run:
```bash
python scripts/create_agent.py
```

Check:
- [ ] auth works
- [ ] Foundry connection succeeds
- [ ] agent create/update returns useful output
- [ ] success and error paths are logged clearly

Expected result:
- `RetailPersonlisedAgent` is created or updated in Foundry

---

# Phase 10 — Verify baseline execution

- [ ] `scripts/run_baseline.py` exists

Run:
```bash
python scripts/run_baseline.py
```

Check:
- [ ] baseline retail prompt runs
- [ ] response comes back from Foundry
- [ ] output includes agent name, model, prompt variant, response, timing
- [ ] output is saved into `results/`

Expected result:
- baseline run is working

---

# Phase 11 — Verify personalization flow

- [ ] `memory.py` loads personas correctly
- [ ] local memory injection works
- [ ] baseline without persona and run with persona both work
- [ ] persona changes response meaningfully

Check:
- [ ] Budget Shopper response differs from Premium Shopper response
- [ ] product/store mentions are relevant
- [ ] prompt injection is clearly visible in code design

Expected result:
- personalization stage is demo-ready

---

# Phase 12 — Verify model comparison

- [ ] `scripts/compare_models.py` exists
- [ ] comparison supports at least two models/configurations
- [ ] latency is measured if practical
- [ ] outputs are shown side-by-side
- [ ] failures for unavailable secondary models are handled gracefully

Run:
```bash
python scripts/compare_models.py
```

Check:
- [ ] comparison summary printed
- [ ] JSON or markdown written to `results/`
- [ ] output is easy to screenshot

Expected result:
- multi-model optimization story is working

---

# Phase 13 — Verify evaluation

- [ ] `scripts/run_eval.py` exists
- [ ] evaluation loads JSONL correctly
- [ ] heuristic scoring works
- [ ] markdown and JSON reports are written

Run:
```bash
python scripts/run_eval.py
```

Check:
- [ ] `results/eval_summary.json` created
- [ ] `results/eval_summary.md` created
- [ ] scores shown for relevance, personalization, grounding, policy/safety, total
- [ ] summary is readable for presentation

Expected result:
- measurable LLMOps quality loop is working

---

# Phase 14 — Verify monitoring and governance layers

- [ ] `monitoring.py` writes runtime logs to `results/`
- [ ] `governance.py` contains governance checklist and presenter-safe explanations
- [ ] UI can show monitoring summary
- [ ] UI can show governance explanation

Check:
- [ ] monitoring includes prompt, model, persona, timing
- [ ] governance section clearly distinguishes local demo controls vs enterprise concepts

Expected result:
- operational story is complete

---

# Phase 15 — Verify Streamlit walkthrough UI

- [ ] `app/demo_ui.py` exists
- [ ] app has Next and Back navigation
- [ ] step state is preserved
- [ ] demo steps align to the instruction file
- [ ] UI shows presenter notes
- [ ] UI can trigger code actions where practical

Run:
```bash
streamlit run app/demo_ui.py
```

Check these steps exist:
- [ ] Welcome / Story setup
- [ ] Prompt management
- [ ] Create / update agent
- [ ] Baseline run
- [ ] Persona personalization
- [ ] Multi-model comparison
- [ ] Evaluation
- [ ] Monitoring and traces
- [ ] Governance and guardrails
- [ ] GitHub Actions / automation

Expected result:
- presenter can walk through the full LLMOps loop in one UI

---

# Phase 16 — Verify tests

- [ ] test suite exists
- [ ] tests do not require live Foundry by default
- [ ] core modules are covered

Run:
```bash
pytest
```

Check:
- [ ] tests pass
- [ ] failures are understandable
- [ ] mocks are used where needed

Expected result:
- repo has a safe local validation loop

---

# Phase 17 — Verify GitHub Actions

- [ ] `.github/workflows/ci.yml` exists
- [ ] `.github/workflows/eval.yml` exists
- [ ] `.github/workflows/foundry-smoke.yml` exists

Check:
- [ ] workflows are readable
- [ ] Azure secrets are referenced correctly
- [ ] eval uploads artifacts
- [ ] smoke workflow is manual-only

Expected result:
- CI/CD story is ready for demo

---

# Phase 18 — Final demo rehearsal checklist

Before presenting:

- [ ] `.env` is correct
- [ ] `python scripts/create_agent.py` works
- [ ] `python scripts/run_baseline.py` works
- [ ] `python scripts/compare_models.py` works
- [ ] `python scripts/run_eval.py` works
- [ ] `streamlit run app/demo_ui.py` works
- [ ] results folder contains fresh output
- [ ] fallback notes exist in UI/demo steps
- [ ] one screenshot-ready eval report is available
- [ ] one screenshot-ready comparison result is available

Expected result:
- no surprises except the ones you planned for

---

# Recommended usage pattern in VS Code

## Option A — best practical approach
1. Put both markdown files in the repo root
2. Ask Copilot to read the instruction file first
3. Let it generate the code
4. Use this checklist to verify and patch gaps in smaller passes

Suggested Copilot follow-up prompts:
```text
Read `COPILOT_TASK_CHECKLIST.md` and tell me which items are incomplete in the current repository.
```

```text
Complete Phase 7 and Phase 8 from `COPILOT_TASK_CHECKLIST.md`.
```

```text
Fix any issues preventing the Streamlit demo UI from running.
```

## Option B — if Copilot struggles with one-shot generation
Generate in this order:
1. core structure
2. config + Foundry client
3. agent creation + runner
4. prompt + memory
5. evaluation + monitoring
6. Streamlit UI
7. workflows + README + tests

---

# Acceptance criteria

This repo is complete only when:

- [ ] `RetailPersonlisedAgent` can be created or updated
- [ ] baseline run works
- [ ] persona-based run works
- [ ] model comparison works
- [ ] evaluation works
- [ ] monitoring/governance story is visible
- [ ] Streamlit walkthrough works
- [ ] GitHub Actions files exist
- [ ] README supports a 20-minute demo

---

# Notes for the presenter

This checklist is not just for build quality.
It also ensures the repo supports your show-and-tell flow:
- prompt management
- managed agent in Foundry
- personalization
- model experimentation
- evaluation
- monitoring
- governance
- automation

That is the LLMOps loop.
