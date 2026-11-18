from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Daily Tracker", page_icon="\U0001F4A7", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Daily Tracker")
st.caption("Log water, sleep, exercise, energy, and mood. Targets are common general guidelines, not personal advice.")

MOODS = ["not set", "happy", "calm", "tired", "anxious", "irritable", "sad"]
TARGETS = {"water_glasses": 8, "sleep_hours": 7, "exercise_minutes": 30}

try:
    logs = api._get("/daily")
    symptoms = api.get_symptoms()
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

by_date = {l["date"]: l for l in logs}
day = st.date_input("Date", value=date.today(), max_value=date.today())
existing = by_date.get(day.isoformat(), {})


def pick(key, default):
    value = existing.get(key)
    return default if value is None else value


mood_default = existing.get("mood") if existing.get("mood") in MOODS else "not set"

with st.form("daily_form"):
    c1, c2, c3 = st.columns(3)
    water = c1.number_input("Water (glasses)", min_value=0, max_value=30, value=int(pick("water_glasses", 0)))
    sleep = c2.number_input("Sleep (hours)", min_value=0.0, max_value=24.0,
                            value=float(pick("sleep_hours", 7.0)), step=0.5)
    exercise = c3.number_input("Exercise (minutes)", min_value=0, max_value=600,
                               value=int(pick("exercise_minutes", 0)), step=5)
    energy = st.slider("Energy (1 = very low, 5 = high)", 1, 5, int(pick("energy", 3)))
    mood = st.selectbox("Mood", MOODS, index=MOODS.index(mood_default))
    saved = st.form_submit_button("Save")

if saved:
    try:
        api._post("/daily", {
            "date": day.isoformat(),
            "water_glasses": int(water),
            "sleep_hours": float(sleep),
            "exercise_minutes": int(exercise),
            "energy": int(energy),
            "mood": None if mood == "not set" else mood,
        })
        st.success("Saved.")
        logs = api._get("/daily")
        by_date = {l["date"]: l for l in logs}
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is uvicorn running?")
    except Exception as e:
        st.error(str(e))

current = by_date.get(day.isoformat())
if current:
    st.subheader("Progress for " + day.isoformat())
    cols = st.columns(3)
    items = [
        ("water_glasses", "Water", "glasses"),
        ("sleep_hours", "Sleep", "hours"),
        ("exercise_minutes", "Exercise", "minutes"),
    ]
    for col, (key, label, unit) in zip(cols, items):
        value = current.get(key) or 0
        col.write(f"{label}: {value} / {TARGETS[key]} {unit}")
        col.progress(min(float(value) / TARGETS[key], 1.0))

if logs:
    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["date"])
    recent = df[df["date"] >= pd.Timestamp(date.today() - timedelta(days=13))].sort_values("date")
    if not recent.empty:
        st.subheader("Last 14 days")
        a, b, c = st.columns(3)
        a.plotly_chart(px.bar(recent, x="date", y="water_glasses", title="Water (glasses)"), width="stretch")
        b.plotly_chart(px.line(recent, x="date", y="sleep_hours", markers=True, title="Sleep (hours)"),
                       width="stretch")
        c.plotly_chart(px.bar(recent, x="date", y="exercise_minutes", title="Exercise (minutes)"),
                       width="stretch")

st.subheader("Habit and symptom patterns")
results = []
if logs and symptoms:
    sdf = pd.DataFrame(symptoms)
    severity = sdf.groupby("date")["severity"].mean().rename("severity")
    joined = pd.DataFrame(logs).set_index("date").join(severity, how="inner")

    checks = [
        ("sleep_hours", 6, "Under 6 hours of sleep", "6+ hours of sleep"),
        ("water_glasses", 6, "Under 6 glasses of water", "6+ glasses of water"),
        ("exercise_minutes", 20, "Under 20 minutes of exercise", "20+ minutes of exercise"),
    ]
    for column, threshold, low_label, high_label in checks:
        data = joined.dropna(subset=[column, "severity"])
        low = data[data[column] < threshold]["severity"]
        high = data[data[column] >= threshold]["severity"]
        if len(low) >= 3 and len(high) >= 3:
            results.append(
                f"- **{low_label}:** average symptom severity {low.mean():.1f}/5 over {len(low)} days, "
                f"vs **{high_label}:** {high.mean():.1f}/5 over {len(high)} days."
            )

if results:
    for line in results:
        st.markdown(line)
    st.caption("These are patterns in your own data, not proof of cause. Small samples can mislead.")
else:
    st.info("Log habits and symptoms on at least 3 days in each group (for example, short vs longer sleep) "
            "to see patterns here.")