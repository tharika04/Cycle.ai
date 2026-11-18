import calendar
from datetime import date, timedelta

import requests
import streamlit as st

import api_client as api

st.set_page_config(page_title="Calendar", page_icon="\U0001F4C5", layout="centered")
api.require_login(); import theme; theme.setup()

CAL_CSS = """
<style>
.cal-month { background:#ffffff; border:1px solid #ffe3ec; border-radius:20px; padding:0.8rem 0.5rem; margin-bottom:1rem; }
.cal-title { text-align:center; font-weight:700; margin-bottom:0.4rem; }
.cal-grid { display:grid; grid-template-columns:repeat(7, 1fr); row-gap:4px; text-align:center; }
.cal-wd { font-size:0.7rem; color:#9a8f94; }
.cd { display:flex; align-items:center; justify-content:center; height:42px; font-size:0.95rem; }
.cd span { display:flex; align-items:center; justify-content:center; width:38px; height:38px; border-radius:50%; }
.cd.pl span { background:#ff4d79; color:#ffffff; font-weight:600; }
.cd.pp span { background:#ffc2d1; color:#a3194a; font-weight:600; }
.cd.fw span { background:#8fdcb4; color:#0b4a2a; font-weight:600; }
.cd.ov span { background:#f4c542; color:#5a4300; font-weight:600; }
.cd.today span { box-shadow:0 0 0 2px #2b2b2b; }
.mini { padding:0.4rem 0.2rem; margin-bottom:0; border-radius:14px; }
.mini .cal-title { font-size:0.8rem; margin-bottom:0.2rem; }
.mini .cal-wd { font-size:0.55rem; }
.mini .cd { height:auto; padding:1px 0; font-size:0.6rem; }
.mini .cd span { width:100%; max-width:17px; height:auto; aspect-ratio:1 / 1; }
.cal-year { display:grid; grid-template-columns:repeat(3, 1fr); gap:0.5rem; margin-bottom:1rem; }
.cal-year-title { text-align:center; font-weight:800; font-size:1.5rem; margin:0.6rem 0; }
.cal-wdrow { display:grid; grid-template-columns:repeat(7, 1fr); text-align:center; font-size:0.7rem; color:#9a8f94; margin-bottom:0.2rem; }
[class*="st-key-calnav"] [data-testid="stHorizontalBlock"],
[class*="st-key-calmetrics"] [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:0.4rem; }
[class*="st-key-calnav"] [data-testid="stColumn"], [class*="st-key-calnav"] [data-testid="column"],
[class*="st-key-calmetrics"] [data-testid="stColumn"], [class*="st-key-calmetrics"] [data-testid="column"] {
  min-width:0 !important; flex:1 1 0 !important; width:auto !important; }
[class*="st-key-calmetrics"] [data-testid="stMetricValue"] { font-size:1.1rem; }
[class*="st-key-calmetrics"] [data-testid="stMetricLabel"] p { font-size:0.7rem; }
.st-key-editperiod a { background:linear-gradient(135deg,#ff6b95,#f0457a); border-radius:999px; justify-content:center; }
.st-key-editperiod a p { color:#ffffff; font-weight:600; }
[class*="st-key-calmonth_"] { background:#ffffff; border:1px solid #ffe3ec; border-radius:20px; padding:0.8rem 0.4rem; margin-bottom:1rem; }
[class*="st-key-calmonth_"] [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:0 !important; }
[class*="st-key-calmonth_"] [data-testid="stColumn"], [class*="st-key-calmonth_"] [data-testid="column"] {
  min-width:0 !important; flex:1 1 0 !important; width:auto !important; }
[class*="st-key-calmonth_"] button {
  width:38px !important; height:38px !important; min-height:0 !important; padding:0 !important;
  margin:0 auto !important; display:flex !important; justify-content:center; align-items:center;
  border-radius:50% !important; background:transparent !important; color:#222222 !important;
  border:none !important; box-shadow:none !important; font-weight:500; position:relative; cursor:pointer; }
[class*="st-key-calmonth_"] button p { font-size:0.95rem; margin:0; color:inherit; }
</style>
"""
st.markdown(CAL_CSS, unsafe_allow_html=True)

