"""
app.py -- TalentScout Hiring Assistant
Run with: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="TalentScout - Hiring Assistant",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from src.state_manager import init_session, reset_session, get_phase_label, info_completion_pct
from src.llm_client import chat
from src.prompts import is_exit_intent
from src.data_handler import save_candidate

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:#0d0f14; --surface:#161a23; --border:#252a36;
  --accent:#6c8fff; --accent2:#a78bfa; --positive:#34d399;
  --text:#e8eaf0; --muted:#6b7280; --user-bg:#1e2640;
  --bot-bg:#161a23; --radius:16px;
}
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; background:var(--bg)!important; color:var(--text); }
.stApp { background:var(--bg)!important; }
.block-container { padding:2rem 1rem 6rem!important; max-width:760px!important; }
.ts-header { text-align:center; padding:2.5rem 0 1.5rem; }
.ts-logo { font-family:'DM Serif Display',serif; font-size:2.4rem; background:linear-gradient(135deg,var(--accent),var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.ts-tagline { color:var(--muted); font-size:0.88rem; margin-top:0.3rem; letter-spacing:0.08em; text-transform:uppercase; }
.ts-progress-wrap { margin:0 0 1.8rem; }
.ts-progress-label { display:flex; justify-content:space-between; font-size:0.75rem; color:var(--muted); margin-bottom:6px; }
.ts-progress-track { height:4px; background:var(--border); border-radius:99px; overflow:hidden; }
.ts-progress-fill { height:100%; background:linear-gradient(90deg,var(--accent),var(--accent2)); border-radius:99px; }
.ts-phase { display:inline-flex; align-items:center; gap:6px; background:var(--surface); border:1px solid var(--border); border-radius:99px; padding:3px 12px; font-size:0.72rem; font-weight:500; color:var(--accent); letter-spacing:0.04em; text-transform:uppercase; margin-bottom:1.2rem; }
.ts-chat { display:flex; flex-direction:column; gap:14px; margin-bottom:1rem; }
.ts-msg { display:flex; gap:12px; align-items:flex-start; animation:fadeUp 0.3s ease; }
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.ts-avatar { width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.9rem; flex-shrink:0; margin-top:2px; }
.ts-avatar-bot { background:linear-gradient(135deg,#3b4fd4,#6c8fff); }
.ts-avatar-user { background:var(--border); }
.ts-bubble { padding:12px 16px; border-radius:var(--radius); font-size:0.92rem; line-height:1.6; max-width:88%; }
.ts-bubble-bot { background:var(--bot-bg); border:1px solid var(--border); border-top-left-radius:4px; color:var(--text); }
.ts-bubble-user { background:var(--user-bg); border:1px solid #2a3560; border-top-right-radius:4px; color:var(--text); margin-left:auto; }
.ts-msg-user { flex-direction:row-reverse; }
.ts-panel { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:1rem 1.2rem; margin-top:1.5rem; font-size:0.82rem; }
.ts-panel-title { font-weight:600; color:var(--accent); font-size:0.78rem; letter-spacing:0.07em; text-transform:uppercase; margin-bottom:10px; }
.ts-panel-row { display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid var(--border); color:var(--muted); }
.ts-panel-row:last-child { border-bottom:none; }
.ts-panel-val { color:var(--text); font-weight:500; max-width:60%; text-align:right; }
.stTextInput>div>div>input { background:var(--surface)!important; border:1px solid var(--border)!important; border-radius:12px!important; color:var(--text)!important; padding:0.75rem 1rem!important; font-size:0.92rem!important; font-family:'DM Sans',sans-serif!important; }
.stTextInput>div>div>input:focus { border-color:var(--accent)!important; box-shadow:0 0 0 2px rgba(108,143,255,0.18)!important; }
.stTextInput>div>div>input::placeholder { color:var(--muted)!important; }
.stButton>button { background:linear-gradient(135deg,var(--accent),var(--accent2))!important; color:white!important; border:none!important; border-radius:10px!important; font-weight:600!important; font-family:'DM Sans',sans-serif!important; }
.stButton>button:hover { opacity:0.88!important; transform:translateY(-1px)!important; }
.ts-ended { text-align:center; padding:2rem; color:var(--positive); font-size:1rem; font-weight:500; }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

init_session()
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

def render_message(role, content):
    if role == "assistant":
        st.markdown(f'<div class="ts-msg"><div class="ts-avatar ts-avatar-bot">🎯</div><div class="ts-bubble ts-bubble-bot">{content}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ts-msg ts-msg-user"><div class="ts-avatar ts-avatar-user">👤</div><div class="ts-bubble ts-bubble-user">{content}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="ts-header"><div class="ts-logo">🎯 TalentScout</div><div class="ts-tagline">AI-Powered Candidate Screening</div></div>', unsafe_allow_html=True)

pct = info_completion_pct()
phase = get_phase_label()
phase_labels = {"greeting":"Greeting","info_gathering":"Info Gathering","tech_questions":"Technical Assessment","closing":"Wrapping Up","ended":"Complete"}

st.markdown(f"""
<div class="ts-progress-wrap">
  <div class="ts-progress-label"><span>Profile Completion</span><span>{int(pct*100)}%</span></div>
  <div class="ts-progress-track"><div class="ts-progress-fill" style="width:{int(pct*100)}%"></div></div>
