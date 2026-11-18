from datetime import date

import requests
import streamlit as st

import api_client as api
import daylog_ui

st.set_page_config(page_title="Log Data", page_icon="\U0001F4DD", layout="centered")
api.require_login(); import theme; theme.setup()
st.title("Log Data")

try:
    cycles = api.get_cycles()
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

starts = [date.fromisoformat(c["start_date"]) for c in cycles]

period_tab, symptom_tab = st.tabs(["Period", "Symptoms & more"])

with period_tab:
    with st.form("cycle_form"):
        start = st.date_input("Period start date", value=date.today())
        has_end = st.checkbox("Period has ended")
        end = st.date_input("Period end date (used if ended is ticked)", value=date.today())
        flow = st.selectbox("Flow", ["light", "medium", "heavy"], index=1)
        save_period = st.form_submit_button("Save period")

    if save_period:
        try:
            api.add_cycle(start.isoformat(), end.isoformat() if has_end else None, flow)
            st.toast("Period saved.")
            st.rerun()
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the backend. Is uvicorn running?")
        except Exception as e:
            st.error(str(e))

    if cycles:
        st.subheader("Logged periods")
        for c in cycles:
            col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
            col1.write(c["start_date"])
            col2.write(c["end_date"] or "ongoing")
            col3.write(c["flow_level"])
            if col4.button("Delete", key="del_" + str(c["id"])):
                api.delete_cycle(c["id"])
                st.rerun()

with symptom_tab:
    if not st.session_state.get("ld_day"):
        st.session_state["ld_day"] = date.today().isoformat()
    daylog_ui.render("ld_day", starts)