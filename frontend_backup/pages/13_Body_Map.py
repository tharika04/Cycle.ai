from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Body Map", page_icon="\U0001F9CD", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Pain Body Map")
st.caption(
    "Click (or drag a box over) the areas where it hurts, then save. "
    "Saved pain also appears in your symptom charts."
)

FRONT = [
    ("Head", 50, 185), ("Neck", 50, 173), ("Chest or breasts", 50, 155),
    ("Upper abdomen", 50, 132), ("Lower abdomen", 50, 105), ("Pelvic area", 50, 88),
    ("Arms", 15, 128), ("Arms", 85, 128), ("Thighs", 38, 55), ("Thighs", 62, 55),
    ("Legs", 41, 20), ("Legs", 59, 20),
]
BACK = [
    ("Head", 50, 185), ("Neck", 50, 173), ("Upper back", 50, 150),
    ("Lower back", 50, 112), ("Hips and buttocks", 50, 86),
    ("Arms", 15, 128), ("Arms", 85, 128), ("Thighs", 38, 55), ("Thighs", 62, 55),
    ("Legs", 41, 20), ("Legs", 59, 20),
]
ALL_AREAS = sorted({z[0] for z in FRONT + BACK})


def silhouette():
    fill = "rgba(230,190,190,0.45)"
    line = dict(color="rgba(150,110,110,0.8)", width=1)
    shapes = [
        dict(type="circle", x0=40, x1=60, y0=175, y1=195),
        dict(type="path", path="M 46 176 L 54 176 L 54 168 L 46 168 Z"),
        dict(type="path", path="M 30 168 L 70 168 L 64 115 L 72 85 L 28 85 L 36 115 Z"),
        dict(type="path", path="M 30 168 L 23 168 L 10 112 L 17 109 L 28 148 Z"),
        dict(type="path", path="M 70 168 L 77 168 L 90 112 L 83 109 L 72 148 Z"),
        dict(type="path", path="M 28 85 L 49 85 L 47 4 L 36 4 Z"),
        dict(type="path", path="M 51 85 L 72 85 L 64 4 L 53 4 Z"),
    ]
    for s in shapes:
        s.update(fillcolor=fill, line=line, layer="below")
    return shapes


def make_figure(zones):
    fig = go.Figure(go.Scatter(
        x=[z[1] for z in zones], y=[z[2] for z in zones], mode="markers",
        marker=dict(size=30, color="#e63946", opacity=0.55, line=dict(color="white", width=2)),
        text=[z[0] for z in zones], hovertemplate="%{text}<extra></extra>",
        selected=dict(marker=dict(color="#c1121f", opacity=1.0, size=34)),
        unselected=dict(marker=dict(opacity=0.5)),
    ))
    fig.update_layout(
        shapes=silhouette(), height=620, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(visible=False, range=[0, 100], fixedrange=True),
        yaxis=dict(visible=False, range=[0, 200], fixedrange=True, scaleanchor="x"),
        dragmode="select", clickmode="event+select", showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


view = st.radio("View", ["Front", "Back"], horizontal=True)
zones = FRONT if view == "Front" else BACK

left, right = st.columns([1, 1])

with left:
    event = st.plotly_chart(
        make_figure(zones), key="body_" + view, on_select="rerun",
        selection_mode=["points", "box"], config={"displayModeBar": False}, width="stretch",
    )

picked = set()
try:
    for p in event["selection"]["points"]:
        idx = p.get("point_index", p.get("point_number"))
        if idx is not None and 0 <= idx < len(zones):
            picked.add(zones[idx][0])
except Exception:
    pass

with right:
    extra = st.multiselect("Or add areas from a list", ALL_AREAS)
    chosen = sorted(picked | set(extra))
    if chosen:
        st.write("Selected: **" + ", ".join(chosen) + "**")
    else:
        st.info("Nothing selected yet. Click an area on the body, or pick from the list.")

    day = st.date_input("Date", value=date.today(), max_value=date.today())
    severity = st.slider("Pain severity (1 = mild, 5 = severe)", 1, 5, 3)

    if st.button("Save pain", disabled=not chosen):
        try:
            for area in chosen:
                api.add_symptom(day.isoformat(), "pain - " + area.lower(), severity, None)
            st.success("Saved pain for: " + ", ".join(chosen))
            if severity >= 5:
                st.warning(
                    "Severe pain deserves attention. If it is sudden, unusual for you, or comes with heavy "
                    "bleeding, fever, or fainting, please get medical care."
                )
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the backend. Is uvicorn running?")
        except Exception as e:
            st.error(str(e))

st.divider()
st.subheader("Your pain history")
try:
    symptoms = api.get_symptoms()
except Exception:
    symptoms = []

pain = [s for s in symptoms if s["symptom"].startswith("pain - ")]
if not pain:
    st.info("No body-map pain logged yet.")
else:
    df = pd.DataFrame(pain)
    df["area"] = df["symptom"].str.replace("pain - ", "", regex=False).str.title()
    summary = (
        df.groupby("area")
        .agg(times=("severity", "size"), avg_severity=("severity", "mean"))
        .reset_index()
        .sort_values("times", ascending=False)
    )
    fig2 = px.bar(
        summary, x="area", y="times", color="avg_severity",
        color_continuous_scale="Reds", range_color=[1, 5],
        labels={"area": "Area", "times": "Times logged", "avg_severity": "Avg severity"},
    )
    st.plotly_chart(fig2, width="stretch")
    recent = df.sort_values("date", ascending=False).head(10)[["date", "area", "severity"]]
    st.dataframe(recent, hide_index=True, width="stretch")