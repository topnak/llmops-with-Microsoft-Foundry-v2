"""Page renderers for each demo step."""

from __future__ import annotations

import json
import re
import sys
import pathlib
import traceback
from typing import Any

import streamlit as st

# Add src and project root to path
_root = pathlib.Path(__file__).resolve().parent.parent
_src = _root / "src"
for _p in (_root, _src):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from llmops_demo.config import (
    AZURE_EXISTING_AIPROJECT_ENDPOINT,
    AGENT_NAME,
    PRIMARY_MODEL,
    COMPARISON_MODELS,
    SAMPLE_QUERIES,
    RESULTS_DIR,
)
from llmops_demo.prompt_manager import list_prompts, load_prompt, validate_prompt, all_prompt_checksums
from llmops_demo.memory import load_personas, load_products, get_persona, inject_memory_into_prompt
from llmops_demo.governance import get_governance_checklist, get_presenter_governance_notes
from llmops_demo.monitoring import get_monitoring_summary
from llmops_demo.utils import load_demo_steps


# ---------------------------------------------------------------------------
# Secret-redaction helpers
# ---------------------------------------------------------------------------
_SENSITIVE_KEYS = re.compile(
    r"(secret|password|pwd|token|credential|api_key|apikey|access_key|"
    r"client_secret|connection_string|sas)",
    re.IGNORECASE,
)

_SENSITIVE_ENV_PATTERN = re.compile(
    r"(AZURE_CLIENT_SECRET|AZURE_CLIENT_ID|AZURE_TENANT_ID|"
    r"AZURE_SUBSCRIPTION_ID|SECRET|TOKEN|PASSWORD|API_KEY|CONNECTION_STRING)"
    r"\s*[=:]\s*\S+",
    re.IGNORECASE,
)


def _redact_secrets(obj: Any) -> Any:
    """Deep-redact sensitive values from dicts/lists before display."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if _SENSITIVE_KEYS.search(str(k)):
                cleaned[k] = "\u2022" * 8
            else:
                cleaned[k] = _redact_secrets(v)
        return cleaned
    if isinstance(obj, list):
        return [_redact_secrets(item) for item in obj]
    if isinstance(obj, str):
        return _SENSITIVE_ENV_PATTERN.sub(
            lambda m: m.group(1) + "=" + "\u2022" * 8, obj
        )
    return obj


def _redact_traceback(tb_text: str) -> str:
    """Remove credential values from traceback text."""
    return _SENSITIVE_ENV_PATTERN.sub(
        lambda m: m.group(1) + "=" + "\u2022" * 8, tb_text
    )


def _safe_json(data: Any) -> None:
    """Display JSON with secrets redacted."""
    st.json(_redact_secrets(data))


def _project_display_name() -> str:
    """Extract just the project name from the endpoint URL."""
    ep = AZURE_EXISTING_AIPROJECT_ENDPOINT
    if "/projects/" in ep:
        return ep.split("/projects/")[-1].rstrip("/")
    return ep[:30] + "\u2026"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_action(label: str, action_fn):
    """Run an action with friendly error handling (secrets redacted)."""
    try:
        return action_fn()
    except Exception as exc:
        st.error(f"{label} failed: {type(exc).__name__}")
        with st.expander("Technical details"):
            st.code(_redact_traceback(traceback.format_exc()))
        return None


def _is_hands_on() -> bool:
    """Return True when the UI is in hands-on lab mode."""
    return st.session_state.get("demo_mode") == "hands_on"


def _show_presenter_note(step: dict):
    """Display the presenter speaker note in an info box (walkthrough only)."""
    if _is_hands_on():
        return
    note = step.get("speaker_note", "")
    if note:
        with st.expander("\U0001f3a4 Presenter Note"):
            st.info(note)
    fallback = step.get("fallback_note", "")
    if fallback:
        with st.expander("\U0001f504 Fallback Note"):
            st.warning(fallback)


# ---------------------------------------------------------------------------
# Step 1 — Welcome
# ---------------------------------------------------------------------------

def render_step_1(step: dict):
    st.header("Welcome — Retail Personalization with LLMOps")

    if _is_hands_on():
        # Compact welcome card + verify connection
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("\U0001f916 Agent", AGENT_NAME)
        col2.metric("\u26a1 Model", PRIMARY_MODEL)
        col3.metric("\U0001f4cb Steps", "10")
        col4.metric("\u2601\ufe0f Project", _project_display_name())

        if st.button("\u2705 Verify Foundry Connection", key="verify_conn_btn"):
            with st.spinner("Connecting to Foundry..."):
                def _verify():
                    from llmops_demo.foundry_client import create_project_client
                    client = create_project_client()
                    return {"status": "connected", "endpoint": AZURE_EXISTING_AIPROJECT_ENDPOINT}
                result = _safe_action("Connection check", _verify)
            if result:
                st.success(f"Connected to Foundry project: **{_project_display_name()}**")
                _safe_json(result)
    else:
        st.markdown(
            """
