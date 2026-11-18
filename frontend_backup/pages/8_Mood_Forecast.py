import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Mood Forecast", page_icon="\U0001F52E", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Mood and Energy Forecast")

try:
    fc = api._get("/daily/forecast")
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

if fc.get("status") != "ok":
    st.info(fc.get("message", "Log your first period on the Log Data page to get a forecast."))
    st.stop()

if fc["personalized_entries"] == 0:
    st.info("This forecast uses general patterns for each cycle phase. "
            "Log energy and mood on the Daily Tracker page to personalize it.")
else:
    st.caption("Personalized using " + str(fc["personalized_entries"]) + " of your daily logs.")

df = pd.DataFrame(fc["days"])

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["energy"], mode="lines+markers", name="Energy"))
fig.add_trace(go.Scatter(x=df["date"], y=df["mood"], mode="lines+markers", name="Mood"))
fig.update_yaxes(range=[1, 5.2], title="Score (1 to 5)")
st.plotly_chart(fig, width="stretch")

table = df[["date", "phase", "energy", "mood_label", "tip"]].copy()
table["phase"] = table["phase"].str.title()
table.columns = ["Date", "Phase", "Energy (1-5)", "Mood", "Tip"]
st.dataframe(table, hide_index=True, width="stretch")

st.caption(
    "This is an estimate from general cycle-phase patterns plus your own logs. "
    "Everyone is different, so treat it as a guide, not a prediction. Not medical advice."
)