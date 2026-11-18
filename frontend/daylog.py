from datetime import date, timedelta

import requests
import streamlit as st

import api_client as api

CATALOG = [
    ("mood", "Mood", [
        ("Calm", "\U0001F60C"), ("Happy", "\U0001F60A"), ("Energetic", "\u26A1"),
        ("Mood swings", "\U0001F3AD"), ("Irritated", "\U0001F620"), ("Sad", "\U0001F622"),
        ("Anxious", "\U0001F61F"), ("Stressed", "\U0001F623"), ("Low energy", "\U0001F62A"),
        ("Confused", "\U0001F615"),
    ]),
    ("symptoms", "Symptoms", [
        ("Everything is fine", "\U0001F44D"), ("Cramps", "\U0001F525"), ("Tender breasts", "\U0001F497"),
        ("Headache", "\U0001F915"), ("Acne", "\U0001F534"), ("Backache", "\U0001F9B4"),
        ("Fatigue", "\U0001F50B"), ("Cravings", "\U0001F36B"), ("Insomnia", "\U0001F319"),
        ("Abdominal pain", "\U0001F616"), ("Dizziness", "\U0001F4AB"), ("Joint pain", "\U0001F9B5"),
    ]),
    ("discharge", "Vaginal discharge", [
        ("No discharge", "\U0001F6AB"), ("Creamy", "\U0001F95B"), ("Watery", "\U0001F4A7"),
        ("Sticky", "\U0001F36F"), ("Egg white", "\U0001F95A"), ("Spotting", "\U0001FA78"),
        ("Unusual", "\u2753"), ("Clumpy white", "\u2601\uFE0F"), ("Gray", "\U0001F32B\uFE0F"),
    ]),
    ("digestion", "Digestion and stool", [
        ("Nausea", "\U0001F922"), ("Bloating", "\U0001F388"), ("Constipation", "\U0001F9F1"),
        ("Diarrhea", "\U0001F6BD"),
    ]),
    ("pregnancy", "Pregnancy test", [
        ("Didn't take tests", "\U0001F6AB"), ("Negative", "\u2796"), ("Positive", "\u2795"),
        ("Faint line", "\u3030\uFE0F"),
    ]),
    ("ovulation", "Ovulation test", [
        ("Didn't take tests", "\U0001F6AB"), ("Test: negative", "\u2796"), ("Test: positive", "\u2795"),
        ("Ovulation: my method", "\U0001F4C6"),
    ]),
    ("other", "Other", [
        ("Travel", "\u2708\uFE0F"), ("Stress", "\u26A1"), ("Meditation", "\U0001F9D8"),
        ("Journaling", "\U0001F4D3"), ("Kegel exercises", "\U0001F4AA"),
        ("Breathing exercises", "\U0001F32C\uFE0F"), ("Disease or injury", "\U0001FA79"),
        ("Alcohol", "\U0001F377"),
    ]),
    ("activity", "Physical activity", [
        ("Didn't exercise", "\U0001F6CB\uFE0F"), ("Yoga", "\U0001F9D8"), ("Gym", "\U0001F3CB\uFE0F"),
        ("Aerobics & dancing", "\U0001F483"), ("Swimming", "\U0001F3CA"), ("Team sports", "\U0001F3C0"),
        ("Running", "\U0001F3C3"), ("Cycling", "\U0001F6B4"), ("Walking", "\U0001F6B6"),
    ]),
    ("pill", "Birth control pill", [
        ("Taken on time", "\u2705"), ("Taken late", "\u23F0"), ("Missed", "\u274C"),
    ]),
]

ICON = {name: icon for _slug, _title, opts in CATALOG for name, icon in opts}

NOTES = {
    "mood": "If a low mood lasts more than two weeks, please talk to someone you trust or a doctor.",
    "discharge": "Unusual colour or smell, itching, or pain that keeps happening is worth checking with a doctor.",
}

