# LLMOps Maturity Level Mapping

## 1. Microsoft LLMOps Maturity Model

Microsoft defines **four maturity levels** for LLMOps adoption.
Each level represents increasing sophistication in how organizations manage
the AI lifecycle:

| Level | Name | Description |
|---|---|---|
| **L0** | **Ad-hoc** | Manual prompt editing, no versioning, no structured evaluation. Teams copy-paste prompts and test by eye. |
| **L1** | **Foundational** | Prompts are stored as files. Agents are created in a managed service. Baseline testing exists. Manual but repeatable. |
| **L2** | **Standardized** | Structured evaluation with scoring dimensions. Model comparison for cost/quality trade-offs. Monitoring in place. Governance controls defined. |
| **L3** | **Advanced / Automated** | CI/CD pipelines validate every change. Promotion is quality-gated. Monitoring feeds back into the development loop. Full governance enforcement. |

---

## 2. How Each Menu Maps to Maturity Levels

### LLMOps Process Stages (Color Coding)

Each step in the demo maps to one of **five LLMOps process stages**:

| Stage | Color | Hex | Description |
|---|---|---|---|
| **Design** | 🟣 Purple | `#7B2D8E` | Defining the problem, setting the scene |
| **Build** | 🔵 Blue | `#0078D4` | Creating prompts, agents, and configurations |
| **Test & Evaluate** | 🟢 Green | `#13A10E` | Running the agent, comparing, scoring |
| **Operate** | 🟠 Orange | `#CA5010` | Monitoring, tracing, observability |
| **Govern & Automate** | 🔴 Red | `#D13438` | Governance, guardrails, CI/CD |

---

### Step-by-Step Maturity Mapping

#### Step 1 — Intro / Scenario

| | |
|---|---|
| **LLMOps Stage** | 🟣 Design |
| **Maturity Level** | L0 → L1 |
| **Why** | Moving from "we should build an AI assistant" (L0 thinking) to "we have a structured plan with clear personas and a managed platform" (L1). This step sets the foundation that prevents ad-hoc approaches. |
| **What it proves** | An LLMOps engineer starts with a clear problem definition, not with code. |

---

#### Step 2 — Prompt Management

| | |
|---|---|
| **LLMOps Stage** | 🔵 Build |
| **Maturity Level** | L1 |
| **Why** | Prompts are stored as **versioned files** with checksums, not ad-hoc strings in a notebook. Multiple variants (baseline, cost-optimized, quality-optimized, grounded) show deliberate prompt engineering. Validation ensures prompts contain required elements. |
| **What it proves** | The organization treats prompts as first-class assets with version control. |
| **Moving to L2** | Would add A/B testing between prompt variants with automated scoring. |

---

#### Step 3 — Create / Update Agent in Foundry

| | |
|---|---|
| **LLMOps Stage** | 🔵 Build |
| **Maturity Level** | L1 → L2 |
| **Why** | Agent creation is managed and versioned via `AIProjectClient.agents.create_version()`. Each new version is non-destructive. The agent is tied to a specific model deployment and instruction set — not hardcoded in application code. |
| **What it proves** | The organization uses a managed platform (Foundry) for agent lifecycle, not manual deployments. |
| **Moving to L2** | Agent versioning is tracked; different versions can be compared in evaluation. |

---

#### Step 4 — Baseline Run

| | |
|---|---|
| **LLMOps Stage** | 🟢 Test & Evaluate |
| **Maturity Level** | L1 |
| **Why** | Establishing a baseline is the first step in measurable improvement. Without a baseline, there is no way to know if changes are positive. The result is structured (model, prompt, latency, response) and logged. |
| **What it proves** | The team measures before optimizing. |

---

#### Step 5 — Persona Personalization

| | |
|---|---|
| **LLMOps Stage** | 🟢 Test & Evaluate |
| **Maturity Level** | L1 → L2 |
| **Why** | Personalization injects customer context (persona preferences, budget, history) into the prompt. This demonstrates **data + prompt + orchestration** as a combined practice. Comparing persona vs. baseline output shows measurable behavior change. |
| **What it proves** | Prompts aren't static — context injection is part of the optimization loop. |
| **Moving to L2** | Would connect to a real customer data platform or Foundry memory store. |

---

#### Step 6 — Multi-Model Comparison

| | |
|---|---|
| **LLMOps Stage** | 🟢 Test & Evaluate |
| **Maturity Level** | L2 |
| **Why** | Comparing multiple models (gpt-4.1-mini vs. gpt-4.1 vs. retail-mini) for the same query is a **standardized practice**. The comparison includes quality, latency, and enables cost/quality trade-off decisions. This is not ad-hoc — it's a structured experiment. |
| **What it proves** | Model selection is data-driven, not opinion-driven. |

---

#### Step 7 — Evaluation