PHASE_TIPS = {
    "menstrual": "Rest, stay hydrated, and favor iron-rich foods. Light movement like walking helps.",
    "follicular": "Energy is rising. A good time for strength training and new projects.",
    "ovulation": "Peak energy for many people. Your fertile window is open.",
    "luteal": "Energy may dip. Magnesium-rich foods and gentle exercise can help with PMS.",
    "late": "Your period is later than predicted. Log it when it starts.",
}
WEEKDAYS = ["M", "T", "W", "T", "F", "S", "S"]
CAL = calendar.Calendar(firstweekday=0)
STATE_STYLE = {
    "pl": ("#ff4d79", "#ffffff"),
    "pp": ("#ffc2d1", "#a3194a"),
    "fw": ("#8fdcb4", "#0b4a2a"),
    "ov": ("#f4c542", "#5a4300"),
}


def add_months(d, n):
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, 1)


def shift(n):
    st.session_state["cal_offset"] = max(-24, min(12, st.session_state.get("cal_offset", 0) + n))


def reset_offset():
    st.session_state["cal_offset"] = 0


def build_marks(cycles, pred, today):
    P = int(pred["avg_period_length"])
    L = int(pred["avg_cycle_length"])
    ordered = sorted(cycles, key=lambda c: c["start_date"])
    next_original = date.fromisoformat(pred["next_period_start"])
    logged, predicted, fertile, ovulation = set(), set(), set(), set()

    def add_fertile(ov):
        ovulation.add(ov)
        for k in range(-5, 2):
            fertile.add(ov + timedelta(days=k))

    for i, c in enumerate(ordered):
        start = date.fromisoformat(c["start_date"])
        if c["end_date"]:
            end = date.fromisoformat(c["end_date"])
        else:
            end = min(start + timedelta(days=P - 1), today)
        end = max(end, start)
        d = start
        while d <= end:
            logged.add(d)
            d += timedelta(days=1)

        if i + 1 < len(ordered):
            nxt = date.fromisoformat(ordered[i + 1]["start_date"])
            if not 15 <= (nxt - start).days <= 60:
                nxt = start + timedelta(days=L)
        else:
            nxt = next_original
        add_fertile(nxt - timedelta(days=14))

    base = max(next_original, today)
    horizon = date(today.year + 1, 12, 31)
    k = 0
    while True:
        start = base + timedelta(days=k * L)
        if start > horizon:
            break
        for j in range(P):
            predicted.add(start + timedelta(days=j))
        if k >= 1:
            add_fertile(start - timedelta(days=14))
        k += 1
    return {"logged": logged, "predicted": predicted, "fertile": fertile, "ovulation": ovulation}


def day_class(d, marks):
    if d in marks["logged"]:
        return "pl"
    if d in marks["predicted"]:
        return "pp"
    if d in marks["ovulation"]:
        return "ov"
    if d in marks["fertile"]:
        return "fw"
    return ""


def month_html(year, month, marks, today, mini=False):
    parts = ['<div class="cal-month' + (" mini" if mini else "") + '">']
    title = calendar.month_name[month] + ("" if mini else " " + str(year))
    parts.append('<div class="cal-title">' + title + "</div>")
    parts.append('<div class="cal-grid">')
    for w in WEEKDAYS:
        parts.append('<div class="cal-wd">' + w + "</div>")
    for week in CAL.monthdayscalendar(year, month):
        for day in week:
            if day == 0:
                parts.append('<div class="cd"></div>')
            else:
                d = date(year, month, day)
                cls = day_class(d, marks) + (" today" if d == today else "")
                parts.append('<div class="cd ' + cls + '"><span>' + str(day) + "</span></div>")
    parts.append("</div></div>")
    return "".join(parts)


def grid_css(months, marks, today, logged):
    base = '[class*="st-key-calmonth_"] .st-key-cd_'
    groups = {"pl": [], "pp": [], "fw": [], "ov": [], "today": [], "dot": []}
    for y, m in months:
        for week in CAL.monthdayscalendar(y, m):
            for day in week:
                if day == 0:
                    continue
                d = date(y, m, day)
                iso = d.isoformat()
                cls = day_class(d, marks)
                if cls:
                    groups[cls].append(base + iso)
                if d == today:
                    groups["today"].append(base + iso)
                if iso in logged:
                    groups["dot"].append(base + iso)
    css = []
    for cls, (bg, fg) in STATE_STYLE.items():
        keys = groups[cls]
        if keys:
            css.append(",".join(k + " button" for k in keys)
                       + "{background:" + bg + " !important;color:" + fg + " !important;font-weight:600 !important;}")
            css.append(",".join(k + " button p" for k in keys) + "{color:" + fg + " !important;}")
    if groups["today"]:
        css.append(",".join(k + " button" for k in groups["today"]) + "{box-shadow:0 0 0 2px #2b2b2b !important;}")
    if groups["dot"]:
        css.append(",".join(k + " button::after" for k in groups["dot"])
                   + '{content:"";position:absolute;bottom:2px;left:50%;width:5px;height:5px;'
                     'margin-left:-2.5px;border-radius:50%;background:#6c5ce7;}')
    return "<style>" + "".join(css) + "</style>"


