# LLMOps Hands-on Lab Guide

> **Role**: You are a developer on the LLMOps team. Your job is to improve the
> RetailPersonlisedAgent — a product recommendation assistant for Australian
> retail brands (Kmart, Officeworks, Bunnings).

---

## Exercise 1 — Environment Setup

### 1.1 Clone the Repository

```powershell
git clone https://github.com/topnak/llmops-with-Microsoft-Foundry-v2.git
cd llmops-with-Microsoft-Foundry-v2
code .
```

### 1.2 Create a Virtual Environment

Open VS Code terminal (`Ctrl+``):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 1.3 Select the Python Interpreter

Press `Ctrl+Shift+P` → **Python: Select Interpreter** → choose `.venv`.

### 1.4 Create Your `.env` File

Copy the template and fill in your credentials:

```powershell
Copy-Item .env.example .env
```

Open `.env` and provide your Azure Service Principal credentials:

```ini
AZURE_CLIENT_ID=<your-app-id>
AZURE_CLIENT_SECRET=<your-secret>
AZURE_TENANT_ID=<your-tenant-id>
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
```

> **Don't have a Service Principal?** Ask your admin, or create one:
> ```powershell
> az login
> az ad sp create-for-rbac --name "llmops-dev-<yourname>" --role "Azure AI User" `
>   --scopes "/subscriptions/<sub-id>/resourceGroups/llmops-demo/providers/Microsoft.CognitiveServices/accounts/llmops-foundry"
> ```
> Copy the `appId`, `password`, and `tenant` into your `.env`.

### 1.5 Verify Setup

```powershell
python -c "from llmops_demo.config import PROJECT_ENDPOINT; print(f'Endpoint: {PROJECT_ENDPOINT}')"
```

You should see the Foundry endpoint printed.

**Checkpoint**: Environment is ready. ✅

---

## Exercise 2 — Explore the Codebase

### 2.1 Understand the Folder Structure

```
llmops-with-Microsoft-Foundry-v2/
├── prompts/                  ← Prompt variants (YOUR MAIN EDIT TARGET)
│   ├── baseline.txt
│   ├── cost_optimized.txt
│   ├── grounded_retail.txt
│   └── quality_optimized.txt
├── src/llmops_demo/          ← Core library (agent, eval, monitoring)
├── app/                      ← Streamlit UI (10-step demo)
├── scripts/                  ← CLI scripts for each operation
├── tests/                    ← Unit tests (26 tests)
├── data/                     ← Personas, products, eval cases
├── .github/workflows/        ← CI/CD pipelines
└── results/                  ← Generated reports & logs
```

### 2.2 Read a Prompt

Open `prompts/baseline.txt` in VS Code and read it. This is what the agent uses
as its system prompt.

### 2.3 Look at the Personas

```powershell
python scripts/seed_local_memory.py
```

This prints all 5 customer personas and 17 products. The agent personalizes
recommendations based on these.

### 2.4 Launch the Streamlit UI (Optional)

```powershell
$env:PYTHONPATH="src"
streamlit run app/demo_ui.py
```

Toggle to **Hands-on Lab** mode in the sidebar to get interactive controls.

**Checkpoint**: You understand the codebase structure. ✅

---

## Exercise 3 — Run Tests & Validate Prompts

### 3.1 Run the Test Suite

```powershell
pytest tests/ -v
```

All 26 tests should pass. These tests verify:
- Prompt loading and validation
- Persona data integrity
- Evaluation scoring logic
- Monitoring event recording
- Configuration correctness

### 3.2 Validate All Prompts

```powershell
python -c "
from llmops_demo.prompt_manager import list_prompts, validate_prompt
for p in list_prompts():
    ok, issues = validate_prompt(p)
    status = 'PASS' if ok else f'FAIL: {issues}'
    print(f'  {p}: {status}')
"
```

### 3.3 Check Prompt Checksums

```powershell
python -c "
from llmops_demo.prompt_manager import list_prompts, get_prompt_checksum
for p in list_prompts():
    print(f'  {p}: {get_prompt_checksum(p)}')
"
```

Save these checksums — they will change after you edit a prompt in Exercise 4.

**Checkpoint**: All tests pass, all prompts valid. ✅

---

## Exercise 4 — Edit a Prompt (The Core Developer Task)

This is the key LLMOps activity: **changing a prompt is like changing code**.

### 4.1 Create a New Branch

```powershell
git checkout -b improve-grounded-prompt
```

### 4.2 Edit the Prompt

Open `prompts/grounded_retail.txt` in VS Code. Make an improvement, for example:

**Before** (find a line like):
```
Recommend products from the approved catalogue only.
```

**After** (improve it):
```
Recommend products ONLY from the approved catalogue.
Always include the product price in AUD.
If the customer's budget band is "low", prioritize items under $50.
Never recommend products from stores the customer hasn't listed as preferences.
```

### 4.3 Verify the Prompt Still Validates

```powershell
python -c "
from llmops_demo.prompt_manager import validate_prompt, get_prompt_checksum
ok, issues = validate_prompt('grounded_retail')
print(f'Valid: {ok}')
print(f'New checksum: {get_prompt_checksum(\"grounded_retail\")}')
"
```

### 4.4 Run Tests Again

```powershell
pytest tests/ -v
```

All tests should still pass.

**Checkpoint**: Prompt edited, validated, tests pass. ✅

---

## Exercise 5 — Run the Agent & Evaluate

### 5.1 Create/Update the Agent in Foundry

```powershell
python scripts/update_agent_version.py --prompt grounded_retail
```

This calls Microsoft Foundry to create a new version of RetailPersonlisedAgent
with your updated prompt.

### 5.2 Run a Baseline Query

```powershell
python scripts/run_baseline.py --query "What should I buy for a kitchen renovation under $200?"
```

Check `results/baseline_result.json` for the full response.

### 5.3 Compare Models

```powershell
python scripts/compare_models.py --prompt grounded_retail --query "Recommend home office setup for a student"
```

This sends the same query to `gpt-4.1-mini` and `gpt-4.1` and shows side-by-side
results with latency.

### 5.4 Run the Evaluation Suite

```powershell
python scripts/run_eval.py --prompt grounded_retail
```

This runs 12 evaluation cases and scores responses on:
- **Relevance** — does the answer address the question?
- **Personalization** — does it use persona context?
- **Grounding** — does it stick to catalogue products?
- **Policy/Safety** — does it follow safety rules?

Review the report at `results/eval_summary.json`.

### 5.5 Compare: Before vs After

If you ran the eval with `baseline` prompt earlier, compare the scores:

```powershell
# Run baseline eval for comparison
python scripts/run_eval.py --prompt baseline
# Then compare the two eval_summary files
```

**Checkpoint**: Agent updated, evaluated, scores reviewed. ✅

---

## Exercise 6 — Commit & Watch CI/CD

### 6.1 Stage Your Changes

```powershell
git add prompts/grounded_retail.txt
git status
```

### 6.2 Commit with a Descriptive Message

```powershell
git commit -m "feat(prompt): improve grounded_retail with budget-aware recommendations

- Added price display requirement
- Added budget band filtering logic
- Added store preference constraint
- Expect improved grounding and personalization scores"
```

### 6.3 Push to GitHub

```powershell
git push -u origin improve-grounded-prompt
```

### 6.4 Create a Pull Request

Go to https://github.com/topnak/llmops-with-Microsoft-Foundry-v2/pulls and
create a PR from `improve-grounded-prompt` → `main`.

### 6.5 Watch the CI Pipeline

The **CI** workflow triggers automatically on your PR:

1. **pytest** — runs all 26 tests
2. **Prompt validation** — checks all prompts are valid and non-empty
3. **Data smoke check** — verifies personas, products, and demo data load correctly

If all checks pass, the PR shows a green checkmark.

### 6.6 Merge & Watch Evaluation

After merging to `main`:

- **CI** runs again on the merge commit
- **Evaluation** pipeline runs automatically — scores your prompt changes
- **Prompt Change Detection** pipeline detects the changed prompt file and runs
  a targeted evaluation

Check the **Actions** tab to see results and download artifacts.

**Checkpoint**: Changes pushed, CI/CD pipelines triggered. ✅

---

## Exercise 7 — Review Pipeline Results

### 7.1 Check CI Results

Go to **Actions** → **CI** → latest run. Verify:
- All tests passed
- All prompts validated
- Data smoke check passed

### 7.2 Check Evaluation Results

Go to **Actions** → **Evaluation** → latest run. Download the
`evaluation-results` artifact. It contains:
- `eval_summary.json` — scores for all 12 cases
- `eval_report.md` — human-readable report

### 7.3 Check Prompt Change Detection

Go to **Actions** → **Prompt Change Detection** → latest run. This shows:
- Which prompt files changed
- Targeted evaluation of the changed prompt
- Before/after comparison data

### 7.4 (Optional) Run Foundry Smoke Test

Go to **Actions** → **Foundry Smoke Test** → **Run workflow** (manual trigger).
This creates the agent in Foundry and runs a live baseline query.

**Checkpoint**: Pipeline results reviewed, LLMOps loop complete! ✅

---

## Summary — The LLMOps Developer Loop

```
    ┌─────────────────────────────────────────────────┐
    │                                                   │
    ▼                                                   │
 Edit Prompt                                            │
    │                                                   │
    ▼                                                   │
 Validate & Test Locally                                │
    │                                                   │
    ▼                                                   │
 Run Agent & Evaluate                                   │
    │                                                   │
    ▼                                                   │
 Commit & Push (PR)                                     │
    │                                                   │
    ├──→ CI: tests + prompt validation ──→ PR gate      │
    │                                                   │
    ▼ (merge)                                           │
 Eval Pipeline: score quality                           │
    │                                                   │
    ├──→ Prompt Change Detection: targeted eval         │
    │                                                   │
    ▼                                                   │
 Review Results ────────────────────────────────────────┘
```

**You are now operating like an LLMOps engineer.** Every prompt change goes
through versioning, testing, evaluation, and automated quality gates — just like
code changes in traditional software engineering.
