# LLMOps Developer Cheat Sheet

## Environment

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Set PYTHONPATH (needed for scripts)
$env:PYTHONPATH = "src"
```

## Testing

```powershell
pytest tests/ -v                     # Run all tests
pytest tests/ -k "prompt"            # Run prompt-related tests only
pytest tests/ -v --tb=short          # Shorter traceback
```

## Prompt Operations

```powershell
# List all prompts
python -c "from llmops_demo.prompt_manager import list_prompts; print(list_prompts())"

# Validate a specific prompt
python -c "from llmops_demo.prompt_manager import validate_prompt; print(validate_prompt('baseline'))"

# Get checksum (version hash)
python -c "from llmops_demo.prompt_manager import prompt_checksum; print(prompt_checksum('baseline'))"
```

## Agent Operations (requires Azure credentials)

```powershell
# Create/update agent with a prompt variant
python scripts/create_agent.py
python scripts/update_agent_version.py --prompt grounded_retail

# Run baseline query
python scripts/run_baseline.py
python scripts/run_baseline.py --query "What gift should I buy?"

# Compare models
python scripts/compare_models.py --prompt baseline
python scripts/compare_models.py --prompt grounded_retail --query "Home office setup?"
```

## Evaluation

```powershell
# Dry run (no Azure calls — scores empty responses)
python scripts/run_eval.py --prompt baseline --dry-run

# Live run (calls Foundry for each eval case)
python scripts/run_eval.py --prompt grounded_retail

# Generate final report
python scripts/export_demo_report.py
```

## Streamlit UI

```powershell
$env:PYTHONPATH = "src"
streamlit run app/demo_ui.py
# Open http://localhost:8501
# Toggle "Hands-on Lab" in sidebar for interactive mode
```

## Git Workflow

```powershell
# Create feature branch
git checkout -b improve-<prompt-name>

# Edit prompt, then...
git add prompts/<prompt-name>.txt
git commit -m "feat(prompt): describe your change"
git push -u origin improve-<prompt-name>

# Create PR on GitHub, CI runs automatically
# After merge: eval + prompt-change-detection pipelines run
```

## Pipeline Triggers

### Unified LLMOps Pipeline (5 connected stages)

Triggered on push/PR to `main`:

| Stage | Name | What it checks |
|---|---|---|
| 1 | Unit Tests | 26 pytest tests on Python 3.11 + 3.12 |
| 2 | Validate Prompts & Data | 4 prompts valid + 5 personas, 17 products, 12 eval cases |
| 3 | Detect Prompt Changes | git diff on `prompts/` directory |
| 4 | Evaluate Quality | 12 cases × 4 dimensions (relevance, personalization, grounding, safety) |
| 5 | Pipeline Report | Summary table + artifact upload |

### Prompt Release Pipeline (9 connected stages — with approval gate)

Triggered on push to `main` when `prompts/*.txt` changes (or manual dispatch):

| Stage | Name | What it does |
|---|---|---|
| 1 | Detect & Validate | Finds changed prompt, validates, runs tests |
| 2 | Eval Baseline (Live) | Scores `baseline` via Foundry: 12 cases × 4 dims |
| 3 | Eval Candidate (Live) | Scores changed prompt the same way |
| 4 | Compare & Report | Side-by-side delta table (🟢/🔴) |
| 5 | AI Feedback | GPT analyzes scores, suggests improvements |
| 6 | Approval Gate | **Pauses for manual approval** |
| 7 | Deploy to Agent | Deploys prompt to Foundry agent |
| 8 | Post-Deploy Eval | Evaluates the live deployed agent |
| 9 | Final Report | Full pre/post comparison + deployment confirmation |

### Other Workflows

| Pipeline | Trigger | What it does |
|---|---|---|
| CI | Push, PR | Tests + prompt validation + data smoke |
| Evaluation | Push to main | Eval suite (dry-run) + upload artifacts |
| Prompt Change Detection | Push to main (prompts/ changed) | Targeted eval for changed prompts |
| Foundry Smoke Test | Manual only | Live agent creation + baseline |

## Comparison & Feedback Scripts

```powershell
# Compare two eval results
python scripts/compare_eval.py \
  --baseline results/eval_baseline.json \
  --candidate results/eval_summary.json

# Get AI feedback on prompt quality
python scripts/ai_feedback.py \
  --comparison results/eval_comparison.json \
  --prompt grounded_retail

# Dry-run AI feedback (no Azure calls)
python scripts/ai_feedback.py \
  --comparison results/eval_comparison.json \
  --prompt grounded_retail --dry-run
```

## Key Files

| File | Purpose |
|---|---|
| `prompts/*.txt` | **Your main edit target** |
| `data/eval_cases.jsonl` | Evaluation test cases |
| `data/personas.json` | Customer personas |
| `scripts/compare_eval.py` | Compare two eval result files |
| `scripts/ai_feedback.py` | AI-powered prompt analysis |
| `results/` | Generated reports (git-ignored) |
| `.env` | Your credentials (git-ignored) |
| `.env.example` | Credential template |
