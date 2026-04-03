"""
state_manager.py — Manages session state for the Streamlit app.
"""

import uuid
import streamlit as st


PHASES = ["greeting", "info_gathering", "tech_questions", "closing", "ended"]

INFO_FIELDS = [
    "Full Name",
    "Email Address",
    "Phone Number",
    "Current Location",
    "Years of Experience",
    "Desired Position(s)",
    "Tech Stack",
]


def init_session():
    """Initialize all session state variables if not already set."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "phase" not in st.session_state:
        st.session_state.phase = "greeting"
    if "collected_data" not in st.session_state:
        st.session_state.collected_data = {}
    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended = False
    if "data_saved" not in st.session_state:
        st.session_state.data_saved = False


def reset_session():
    """Clear all session state to start fresh."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()


def get_phase_label() -> str:
    return st.session_state.get("phase", "greeting")


def advance_phase():
    """Move to the next phase."""
    current = st.session_state.phase
    idx = PHASES.index(current) if current in PHASES else 0
    if idx < len(PHASES) - 1:
        st.session_state.phase = PHASES[idx + 1]


def info_completion_pct() -> float:
    """Return 0.0–1.0 representing how many info fields have been collected."""
    collected = st.session_state.get("collected_data", {})
    return len([f for f in INFO_FIELDS if f in collected]) / len(INFO_FIELDS)
