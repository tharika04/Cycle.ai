import uuid

import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Chatbot", page_icon="\U0001F4AC", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Ask HerRhythm")
st.caption("General information only, not medical advice. For urgent symptoms, see a doctor.")

LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"]

SUGGESTIONS = {
    "menstrual": ["How can I ease my cramps?", "What should I eat during my period?", "Is my flow normal?"],
    "follicular": ["What workouts suit this phase?", "Why is my energy rising?", "What should I eat today?"],
    "ovulation": ["What is my fertile window?", "What are signs of ovulation?", "What should I eat today?"],
    "luteal": ["How can I reduce PMS?", "Why do I crave sugar before my period?", "What should I eat today?"],
}


def new_id():
    return uuid.uuid4().hex


def start_new_chat():
    st.session_state["conv_id"] = new_id()
    st.session_state["chat"] = []


def open_chat(conv_id):
    try:
        rows = api.get_chat_history(conv_id)
    except Exception:
        rows = []
    chat = []
    for r in rows:
        chat.append(("user", r["message"]))
        chat.append(("assistant", r["response"]))
    st.session_state["conv_id"] = conv_id
    st.session_state["chat"] = chat


def refresh_convs():
    """Reload the past-chats list from the backend. Called only when it can change."""
    try:
        st.session_state["convs"] = api.get_conversations()
    except Exception:
        st.session_state.setdefault("convs", [])


if "conv_id" not in st.session_state:
    start_new_chat()

# Current cycle phase: fetched once per session, not on every rerun.
if "phase" not in st.session_state:
    phase = "follicular"
    try:
        pred = api.get_prediction()
        if pred.get("status") == "ok":
            phase = "luteal" if pred["current_phase"] == "late" else pred["current_phase"]
    except Exception:
        pass
    st.session_state["phase"] = phase
phase = st.session_state["phase"]

# ---- Sidebar ----
language = st.sidebar.selectbox("Reply language", LANGUAGES)

if st.sidebar.button("New chat", type="primary", use_container_width=True):
    start_new_chat()
    st.rerun()

if st.sidebar.button("Delete this chat", use_container_width=True):
    try:
        api.delete_conversation(st.session_state["conv_id"])
    except Exception:
        pass
    refresh_convs()
    start_new_chat()
    st.rerun()

st.sidebar.markdown("**Past chats**")
if "convs" not in st.session_state:
    refresh_convs()
convs = st.session_state["convs"]
for c in convs[:10]:
    title = c["title"] or "Chat"
    if c["id"] == "legacy":
        title = "Earlier chats: " + title
    if c["id"] == st.session_state["conv_id"]:
        title = "> " + title
    if st.sidebar.button(title, key="conv_" + c["id"], use_container_width=True):
        open_chat(c["id"])
        st.rerun()

# ---- Main area ----
if not st.session_state["chat"]:
    st.info("New chat. Pick a quick question below or type your own.")

for role, text in st.session_state["chat"]:
    with st.chat_message(role):
        st.markdown(text)

st.write("Quick questions:")
options = SUGGESTIONS[phase]
cols = st.columns(len(options))
for i, q in enumerate(options):
    if cols[i].button(q, key="sugg_" + str(i)):
        st.session_state["pending"] = q
        st.rerun()

typed = st.chat_input("Ask a question about your cycle or health")
prompt = typed or st.session_state.pop("pending", None)

if prompt:
    st.session_state["chat"].append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = api.send_message(prompt, language, st.session_state["conv_id"])["response"]
            except requests.exceptions.Timeout:
                reply = "That took too long. Please try again."
            except requests.exceptions.ConnectionError:
                reply = "Cannot reach the backend. Is uvicorn running?"
            except Exception as e:
                reply = "Error: " + str(e)
        st.markdown(reply)
    st.session_state["chat"].append(("assistant", reply))
    if len(st.session_state["chat"]) == 2:
        # First message of a new chat: the past-chats list now has a new entry.
        refresh_convs()
        st.rerun()