A retail organization wants an intelligent assistant that can **personalize
retail recommendations** across Australian brands: **Kmart**, **Officeworks**,
and **Bunnings**.

This demo walks through the full **LLMOps lifecycle** on **Microsoft Foundry**:
prompt management \u2192 agent versioning \u2192 personalization \u2192 model comparison \u2192
evaluation \u2192 monitoring \u2192 governance \u2192 CI/CD automation.
"""
        )
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("\U0001f916 Agent", AGENT_NAME)
        col2.metric("\u26a1 Primary Model", PRIMARY_MODEL)
        col3.metric("\U0001f4cb Demo Steps", "10")
        col4.metric("\u2601\ufe0f Project", _project_display_name())

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 2 — Prompt Management
# ---------------------------------------------------------------------------

def render_step_2(step: dict):
    st.header("\U0001f4dd Prompt Management")

    if not _is_hands_on():
        st.markdown(
            "Prompts are **versioned assets**. Multiple variants exist for different "
            "operational goals. Changes to prompts affect agent behavior and must be tracked."
        )

    prompts = list_prompts()
    selected = st.selectbox("Select prompt variant", prompts, key="prompt_select")

    if selected:
        is_valid, issues = validate_prompt(selected)
        text = load_prompt(selected)

        if _is_hands_on():
            # Editable prompt text area for experimentation
            edited = st.text_area("Edit prompt (experiment live)", value=text, height=250, key="prompt_edit")
            if edited != text:
                import hashlib
                new_hash = hashlib.sha256(edited.encode()).hexdigest()[:12]
                st.info(f"Modified prompt checksum: `{new_hash}` (original differs)")
            else:
                st.code(text, language="text")
        else:
            st.code(text, language="text")

        if is_valid:
            st.success(f"Prompt '{selected}' is valid.")
        else:
            st.warning(f"Prompt issues: {', '.join(issues)}")

    if not _is_hands_on():
        st.subheader("All Prompt Checksums")
        checksums = all_prompt_checksums()
        _safe_json(checksums)

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 3 — Create / Update Agent
# ---------------------------------------------------------------------------

def render_step_3(step: dict):
    st.header("\U0001f527 Create or Update Agent in Foundry")

    if _is_hands_on():
        # Let user pick a prompt variant to use for the agent
        prompt_variant = st.selectbox(
            "Prompt variant for agent instructions", list_prompts(), key="agent_prompt_variant"
        )
    else:
        prompt_variant = None
        st.markdown(
            f"Agent versioning in Microsoft Foundry. We create or update "
            f"**{AGENT_NAME}** using a managed `PromptAgentDefinition`."
        )

    if st.button("Create or Update Agent", key="create_agent_btn"):
        with st.spinner("Connecting to Foundry..."):
            def _create():
                from llmops_demo.agent_manager import create_or_update_agent
                return create_or_update_agent()
            result = _safe_action("Agent creation", _create)
        if result:
            _safe_json(result)
            if result.get("status") == "error":
                st.error(result.get("error", "Unknown error"))
            else:
                st.success("Agent created/updated successfully.")

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 4 — Baseline Run
# ---------------------------------------------------------------------------

def render_step_4(step: dict):
    st.header("\U0001f680 Baseline Run")

    if not _is_hands_on():
        st.markdown(
            f"Run the agent with the **baseline prompt** and no persona. "
            f"Model: `{PRIMARY_MODEL}`."
        )

    query = st.selectbox(
        "Select sample query", SAMPLE_QUERIES, key="baseline_query"
    )
    custom = st.text_area("Or enter a custom query", key="baseline_custom")
    user_input = custom.strip() or query

    if st.button("Run Baseline", key="run_baseline_btn"):
        with st.spinner("Invoking agent..."):
            def _run():
                from llmops_demo.agent_runner import run_query
                from llmops_demo.monitoring import record_event
                from dataclasses import asdict
                res = run_query(user_input, prompt_name="baseline", model=PRIMARY_MODEL)
                record_event(res)
                return asdict(res)
            result = _safe_action("Baseline run", _run)
        if result:
            # Store for comparison in hands-on mode
            st.session_state["last_baseline"] = result
            st.subheader("Response")
            st.write(result.get("response_text", ""))
            with st.expander("Full result"):
                _safe_json(result)

    # Hands-on: show previous run for comparison
    if _is_hands_on():
        prev = st.session_state.get("last_baseline")
        if prev:
            with st.expander("\U0001f4cb Previous baseline response"):
                st.caption(f"Model: {prev.get('model_name', '')} | Prompt: {prev.get('prompt_variant', '')}")
                st.write(prev.get("response_text", ""))

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 5 — Persona Personalization
# ---------------------------------------------------------------------------

def render_step_5(step: dict):
    st.header("\U0001f464 Persona Personalization")

    if not _is_hands_on():
        st.markdown(
            "Inject customer persona context to observe behavior change. "
            "LLMOps includes **data + prompt + orchestration**."
        )

    personas = load_personas()
    persona_names = {p["persona_id"]: p["name"] for p in personas}
    selected_id = st.selectbox(
        "Select persona",
        list(persona_names.keys()),
        format_func=lambda x: persona_names[x],
        key="persona_select",
    )

    prompt_name = st.selectbox("Prompt variant", list_prompts(), key="persona_prompt")
    query = st.selectbox("Sample query", SAMPLE_QUERIES, key="persona_query")
    custom = st.text_area("Or custom query", key="persona_custom")
    user_input = custom.strip() or query

    if selected_id and not _is_hands_on():
        with st.expander("Persona details"):
            _safe_json(get_persona(selected_id))

    if _is_hands_on():
        col_run, col_all = st.columns(2)
        with col_run:
            run_single = st.button("Run with Persona", key="run_persona_btn", use_container_width=True)
        with col_all:
            run_all = st.button("Run All Personas", key="run_all_personas_btn", use_container_width=True)
    else:
        run_single = st.button("Run with Persona", key="run_persona_btn")
        run_all = False

    if run_single:
        with st.spinner("Invoking agent with persona..."):
            def _run():
                from llmops_demo.agent_runner import run_query
                from llmops_demo.monitoring import record_event
                from dataclasses import asdict
                res = run_query(
                    user_input,
                    prompt_name=prompt_name,
                    model=PRIMARY_MODEL,
                    persona_id=selected_id,
                )
                record_event(res)
                return asdict(res)
            result = _safe_action("Persona run", _run)
        if result:
            st.subheader("Personalized Response")
            st.write(result.get("response_text", ""))
            with st.expander("Full result"):
                _safe_json(result)

    if run_all:
        with st.spinner("Running all personas..."):
            def _run_all():
                from llmops_demo.agent_runner import run_query
                from llmops_demo.monitoring import record_event
                from dataclasses import asdict
                rows = []
                for pid, pname in persona_names.items():
                    try:
                        res = run_query(user_input, prompt_name=prompt_name, model=PRIMARY_MODEL, persona_id=pid)
                        record_event(res)
                        rows.append({"Persona": pname, "Response": res.response_text[:300], "Latency": f"{res.elapsed_seconds}s"})
                    except Exception as exc:
                        rows.append({"Persona": pname, "Response": f"Error: {type(exc).__name__}", "Latency": "-"})
                return rows
            rows = _safe_action("All personas", _run_all)
        if rows:
            st.subheader("All Persona Comparison")
            st.dataframe(rows, use_container_width=True)

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 6 — Multi-Model Comparison
# ---------------------------------------------------------------------------

def render_step_6(step: dict):
    st.header("\u2696\ufe0f Multi-Model Comparison")

    if not _is_hands_on():
        st.markdown(
            "Compare model outputs to optimize **quality, cost, and latency**."
        )

    query = st.selectbox("Sample query", SAMPLE_QUERIES, key="compare_query")
    custom = st.text_area("Or custom query", key="compare_custom")
    user_input = custom.strip() or query
    prompt_name = st.selectbox("Prompt variant", list_prompts(), key="compare_prompt")

    st.write(f"Models to compare: {', '.join(COMPARISON_MODELS)}")

    if st.button("Compare Models", key="compare_btn"):
        with st.spinner("Running comparison..."):
            def _compare():
                from llmops_demo.model_compare import compare_models
                return compare_models(user_input, prompt_name=prompt_name)
            result = _safe_action("Model comparison", _compare)
        if result:
            comparisons = result.get("comparisons", [])

            if _is_hands_on():
                # Compact dataframe view for hands-on
                rows = []
                for c in comparisons:
                    rows.append({
                        "Model": c["model"],
                        "Latency": f"{c['elapsed_seconds']}s",
                        "Status": c["status"],
                        "Response (excerpt)": (c.get("response_text", "") or "")[:200],
                    })
                st.dataframe(rows, use_container_width=True)
            else:
                # Card-based view for walkthrough
                per_row = min(2, len(comparisons)) or 1
                for row_start in range(0, len(comparisons), per_row):
                    row_items = comparisons[row_start : row_start + per_row]
                    cols = st.columns(len(row_items))
                    for i, c in enumerate(row_items):
                        with cols[i]:
                            st.subheader(c["model"])
                            m1, m2 = st.columns(2)
                            m1.metric("Latency", f"{c['elapsed_seconds']}s")
                            m2.metric("Status", c["status"])
                            st.write(c.get("response_text", "")[:500])
                            if c.get("error"):
                                st.error(c["error"])

            with st.expander("Full comparison JSON"):
                _safe_json(result)

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 7 — Evaluation
# ---------------------------------------------------------------------------

def render_step_7(step: dict):
    st.header("\U0001f4ca Evaluation")

    if not _is_hands_on():
        st.markdown(
            "Run structured evaluations to **measure quality**. "
            "Scoring: relevance, personalization, grounding, policy/safety."
        )

    prompt_name = st.selectbox("Prompt variant", list_prompts(), key="eval_prompt")
    # Hands-on defaults to live eval; walkthrough defaults to dry run
    default_dry = not _is_hands_on()
    dry_run = st.checkbox("Dry run (no Foundry calls, score empty responses)", value=default_dry, key="eval_dry")

    if st.button("Run Evaluation", key="eval_btn"):
        with st.spinner("Running evaluation..."):
            def _evaluate():
                from llmops_demo.evaluation import (
                    load_eval_cases, run_evaluation,
                    generate_eval_summary, save_eval_reports,
                )
                from llmops_demo.agent_runner import run_query

                cases = load_eval_cases()
                responses = []
                for case in cases:
                    if dry_run:
                        text = ""
                    else:
                        try:
                            res = run_query(
                                case["user_input"],
                                prompt_name=prompt_name,
                                persona_id=case.get("persona_id"),
                            )
                            text = res.response_text
                        except Exception:
                            text = ""
                    responses.append({"case": case, "response_text": text})

                results = run_evaluation(responses)
                summary = generate_eval_summary(results)
                save_eval_reports(summary)
                return summary
            summary = _safe_action("Evaluation", _evaluate)

        if summary:
            st.subheader("Average Scores")
            avgs = summary.get("averages", {})
            # Display scores in rows of 3 for better wrapping
            avg_items = list(avgs.items())
            for row_start in range(0, len(avg_items), 3):
                row_slice = avg_items[row_start : row_start + 3]
                avg_cols = st.columns(len(row_slice))
                for i, (dim, score) in enumerate(row_slice):
                    avg_cols[i].metric(dim.replace("_", " ").title(), score)

            st.subheader("Per-Case Results")
            rows = []
            for r in summary.get("results", []):
                s = r["scores"]
                rows.append({
                    "ID": r["id"],
                    "Rel": s["relevance"],
                    "Pers": s["personalization"],
                    "Grnd": s["grounding"],
                    "Pol": s["policy_safety"],
                    "Tot": s["total"],
                })
            st.dataframe(rows, use_container_width=True)

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 8 — Monitoring and Traces
# ---------------------------------------------------------------------------

def render_step_8(step: dict):
    st.header("\U0001f4c8 Monitoring and Traces")

    if not _is_hands_on():
        st.markdown(
            "Every invocation is traced: model, prompt, persona, latency, and result. "
            "Foundry provides built-in tracing. Here we show local monitoring data."
        )

    summary = get_monitoring_summary()

    if summary["total_events"] == 0:
        st.info(
            "No monitoring events recorded yet. Run some queries in earlier "
            "steps to generate monitoring data."
        )
        if not _is_hands_on():
            st.markdown(
                "**In Foundry**: The monitoring dashboard would show traces, latency "
                "distributions, error rates, token usage, and per-model breakdowns."
            )
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Events", summary["total_events"])
        col2.metric("Successes", summary["successes"])
        col3.metric("Avg Latency", f"{summary['avg_latency_seconds']}s")

        st.subheader("Event Log")
        st.dataframe(summary["events"], use_container_width=True)

        if _is_hands_on():
            col_export, col_clear = st.columns(2)
            with col_export:
                import json as _json
                csv_data = "\n".join(
                    ",".join(str(v) for v in e.values()) for e in summary["events"]
                )
                header = ",".join(summary["events"][0].keys()) if summary["events"] else ""
                st.download_button(
                    "Export CSV",
                    data=header + "\n" + csv_data,
                    file_name="monitoring_log.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_clear:
                if st.button("Clear Log", key="clear_log_btn", use_container_width=True):
                    from llmops_demo.monitoring import clear_events
                    clear_events()
                    st.rerun()

    if not _is_hands_on():
        st.markdown(
            """