CSS = """
<style>
.dl-date { text-align: center; font-size: 1.5rem; font-weight: 700; line-height: 1.2; }
.dl-sub { text-align: center; color: #8a7f85; font-size: 0.9rem; }
.dl-title { font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem; }
[class*="st-key-dlhead"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; align-items: center; gap: 0.3rem; }
[class*="st-key-dlhead"] [data-testid="stColumn"], [class*="st-key-dlhead"] [data-testid="column"] {
  min-width: 0 !important; flex: 1 1 0 !important; width: auto !important; }
[class*="st-key-dlhead"] [data-testid="stColumn"]:first-child, [class*="st-key-dlhead"] [data-testid="stColumn"]:last-child { flex: 0 0 52px !important; }
[class*="st-key-dlhead"] button {
  width: 44px; height: 44px; padding: 0 !important; border-radius: 50% !important;
  background: #f3f1f2 !important; color: #222222 !important; box-shadow: none !important; font-size: 1.4rem; }
[class*="st-key-dlsearch"] input { background: #eceaeb !important; border: none !important; border-radius: 999px !important; }
[class*="st-key-dlcat_"] {
  background: #ffffff; border-radius: 22px; padding: 0.9rem 1rem 0.6rem 1rem; margin-bottom: 0.8rem;
  border: 1px solid #f1e6ea; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05); }
[class*="st-key-dlcat_"] [data-testid="stButtonGroup"] { gap: 0.4rem; flex-wrap: wrap; }
[class*="st-key-dlcat_"] [data-testid="stButtonGroup"] button { border-radius: 999px; border: none; padding: 0.45rem 0.9rem; font-weight: 500; }
.st-key-dlcat_mood [data-testid="stBaseButton-pills"] { background: #fff3e6; color: #3a2a1a; }
.st-key-dlcat_mood [data-testid="stBaseButton-pillsActive"] { background: #ff9f43; color: #ffffff; }
.st-key-dlcat_symptoms [data-testid="stBaseButton-pills"] { background: #fdeaf3; color: #3a1a2a; }
.st-key-dlcat_symptoms [data-testid="stBaseButton-pillsActive"] { background: #ee5d96; color: #ffffff; }
.st-key-dlcat_discharge [data-testid="stBaseButton-pills"] { background: #f1ecff; color: #261a3a; }
.st-key-dlcat_discharge [data-testid="stBaseButton-pillsActive"] { background: #8e6bf2; color: #ffffff; }
.st-key-dlcat_digestion [data-testid="stBaseButton-pills"] { background: #fae9f5; color: #3a1a35; }
.st-key-dlcat_digestion [data-testid="stBaseButton-pillsActive"] { background: #d94db4; color: #ffffff; }
.st-key-dlcat_pregnancy [data-testid="stBaseButton-pills"] { background: #fff1e8; color: #3a2a1a; }
.st-key-dlcat_pregnancy [data-testid="stBaseButton-pillsActive"] { background: #f4a27a; color: #ffffff; }
.st-key-dlcat_ovulation [data-testid="stBaseButton-pills"] { background: #e5f6f4; color: #1a3a36; }
.st-key-dlcat_ovulation [data-testid="stBaseButton-pillsActive"] { background: #3fb7aa; color: #ffffff; }
.st-key-dlcat_other [data-testid="stBaseButton-pills"] { background: #fff4e8; color: #3a2a1a; }
.st-key-dlcat_other [data-testid="stBaseButton-pillsActive"] { background: #f08c3c; color: #ffffff; }
.st-key-dlcat_activity [data-testid="stBaseButton-pills"] { background: #e4f6e8; color: #1a3a24; }
.st-key-dlcat_activity [data-testid="stBaseButton-pillsActive"] { background: #3dae5f; color: #ffffff; }
.st-key-dlcat_pill [data-testid="stBaseButton-pills"] { background: #e6f4ff; color: #1a2a3a; }
.st-key-dlcat_pill [data-testid="stBaseButton-pillsActive"] { background: #4aa8e8; color: #ffffff; }
</style>
"""


def _put(path, payload):
    r = requests.put(api.API_URL + path, json=payload, headers=api._headers(), timeout=api.TIMEOUT)
    return api._handle(r)


def _key(iso, slug):
    return "dl_" + iso + "_" + slug


