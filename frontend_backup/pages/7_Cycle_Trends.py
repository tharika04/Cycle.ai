from datetime import date

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Cycle Trends", page_icon="\U0001F4C9", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Cycle Trends")

try:
    cycles = api.get_cycles()
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

starts = sorted(date.fromisoformat(c["start_date"]) for c in cycles)
if len(starts) < 2:
    st.info("Log at least 2 periods on the Log Data page to see cycle length trends.")
    st.stop()

rows = [{"cycle_start": a, "length": (b - a).days} for a, b in zip(starts, starts[1:])]
df = pd.DataFrame(rows)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average length", f"{df['length'].mean():.1f} days")
c2.metric("Shortest", f"{df['length'].min()} days")
c3.metric("Longest", f"{df['length'].max()} days")
c4.metric("Variation", f"{df['length'].max() - df['length'].min()} days")

fig = go.Figure()
fig.add_hrect(
    y0=21, y1=35, fillcolor="green", opacity=0.12, line_width=0,
    annotation_text="Typical range (21-35 days)", annotation_position="top left",
)
fig.add_trace(go.Scatter(x=df["cycle_start"], y=df["length"], mode="lines+markers", name="Cycle length"))
fig.update_yaxes(title="Days", range=[min(15, df["length"].min() - 3), max(40, df["length"].max() + 3)])
fig.update_xaxes(title="Cycle start date")
st.plotly_chart(fig, width="stretch")

outside = df[(df["length"] < 21) | (df["length"] > 35)]
if not outside.empty:
    st.warning(
        str(len(outside)) + " cycle(s) were outside the 21-35 day range. "
        "If this keeps happening, consider talking to a doctor."
    )
else:
    st.success("All your logged cycles are inside the typical 21-35 day range.")

st.caption("The typical range is for adults; teens can vary more. Not medical advice.")