**How this maps to Foundry:**
- **Traces**: Every agent invocation includes request/response tracing.
- **Metrics**: Token usage, latency percentiles, error rates.
- **Dashboards**: Azure Monitor and Application Insights integration.
"""
        )

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 9 — Governance and Guardrails
# ---------------------------------------------------------------------------

def render_step_9(step: dict):
    st.header("\U0001f6e1\ufe0f Governance and Guardrails")

    if not _is_hands_on():
        st.markdown(
            "Controls that keep AI safe and compliant — from prompt approval to "
            "evaluation gates and RBAC."
        )

    checklist = get_governance_checklist()

    if _is_hands_on():
        # Interactive checkbox form with completion score
        st.markdown("**Review each control and check off the ones in place:**")
        checked = 0
        for item in checklist:
            val = st.checkbox(item["control"], key=f"gov_{item['control']}")
            if val:
                checked += 1
        total = len(checklist)
        pct = int(checked / total * 100) if total else 0
        st.progress(pct / 100, text=f"Governance completion: {checked}/{total} ({pct}%)")
    else:
        for item in checklist:
            scope_label = {
                "local_demo": "Local Demo",
                "foundry": "Foundry / Enterprise",
                "both": "Both",
            }.get(item["scope"], item["scope"])

            with st.expander(f"{item['control']} — *{scope_label}*"):
                st.write(item["description"])
                st.caption(f"Enterprise equivalent: {item['enterprise_equivalent']}")

        st.subheader("Presenter Notes")
        st.markdown(get_presenter_governance_notes())

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step 10 — GitHub Actions / Automation
# ---------------------------------------------------------------------------

def render_step_10(step: dict):
    st.header("GitHub Actions — Closing the Loop")

    if not _is_hands_on():
        st.markdown(
            "CI/CD automates the LLMOps loop: validate prompts, run tests, "
            "evaluate quality, and gate promotions."
        )

    workflows_dir = pathlib.Path(__file__).resolve().parent.parent / ".github" / "workflows"
    if workflows_dir.exists():
        for wf in sorted(workflows_dir.glob("*.yml")):
            with st.expander(f"Workflow: {wf.name}"):
                st.code(wf.read_text(encoding="utf-8"), language="yaml")
    else:
        st.warning("Workflow files not found. Expected at .github/workflows/")

    if not _is_hands_on():
        st.markdown(
            """
