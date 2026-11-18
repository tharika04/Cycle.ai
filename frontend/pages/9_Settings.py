import json

import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Settings", page_icon="\u2699\ufe0f", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Settings and Privacy")

st.subheader("Export my data")
st.write("Download everything HerRhythm has stored about you.")
try:
    data = api._get("/account/export")
    st.download_button(
        "Download my data (JSON)",
        data=json.dumps(data, indent=2),
        file_name="herrhythm_my_data.json",
        mime="application/json",
    )
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
except Exception as e:
    st.error(str(e))

st.divider()
st.subheader("Delete my account")
st.warning("This permanently deletes your account, periods, symptoms, and chat history. It cannot be undone.")
confirm = st.checkbox("I understand and want to delete everything")
if st.button("Delete my account", disabled=not confirm, type="primary"):
    try:
        api._delete("/account")
        st.session_state.pop("token", None)
        st.session_state.pop("chat", None)
        st.success("Your account and all data were deleted. Return to the Home page to register again.")
        st.stop()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is uvicorn running?")
    except Exception as e:
        st.error(str(e))