| | |
|---|---|
| **LLMOps Stage** | 🟢 Test & Evaluate |
| **Maturity Level** | L2 |
| **Why** | Structured evaluation with **four scoring dimensions** (relevance, personalization, grounding, policy/safety) against 12 fixed test cases. Results are saved as reports. This is the core of LLMOps maturity — every change is evaluated against a consistent benchmark. |
| **What it proves** | Quality is measurable and repeatable, not subjective. |
| **Moving to L3** | Evaluation runs automatically in CI on every prompt change. |

---

#### Step 8 — Monitoring and Traces

| | |
|---|---|
| **LLMOps Stage** | 🟠 Operate |
| **Maturity Level** | L2 |
| **Why** | Every invocation is traced with structured data (model, prompt variant, persona, latency, status). The local monitoring log mirrors what Foundry provides natively via Azure Monitor and Application Insights. Monitoring enables the feedback loop from production back to development. |
| **What it proves** | Observability is built in, not bolted on. |
| **Moving to L3** | Monitoring alerts trigger automated re-evaluation or rollback. |

---

#### Step 9 — Governance and Guardrails

| | |
|---|---|
| **LLMOps Stage** | 🔴 Govern & Automate |
| **Maturity Level** | L2 → L3 |
| **Why** | Governance checklist covers approved prompts, agent versioning, evaluation gates, RBAC, and safety expectations. Each control is tagged as "Local Demo", "Foundry / Enterprise", or "Both". This demonstrates that governance is not an afterthought — it's embedded in the workflow. |
| **What it proves** | The organization has explicit controls for AI safety and compliance. |

---

#### Step 10 — GitHub Actions / Automation

| | |
|---|---|
| **LLMOps Stage** | 🔴 Govern & Automate |
| **Maturity Level** | L3 |
| **Why** | The unified **LLMOps Pipeline** (`llmops-pipeline.yml`) runs 5 connected stages on every push: (1) Unit Tests on Python 3.11+3.12, (2) Prompt validation + data integrity checks, (3) Prompt change detection via git diff, (4) Quality evaluation — 12 cases scored on 4 dimensions (relevance, personalization, grounding, policy/safety) with multi-model support, and (5) Pipeline report with summary table. Additional workflows for CI, evaluation, and Foundry smoke testing complete the automation suite. Promotion is quality-gated. This is the highest maturity level — the loop is closed, automated, and self-reinforcing. |
| **What it proves** | The LLMOps loop runs without manual intervention on every code change. |

---

## 3. Summary Matrix

| Step | Menu Title | LLMOps Stage | Stage Color | Maturity Level | Key Capability |
|---|---|---|---|---|---|
| 1 | Intro / Scenario | 🟣 Design | Purple `#7B2D8E` | L0→L1 | Problem definition |
| 2 | Prompt Management | 🔵 Build | Blue `#0078D4` | L1 | Versioned prompt assets |
| 3 | Create / Update Agent | 🔵 Build | Blue `#0078D4` | L1→L2 | Managed agent versioning |
| 4 | Baseline Run | 🟢 Test & Evaluate | Green `#13A10E` | L1 | Baseline measurement |
| 5 | Persona Personalization | 🟢 Test & Evaluate | Green `#13A10E` | L1→L2 | Context-aware orchestration |
| 6 | Multi-Model Comparison | 🟢 Test & Evaluate | Green `#13A10E` | L2 | Data-driven model selection |
| 7 | Evaluation | 🟢 Test & Evaluate | Green `#13A10E` | L2 | Structured quality scoring |
| 8 | Monitoring & Traces | 🟠 Operate | Orange `#CA5010` | L2 | Observability & tracing |
| 9 | Governance & Guardrails | 🔴 Govern & Automate | Red `#D13438` | L2→L3 | Safety & compliance controls |
| 10 | GitHub Actions | 🔴 Govern & Automate | Red `#D13438` | L3 | Automated CI/CD loop |

---

## 4. Maturity Progression Visualized

```
L0  Ad-hoc          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                     Step 1 starts here (no process)

L1  Foundational     ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                     Steps 1-4: prompts versioned, agent managed, baseline set

L2  Standardized     ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░
                     Steps 5-9: evaluation, comparison, monitoring, governance

L3  Automated        ████████████████████████████████████████
                     Step 10: CI/CD closes the loop — full automation
```

### The Journey Through the Demo

1. **Steps 1-2** (Design → Build): Establish the foundation — problem, prompts, tooling
2. **Steps 3-4** (Build → Test): Create the agent, get a baseline
3. **Steps 5-7** (Test & Evaluate): Optimise through personas, models, and evaluation
4. **Step 8** (Operate): Observe what happened — monitoring as a feedback mechanism
5. **Steps 9-10** (Govern & Automate): Lock it down, automate the loop

By the end of Step 10, the audience has seen a complete journey from **L0 (ad-hoc)** to **L3 (automated)**. The demo proves it's not just theory — every step is executable and backed by real Foundry integration.
