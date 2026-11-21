import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
TIMEOUT = 30


def _headers():
    return {"Authorization": "Bearer " + st.session_state.get("token", "")}


def _handle(r):
    if r.status_code == 401 and "token" in st.session_state:
        del st.session_state["token"]
        st.warning("Session expired. Go to the Home page and log in again.")
        st.stop()
    if not r.ok:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(detail)
    return r.json()


def _get(path, params=None):
    return _handle(requests.get(API_URL + path, headers=_headers(), params=params, timeout=TIMEOUT))


def _post(path, payload):
    return _handle(requests.post(API_URL + path, json=payload, headers=_headers(), timeout=TIMEOUT))


def _delete(path, params=None):
    return _handle(requests.delete(API_URL + path, headers=_headers(), params=params, timeout=TIMEOUT))


def register(name, age, email, password):
    r = requests.post(
        API_URL + "/auth/register",
        json={"name": name, "age": age, "email": email, "password": password},
        timeout=TIMEOUT,
    )
    return _handle(r)


def login(email, password):
    r = requests.post(
        API_URL + "/auth/login",
        data={"username": email, "password": password},
        timeout=TIMEOUT,
    )
    return _handle(r)["access_token"]


def get_cycles():
    return _get("/cycles")


def add_cycle(start, end, flow):
    return _post("/cycles", {"start_date": start, "end_date": end, "flow_level": flow})


def delete_cycle(cycle_id):
    return _delete("/cycles/" + str(cycle_id))


def get_symptoms():
    return _get("/symptoms")


def add_symptom(day, symptom, severity, mood):
    return _post(
        "/symptoms",
        {"date": day, "symptom": symptom, "severity": severity, "mood": mood},
    )


def get_prediction():
    return _get("/predict")


def get_plan(phase, diet):
    return _get("/plan?phase=" + phase + "&diet=" + diet)


def send_message(message, language="English", conversation_id=""):
    r = requests.post(
        API_URL + "/chat",
        json={"message": message, "language": language, "conversation_id": conversation_id},
        headers=_headers(),
        timeout=60,
    )
    return _handle(r)


def get_conversations():
    return _get("/chat/conversations")


def get_chat_history(conversation_id):
    return _get("/chat/history", {"conversation_id": conversation_id})


def delete_conversation(conversation_id):
    return _delete("/chat/history", {"conversation_id": conversation_id})


def require_login():
    if "token" not in st.session_state:
        st.warning("Please log in on the Home page first.")
        st.stop()