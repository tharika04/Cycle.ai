from datetime import date

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from fpdf import FPDF

import api_client as api

st.set_page_config(page_title="Insights and Report", page_icon="\U0001F4CA", layout="wide")
api.require_login(); import theme; theme.setup()
st.title("Insights and Doctor Report")

try:
    cycles = api.get_cycles()
    symptoms = api.get_symptoms()
    pred = api.get_prediction()
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

if pred.get("status") != "ok":
    st.info("Log your first period on the Log Data page to see insights.")
    st.stop()

PHASE_ORDER = ["menstrual", "follicular", "ovulation", "luteal"]
starts = sorted(date.fromisoformat(c["start_date"]) for c in cycles)


def phase_for(day):
    ovulation_day = pred["avg_cycle_length"] - 14
    if day <= pred["avg_period_length"]:
        return "menstrual"
    if day < ovulation_day - 1:
        return "follicular"
    if day <= ovulation_day + 1:
        return "ovulation"
    return "luteal"


def cycle_day(d):
    earlier = [s for s in starts if s <= d]
    if not earlier:
        return None
    n = (d - earlier[-1]).days + 1
    return n if n <= 60 else None


rows = []
for s in symptoms:
    day = cycle_day(date.fromisoformat(s["date"]))
    if day is None:
        continue
    rows.append({
        "symptom": s["symptom"],
        "severity": s["severity"],
        "day": day,
        "phase": phase_for(day),
    })
df = pd.DataFrame(rows)

insights = []
if not df.empty:
    for name, g in df.groupby("symptom"):
        top_phase = g["phase"].value_counts().idxmax()
        share = round(100 * (g["phase"] == top_phase).mean())
        insights.append(
            name.title() + ": logged " + str(len(g)) + " time(s), average severity "
            + str(round(g["severity"].mean(), 1)) + "/5, most often in the "
            + top_phase + " phase (" + str(share) + "% of entries)."
        )

st.subheader("Your cycle at a glance")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Cycles logged", pred["cycles_logged"])
c2.metric("Average cycle", str(pred["avg_cycle_length"]) + " days")
c3.metric("Average period", str(pred["avg_period_length"]) + " days")
c4.metric("Regularity", "Irregular" if pred["irregular"] else "Regular")

st.subheader("Symptom patterns")
if df.empty:
    st.info("Log some symptoms on the Log Data page to see patterns.")
else:
    for text in insights:
        st.markdown("- " + text)
    chart_data = df.groupby(["phase", "symptom"]).size().reset_index(name="count")
    fig = px.bar(
        chart_data, x="phase", y="count", color="symptom",
        category_orders={"phase": PHASE_ORDER},
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("More logged days give more reliable patterns.")


def clean(text):
    return str(text).encode("latin-1", "replace").decode("latin-1")


def build_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def heading(text):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, clean(text), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)

    def line(text):
        pdf.multi_cell(0, 6, clean(text), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "HerRhythm Health Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    line("Generated on " + date.today().isoformat())

    heading("Cycle summary")
    line("Cycles logged: " + str(pred["cycles_logged"]))
    line("Average cycle length: " + str(pred["avg_cycle_length"]) + " days")
    line("Average period length: " + str(pred["avg_period_length"]) + " days")
    line("Last period start: " + str(pred["last_period_start"]))
    line("Predicted next period: " + str(pred["next_period_start"]))
    line("Regularity: " + ("irregular pattern noticed" if pred["irregular"] else "no irregularity noticed"))
    line("Prediction confidence: " + str(pred["confidence"]))

    heading("Logged periods (most recent first)")
    for c in sorted(cycles, key=lambda x: x["start_date"], reverse=True)[:12]:
        line(c["start_date"] + " to " + (c["end_date"] or "ongoing") + " | flow: " + c["flow_level"])

    heading("Symptom patterns")
    if insights:
        for text in insights:
            line("- " + text)
    else:
        line("No symptoms logged.")

    heading("Note")
    line(
        "This summary is generated from self-reported data in HerRhythm. "
        "It is not a diagnosis. Please discuss any concerns with a doctor."
    )
    return bytes(pdf.output())


st.subheader("Doctor-ready report")
st.write("Download a one-page summary you can share with your doctor.")
st.download_button(
    "Download PDF report",
    data=build_pdf(),
    file_name="herrhythm_report.pdf",
    mime="application/pdf",
)