def open_day(d, today):
    if d > today:
        st.toast("You can only log today or earlier days.")
        return
    st.session_state["dl_day"] = d.isoformat()
    st.switch_page("pages/2_Log_Data.py")


def month_grid(year, month, marks, today):
    with st.container(key="calmonth_%d_%d" % (year, month)):
        st.markdown(
            "<div class='cal-title'>" + calendar.month_name[month] + " " + str(year) + "</div>"
            "<div class='cal-wdrow'>" + "".join("<div>" + w + "</div>" for w in WEEKDAYS) + "</div>",
            unsafe_allow_html=True,
        )
        for week in CAL.monthdayscalendar(year, month):
            cols = st.columns(7)
            for col, day in zip(cols, week):
                if day == 0:
                    continue
                d = date(year, month, day)
                if col.button(str(day), key="cd_" + d.isoformat()):
                    open_day(d, today)


st.title("Calendar")

try:
    pred = api.get_prediction()
    cycles = api.get_cycles()
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the backend. Is uvicorn running?")
    st.stop()
except Exception as e:
    st.error(str(e))
    st.stop()

if pred.get("status") != "ok" or not cycles:
    st.info("Log your first period to see your calendar.")
    st.page_link("pages/2_Log_Data.py", label="Log your last period", icon="\U0001F4DD")
    st.stop()

today = date.today()
marks = build_marks(cycles, pred, today)

with st.container(key="calmetrics"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Phase", pred["current_phase"].title())
    c2.metric("Day of cycle", pred["day_in_cycle"])
    left = pred["days_until_next_period"]
    c3.metric("Next period", str(left) + " days" if left >= 0 else str(-left) + " late")

st.info(PHASE_TIPS.get(pred["current_phase"], ""))

view = st.segmented_control("View", ["Month", "Year"], default="Month",
                            label_visibility="collapsed", key="cal_view")
view = view or "Month"

st.markdown(
    "<div class='legend'><span style='background:#ff4d79'></span>Logged period"
    "<span style='background:#ffc2d1'></span>Predicted period"
    "<span style='background:#8fdcb4'></span>Fertile window"
    "<span style='background:#f4c542'></span>Ovulation</div>",
    unsafe_allow_html=True,
)

if view == "Month":
    if "cal_offset" not in st.session_state:
        st.session_state["cal_offset"] = 0
    with st.container(key="calnav"):
        a, b, c = st.columns(3)
        a.button("\u25C0 Earlier", on_click=shift, args=(-3,), key="cal_prev")
        b.button("Today", on_click=reset_offset, key="cal_today")
        c.button("Later \u25B6", on_click=shift, args=(3,), key="cal_next")

    first = add_months(date(today.year, today.month, 1), st.session_state["cal_offset"] - 1)
    months = [(add_months(first, i).year, add_months(first, i).month) for i in range(4)]
    range_start = date(months[0][0], months[0][1], 1)
    last_y, last_m = months[-1]
    range_end = date(last_y, last_m, calendar.monthrange(last_y, last_m)[1])
    try:
        logged = set(api._get("/day/logged", {"start": range_start.isoformat(), "end": range_end.isoformat()}))
    except Exception:
        logged = set()

    st.markdown(grid_css(months, marks, today, logged), unsafe_allow_html=True)
    st.caption("Tap a date to open its log. A purple dot means something is logged that day.")
    for y, m in months:
        month_grid(y, m, marks, today)

    with st.container(key="editperiod"):
        st.page_link("pages/2_Log_Data.py", label="Edit period dates", icon="\u270F\uFE0F")
else:
    first_year = min(date.fromisoformat(c["start_date"]).year for c in cycles)
    html = ""
    for year in range(min(first_year, today.year), today.year + 2):
        html += '<div class="cal-year-title">' + str(year) + '</div><div class="cal-year">'
        for month in range(1, 13):
            html += month_html(year, month, marks, today, mini=True)
        html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

if pred["confidence"] == "low":
    st.caption("Confidence is low. Log at least 3 cycles for better predictions.")
if pred["irregular"]:
    st.warning("Your cycles look irregular. Consider talking to a doctor if this continues.")

st.caption("Red: logged period | Light red: predicted period | Green: fertile window | Yellow: ovulation")
st.caption(pred["note"])