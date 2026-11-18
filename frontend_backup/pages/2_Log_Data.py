from datetime import date

import requests
import streamlit as st

import api_client as api
import daylog

st.set_page_config(page_title="Track", page_icon="\u2795", layout="centered")
api.require_login(); import theme; theme.setup()

st.title("Track")

day_tab, period_tab = st.tabs(["Day log", "Period"])

with day_tab:
    daylog.render()

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
            st.success("Period saved.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the backend. Is uvicorn running?")
        except Exception as e:
            st.error(str(e))

    try:
        cycles = api.get_cycles()
    except Exception:
        cycles = []
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