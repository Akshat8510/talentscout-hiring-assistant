import uuid
import streamlit as st

PHASES = ["greeting", "info_gathering", "tech_questions", "closing", "ended"]
INFO_FIELDS = ["Full Name", "Email Address", "Phone Number", "Current Location", "Years of Experience", "Desired Position(s)", "Tech Stack"]

def init_session():
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
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()

def get_phase_label():
    return st.session_state.get("phase", "greeting")

def info_completion_pct():
    collected = st.session_state.get("collected_data", {})
    return len([f for f in INFO_FIELDS if f in collected]) / len(INFO_FIELDS)