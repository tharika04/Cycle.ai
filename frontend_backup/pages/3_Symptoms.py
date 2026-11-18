import pandas as pd
import plotly.express as px
import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Symptoms", page_icon="\U0001F4C8", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Symptom Insights")

try:
    data = api.get_symptoms()
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

if not data:
    st.info("No symptoms logged yet. Add some on the Log Data page.")
    st.stop()

df = pd.DataFrame(data)
df["date"] = pd.to_datetime(df["date"])

summary = (
    df.groupby("symptom")
    .agg(times_logged=("severity", "size"), avg_severity=("severity", "mean"))
    .reset_index()
    .sort_values("times_logged", ascending=False)
)

st.subheader("Most frequent symptoms")
fig_bar = px.bar(
    summary, x="symptom", y="times_logged", color="avg_severity",
    color_continuous_scale="Reds", range_color=[1, 5],
)
st.plotly_chart(fig_bar, width="stretch")

st.subheader("Severity over time")
fig_line = px.line(df.sort_values("date"), x="date", y="severity", color="symptom", markers=True)
fig_line.update_yaxes(range=[0, 5.5])
st.plotly_chart(fig_line, width="stretch")

st.subheader("Symptom heatmap (max severity per day)")
heat = df.pivot_table(index="symptom", columns=df["date"].dt.date, values="severity", aggfunc="max")
fig_heat = px.imshow(heat, color_continuous_scale="Reds", aspect="auto", zmin=1, zmax=5)
st.plotly_chart(fig_heat, width="stretch")