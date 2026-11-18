import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Diet and Exercise", page_icon="\U0001F957", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Diet and Exercise Plan")

PHASES = ["menstrual", "follicular", "ovulation", "luteal"]

current = "follicular"
try:
    pred = api.get_prediction()
    if pred.get("status") == "ok":
        current = "luteal" if pred["current_phase"] == "late" else pred["current_phase"]
        st.caption("Your current phase: " + current.title())
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception:
    pass

col_a, col_b = st.columns(2)
phase = col_a.selectbox("Cycle phase", PHASES, index=PHASES.index(current), format_func=str.title)
diet = col_b.radio("Diet preference", ["vegetarian", "non-vegetarian", "vegan"], horizontal=True)

try:
    plan = api.get_plan(phase, diet)
except Exception as e:
    st.error(str(e))
    st.stop()

st.subheader(plan["title"])
st.info(plan["focus"])

left, right = st.columns(2)

with left:
    st.markdown("### What to eat")
    for item in plan["eat"]:
        st.markdown("- " + item)
    st.markdown("### Go easy on")
    for item in plan["limit"]:
        st.markdown("- " + item)

with right:
    ex = plan["exercise"]
    st.markdown("### Exercise")
    st.markdown("**Intensity:** " + ex["intensity"])
    st.markdown("**Duration:** " + ex["duration"])
    for item in ex["activities"]:
        st.markdown("- " + item)
    st.markdown("### Tips")
    for item in plan["tips"]:
        st.markdown("- " + item)

st.caption(plan["disclaimer"])