</div>
<div class="ts-phase">&#9679; {phase_labels.get(phase, phase)}</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    greeting, _ = chat(
        messages=[{"role": "user", "content": "Hello, I am here for the interview."}],
        collected_data={}, phase="greeting",
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting})

st.markdown('<div class="ts-chat">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.collected_data:
    rows = "".join(f'<div class="ts-panel-row"><span>{k}</span><span class="ts-panel-val">{v}</span></div>' for k, v in st.session_state.collected_data.items())
    st.markdown(f'<div class="ts-panel"><div class="ts-panel-title">&#128203; Collected Profile</div>{rows}</div>', unsafe_allow_html=True)

if st.session_state.conversation_ended:
    st.markdown('<div class="ts-ended">&#10003; Interview session complete. Thank you!</div>', unsafe_allow_html=True)
    if st.button("Start New Interview"):
        reset_session()
        st.session_state.input_key = 0
        st.rerun()
    st.stop()

with st.container():
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Your message", placeholder="Type your response here... (type 'bye' to exit)", key=f"user_input_{st.session_state.input_key}", label_visibility="collapsed")
    with col2:
        send = st.button("Send →", use_container_width=True)

if (send or user_input) and user_input.strip():
    user_text = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_text})

    if is_exit_intent(user_text):
        farewell = "Thank you for taking the time to speak with us today! Our recruitment team will review your profile and get back to you within 3–5 business days. Wishing you all the best! 👋"
        st.session_state.messages.append({"role": "assistant", "content": farewell})
        st.session_state.conversation_ended = True
        if st.session_state.collected_data and not st.session_state.data_saved:
            st.session_state.collected_data["session_id"] = st.session_state.session_id
            save_candidate(st.session_state.collected_data)
            st.session_state.data_saved = True
        st.session_state.input_key += 1
        st.rerun()

    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.spinner("Aria is typing..."):
        try:
            reply, new_fields = chat(messages=api_messages, collected_data=st.session_state.collected_data, phase=st.session_state.phase)
        except Exception as e:
            reply = f"⚠️ Something went wrong: {str(e)}"
            new_fields = {}

    st.session_state.messages.append({"role": "assistant", "content": reply})

    if new_fields and isinstance(new_fields, dict):
        for k, v in new_fields.items():
            if k not in st.session_state.collected_data and v:
                st.session_state.collected_data[k] = v

    cd = st.session_state.collected_data
    if "Tech Stack" in cd and st.session_state.phase == "info_gathering":
        st.session_state.phase = "tech_questions"
    elif "Full Name" in cd and st.session_state.phase == "greeting":
        st.session_state.phase = "info_gathering"

    reply_lower = reply.lower()
    if any(kw in reply_lower for kw in ["3–5 business days", "3-5 business days", "our team will review", "best of luck", "take care", "goodbye"]):
        st.session_state.phase = "closing"
        if st.session_state.collected_data and not st.session_state.data_saved:
            st.session_state.collected_data["session_id"] = st.session_state.session_id
            save_candidate(st.session_state.collected_data)
            st.session_state.data_saved = True
        st.session_state.conversation_ended = True

    st.session_state.input_key += 1
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
if st.button("↺ Reset Interview"):
    reset_session()
    st.session_state.input_key = 0
    st.rerun()