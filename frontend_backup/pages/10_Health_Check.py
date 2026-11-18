import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Health Check", page_icon="\U0001FA7A", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Cycle Health Check")
st.caption("A simple screening of your logged data against common general guidelines. It is not a diagnosis.")

try:
    res = api._get("/wellness/screening")
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

if res.get("status") != "ok":
    st.info(res.get("message", "Log your first period to run the health check."))
    st.stop()

overall = res["overall"]
if overall == "see_doctor":
    st.error("Something in your logs is worth discussing with a doctor soon.")
elif overall == "watch":
    st.warning("A few things are worth keeping an eye on.")
else:
    st.success("No flags from your logged data.")

st.caption("Cycles analyzed: " + str(res["cycles_analyzed"]))

boxes = {"see_doctor": st.error, "watch": st.warning, "ok": st.success, "info": st.info}
for f in res["findings"]:
    boxes[f["level"]]("**" + f["title"] + "**\n\n" + f["detail"])

st.caption(res["disclaimer"])