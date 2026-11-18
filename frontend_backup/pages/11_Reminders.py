import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Reminders", page_icon="\U0001F514", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Reminders")

try:
    data = api._get("/wellness/reminders")
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

boxes = {"late": st.warning, "period": st.info, "fertile": st.info, "log": st.info, "tip": st.success}
for r in data["reminders"]:
    boxes.get(r["kind"], st.info)("**" + r["title"] + "**\n\n" + r["message"])

st.divider()
st.subheader("Email me my reminders (optional)")
st.write("Sends today's reminders to your account email: " + data["email_hint"])
if st.button("Send reminders to my email"):
    try:
        res = api._post("/wellness/reminders/email", {})
        st.success("Sent to " + res["to"] + ". Check your inbox and spam folder.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is uvicorn running?")
    except Exception as e:
        st.error(str(e))

st.caption("Reminders are estimates based on your logs, not medical advice.")