def _save(title, key, iso):
    items = list(st.session_state.get(key) or [])
    severity = int(st.session_state.get("dl_sev_" + iso, 3))
    try:
        _put("/day/category", {"date": iso, "category": title, "items": items, "severity": severity})
        st.toast("Saved", icon="\u2705")
    except Exception as e:
        st.toast("Could not save: " + str(e)[:80])


def _resave_symptoms(iso):
    severity = int(st.session_state.get("dl_sev_" + iso, 3))
    for slug, title in (("symptoms", "Symptoms"), ("digestion", "Digestion and stool")):
        key = _key(iso, slug)
        if key in st.session_state:
            items = list(st.session_state.get(key) or [])
            try:
                _put("/day/category", {"date": iso, "category": title, "items": items, "severity": severity})
            except Exception as e:
                st.toast("Could not save: " + str(e)[:80])
                return
    st.toast("Saved", icon="\u2705")


def _shift(n):
    d = date.fromisoformat(st.session_state["dl_day"]) + timedelta(days=n)
    if d <= date.today():
        st.session_state["dl_day"] = d.isoformat()


def _to_today():
    st.session_state["dl_day"] = date.today().isoformat()


def _cycle_day(day, cycles):
    starts = sorted(date.fromisoformat(c["start_date"]) for c in cycles)
    earlier = [s for s in starts if s <= day]
    if not earlier:
        return None
    n = (day - earlier[-1]).days + 1
    return n if n <= 60 else None


def render():
    st.markdown(CSS, unsafe_allow_html=True)
    if "dl_day" not in st.session_state:
        st.session_state["dl_day"] = date.today().isoformat()
    day = date.fromisoformat(st.session_state["dl_day"])
    iso = day.isoformat()
    today = date.today()

    try:
        cycles = api.get_cycles()
        saved = api._get("/day", {"date": iso})
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is uvicorn running?")
        return
    except Exception as e:
        st.error(str(e))
        return

    selections = saved.get("selections", {})
    cd = _cycle_day(day, cycles)
    label = str(day.day) + " " + day.strftime("%B") + ("" if day.year == today.year else " " + str(day.year))
    sub = ("Cycle day " + str(cd)) if cd else "Log your day"

    with st.container(key="dlhead"):
        a, b, c = st.columns([1, 4, 1])
        a.button("\u2039", key="dl_prev", on_click=_shift, args=(-1,))
        b.markdown(
            "<div class='dl-date'>" + label + "</div><div class='dl-sub'>" + sub + "</div>",
            unsafe_allow_html=True,
        )
        c.button("\u203A", key="dl_next", on_click=_shift, args=(1,), disabled=day >= today)

    if day != today:
        st.button("Back to today", key="dl_today", on_click=_to_today)

    with st.container(key="dlsearch"):
        query = st.text_input("Search", key="dl_q", placeholder="Search", label_visibility="collapsed")
    query = (query or "").strip().lower()
    st.caption("Tap to select. Changes save automatically.")

    for slug, title, options in CATALOG:
        names = [name for name, _icon in options]
        if query and query not in title.lower() and not any(query in n.lower() for n in names):
            continue
        key = _key(iso, slug)
        with st.container(key="dlcat_" + slug):
            st.markdown("<div class='dl-title'>" + title + "</div>", unsafe_allow_html=True)
            chosen = st.pills(
                title, names, selection_mode="multi",
                default=[i for i in selections.get(title, []) if i in names],
                format_func=lambda n: ICON.get(n, "") + " " + n,
                key=key, label_visibility="collapsed",
                on_change=_save, args=(title, key, iso),
            )
            if slug == "symptoms" and chosen and chosen != ["Everything is fine"]:
                st.slider(
                    "How strong? (1 = mild, 5 = severe)", 1, 5, int(saved.get("severity", 3)),
                    key="dl_sev_" + iso, on_change=_resave_symptoms, args=(iso,),
                )
            if slug in NOTES:
                st.caption(NOTES[slug])
            if slug == "pregnancy" and chosen and "Positive" in chosen:
                st.info("Home tests can be confirmed with a doctor, who can also guide your next steps.")