"""
Microsoft Foundry LLMOps Demo — Streamlit UI

Run with:
    streamlit run app/demo_ui.py
"""

from __future__ import annotations

import sys
import pathlib

# Ensure project root and src are on path
_root = pathlib.Path(__file__).resolve().parent.parent
_src = _root / "src"
for _p in (_root, _src):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st

from llmops_demo.config import APP_TITLE
from llmops_demo.utils import load_demo_steps
from app.pages import STEP_RENDERERS

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🛒",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Load premium stylesheet from external CSS file
# ---------------------------------------------------------------------------
_css_path = pathlib.Path(__file__).resolve().parent / "assets" / "style.css"
if _css_path.exists():
    st.markdown(
        f"<style>{_css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Load demo step metadata
# ---------------------------------------------------------------------------
demo_steps = load_demo_steps()
total_steps = len(demo_steps)

# ---------------------------------------------------------------------------
# Session state — current step + demo mode
# ---------------------------------------------------------------------------
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = "walkthrough"


def _go_back():
    if st.session_state.current_step > 1:
        st.session_state.current_step -= 1


def _go_next():
    if st.session_state.current_step < total_steps:
        st.session_state.current_step += 1


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title(APP_TITLE)

    # Mode toggle
    _hands_on = st.toggle("Hands-on Lab", value=(st.session_state.demo_mode == "hands_on"), key="mode_toggle")
    st.session_state.demo_mode = "hands_on" if _hands_on else "walkthrough"
    _mode_caption = "Hands-on Lab — Live Foundry" if _hands_on else "Guided 20-minute demo walkthrough"
    st.caption(_mode_caption)

    st.markdown(
        '<div class="stage-legend">'
        '<span><span class="stage-swatch" style="background:#7B2D8E"></span>Design</span>'
        '<span><span class="stage-swatch" style="background:#0078D4"></span>Build</span>'
        '<span><span class="stage-swatch" style="background:#13A10E"></span>Test &amp; Eval</span>'
        '<span><span class="stage-swatch" style="background:#CA5010"></span>Operate</span>'
        '<span><span class="stage-swatch" style="background:#D13438"></span>Govern</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    for step in demo_steps:
        num = step["step_number"]
        icon = '\u2705' if num < st.session_state.current_step else '\u25b6' if num == st.session_state.current_step else '\u25cb'
        label = f"{icon} {num}. {step['title']}"
        if st.button(label, key=f"nav_{num}", use_container_width=True):
            st.session_state.current_step = num
            st.rerun()

    st.divider()
    st.caption(f"Step {st.session_state.current_step} of {total_steps}")

# ---------------------------------------------------------------------------
# Navigation bar
# ---------------------------------------------------------------------------
current_meta = demo_steps[st.session_state.current_step - 1]

# Progress bar (full width — always readable)
st.progress(st.session_state.current_step / total_steps)

# Nav row: Back | step info | Next
_STEP_COLORS = {
    1: "#7B2D8E",  2: "#0078D4",  3: "#0078D4",
    4: "#13A10E",  5: "#13A10E",  6: "#13A10E",  7: "#13A10E",
    8: "#CA5010",  9: "#D13438", 10: "#D13438",
}
_step_color = _STEP_COLORS.get(st.session_state.current_step, "#0078D4")

# Mode badge
_mode_badge_color = "#50E6FF" if st.session_state.demo_mode == "hands_on" else "#A0A0A0"
_mode_badge_label = "HANDS-ON" if st.session_state.demo_mode == "hands_on" else "WALKTHROUGH"

nav_cols = st.columns([1, 4, 1])
with nav_cols[0]:
    st.button("← Back", on_click=_go_back, disabled=st.session_state.current_step <= 1, use_container_width=True)
with nav_cols[1]:
    st.markdown(
        f"<div style='text-align:center;font-size:0.85rem;'>"
        f"<span class='mode-badge' style='background:{_mode_badge_color};'>{_mode_badge_label}</span> "
        f"<span style='display:inline-block;width:10px;height:10px;"
        f"border-radius:50%;background:{_step_color};margin-right:6px;"
        f"vertical-align:middle;'></span>"
        f"Step {st.session_state.current_step}/{total_steps} &mdash; "
        f"<strong>{current_meta['title']}</strong><br/>"
        f"<span style='opacity:0.7'>LLMOps: {current_meta['llmops_stage']} · "
        f"Foundry: {current_meta['foundry_capability']}</span></div>",
        unsafe_allow_html=True,
    )
with nav_cols[2]:
    st.button("Next →", on_click=_go_next, disabled=st.session_state.current_step >= total_steps, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Render current step
# ---------------------------------------------------------------------------
renderer = STEP_RENDERERS.get(st.session_state.current_step)
if renderer:
    renderer(current_meta)
else:
    st.error(f"No renderer for step {st.session_state.current_step}")