### The LLMOps Automation Loop

```
Prompt Change → CI Validation → Evaluation → Quality Gate → Promotion
     ↑                                                          |
     └──────────── Monitoring Feedback ←────────────────────────┘
```
"""
        )

    if _is_hands_on():
        st.divider()
        if st.button("Run Smoke Test", key="smoke_test_btn"):
            with st.spinner("Running smoke test..."):
                def _smoke():
                    from llmops_demo.agent_runner import run_query
                    res = run_query("What are today's deals?", prompt_name="baseline", model=PRIMARY_MODEL)
                    return res.status
                status = _safe_action("Smoke test", _smoke)
            if status == "success":
                st.success("Smoke test passed!")
            elif status:
                st.error(f"Smoke test returned: {status}")

        # Session summary
        summary = get_monitoring_summary()
        if summary["total_events"] > 0:
            st.subheader("Session Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Runs", summary["total_events"])
            c2.metric("Successes", summary["successes"])
            c3.metric("Avg Latency", f"{summary['avg_latency_seconds']}s")

    st.success("\U0001f389 LLMOps loop complete! The full cycle is covered.")

    _show_presenter_note(step)


# ---------------------------------------------------------------------------
# Step renderer dispatch
# ---------------------------------------------------------------------------

STEP_RENDERERS = {
    1: render_step_1,
    2: render_step_2,
    3: render_step_3,
    4: render_step_4,
    5: render_step_5,
    6: render_step_6,
    7: render_step_7,
    8: render_step_8,
    9: render_step_9,
    10: render_step_10,
}
