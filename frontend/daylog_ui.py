import calendar
from datetime import date, timedelta

import requests
import streamlit as st

import api_client as api

EMOJI = {
    "Calm": "\U0001F60C", "Happy": "\U0001F60A", "Energetic": "\u26A1", "Frisky": "\U0001F61C",
    "Mood swings": "\U0001F3AD", "Irritated": "\U0001F620", "Sad": "\U0001F622", "Anxious": "\U0001F630",
    "Depressed": "\U0001F61E", "Feeling guilty": "\U0001F614", "Obsessive thoughts": "\U0001F4AD",
    "Low energy": "\U0001F50B", "Apathetic": "\U0001F611", "Confused": "\U0001F615",
    "Very self-critical": "\U0001F623",
    "Everything is fine": "\U0001F44D", "Cramps": "\U0001FA78", "Tender breasts": "\U0001F497",
    "Headache": "\U0001F915", "Acne": "\U0001F534", "Backache": "\U0001F9B4", "Fatigue": "\U0001F971",
    "Cravings": "\U0001F354", "Insomnia": "\U0001F319", "Abdominal pain": "\U0001F623",
    "Vaginal itching": "\U0001F538", "Vaginal dryness": "\U0001F3DC\uFE0F", "Hot flashes": "\U0001F525",
    "Night sweats": "\U0001F4A6", "Joint pain": "\U0001F9B5",
    "No discharge": "\U0001F6AB", "Creamy": "\U0001F95B", "Watery": "\U0001F4A7", "Sticky": "\U0001F36F",
    "Egg white": "\U0001F95A", "Spotting": "\U0001FA78", "Unusual": "\u2753", "Clumpy white": "\u2601\uFE0F",
    "Gray": "\U0001F32B\uFE0F",
    "Nausea": "\U0001F922", "Bloating": "\U0001F388", "Constipation": "\U0001F9F1", "Diarrhea": "\U0001F6BD",
    "Didn't take tests": "\U0001F6AB", "Positive": "\u2795", "Negative": "\u2796", "Faint line": "\u3030\uFE0F",
    "Test: positive": "\u2795", "Test: negative": "\u2796", "Ovulation: my method": "\U0001F9ED",
    "Travel": "\u2708\uFE0F", "Stress": "\u26A1", "Meditation": "\U0001F9D8", "Journaling": "\U0001F4D3",
    "Kegel exercises": "\U0001F4AA", "Breathing exercises": "\U0001F32C\uFE0F",
    "Disease or injury": "\U0001FA79", "Alcohol": "\U0001F377",
    "Didn't exercise": "\U0001F6CB\uFE0F", "Yoga": "\U0001F9D8\u200D\u2640\uFE0F", "Gym": "\U0001F3CB\uFE0F",
    "Aerobics & dancing": "\U0001F483", "Swimming": "\U0001F3CA", "Team sports": "\U0001F3C0",
    "Running": "\U0001F3C3", "Cycling": "\U0001F6B4", "Walking": "\U0001F6B6",
    "Taken on time": "\U0001F48A", "Yesterday's pill": "\u23EE\uFE0F",
}

COLORS = {
    "mood": ("#fff1e0", "#ffe2c2", "#ff9f43"),
    "symptoms": ("#fbeaf2", "#f6d3e4", "#e8559a"),
    "discharge": ("#f0ecfc", "#e0d8f8", "#8a6fe0"),
    "digestion": ("#f7e7f4", "#efd0ea", "#c04fa8"),
    "preg_test": ("#fdf1e6", "#fbdcc2", "#f2994a"),
    "ovul_test": ("#e4f6f3", "#c6ebe5", "#2fa89a"),
    "other": ("#fff1e0", "#ffe2c2", "#ff9f43"),
    "activity": ("#e3f5e8", "#c5ebd0", "#3fb56a"),
    "oc": ("#e6f3fd", "#c9e4f9", "#3b9ae0"),
}


def _css():
    rules = [
        '[class*="st-key-dlcard_"] { background:#ffffff; border-radius:20px; padding:1rem 1rem 0.6rem 1rem;'
        ' border:1px solid #f1e6ea; box-shadow:0 3px 14px rgba(0,0,0,0.05); margin-bottom:0.8rem; }',
        '.dl-title { font-weight:700; font-size:1.05rem; margin-bottom:0.1rem; }',
        '.dl-hint { font-size:0.8rem; color:#8a7f85; margin-bottom:0.4rem; }',
        '.dl-date { text-align:center; font-weight:700; font-size:1.25rem; line-height:1.2; }',
        '.dl-sub { text-align:center; color:#8a7f85; font-size:0.85rem; }',
        '[class*="st-key-dlhead"] [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; align-items:center; }',
        '[class*="st-key-dlhead"] [data-testid="stColumn"], [class*="st-key-dlhead"] [data-testid="column"] '
        '{ min-width:0 !important; flex:1 1 0 !important; width:auto !important; }',
        '[class*="st-key-dlhead"] [data-testid="stColumn"]:nth-child(2), '
        '[class*="st-key-dlhead"] [data-testid="column"]:nth-child(2) { flex:4 1 0 !important; }',
        '[class*="st-key-dlhead"] .stButton > button { background:#ffffff; color:#1c1c1e; box-shadow:none;'
        ' border:1px solid #f1e6ea; width:42px; height:42px; padding:0; border-radius:50%; font-size:1.3rem; }',
        '.st-key-dlclose .stButton > button { background:#ffffff; color:#1c1c1e; box-shadow:none;'
        ' border:1px solid #f1e6ea; width:42px; height:42px; padding:0; border-radius:50%; font-size:1.1rem; }',
        '.st-key-dlsave { position:sticky; bottom:76px; z-index:900; padding-top:0.4rem; }',
        '.st-key-dlsave .stButton > button { width:100%; padding:0.8rem 1rem; font-size:1.05rem; }',
        '[class*="st-key-dlcard_"] button[data-testid^="stBaseButton-pills"] { border-radius:999px;'
        ' padding:0.3rem 0.85rem; font-size:0.9rem; }',
    ]
    for key, (base, border, active) in COLORS.items():
        rules.append(
            '.st-key-dlcard_%s button[data-testid^="stBaseButton-pills"] '
            '{ background:%s; border:1px solid %s; color:#2b2326; }' % (key, base, border)
        )
        rules.append(
            '.st-key-dlcard_%s button[data-testid="stBaseButton-pillsActive"] '
            '{ background:%s !important; border-color:%s !important; color:#ffffff !important; font-weight:600; }'
            % (key, active, active)
        )
    return "<style>" + "".join(rules) + "</style>"


def cycle_day(day, starts):
    earlier = [s for s in starts if s <= day]
    if not earlier:
        return None
    n = (day - max(earlier)).days + 1
    return n if n <= 60 else None


def catalog():
    if "dl_catalog" not in st.session_state:
        st.session_state["dl_catalog"] = api._get("/daylog/catalog")
    return st.session_state["dl_catalog"]


def logged_dates():
    if "dl_dates" not in st.session_state:
        try:
            st.session_state["dl_dates"] = set(api._get("/daylog/dates"))
        except Exception:
            st.session_state["dl_dates"] = set()
    return st.session_state["dl_dates"]


def _store():
    return st.session_state.setdefault("dl_store", {})


def _load(iso):
    store = _store()
    if iso not in store:
        data = api._get("/daylog/" + iso)
        store[iso] = {"tags": {k: list(v) for k, v in data["tags"].items()}, "severity": int(data["severity"])}
    return store[iso]


def _sync_pills(iso, cat, wkey):
    _store()[iso]["tags"][cat] = list(st.session_state.get(wkey) or [])


def _sync_sev(iso, wkey):
    _store()[iso]["severity"] = int(st.session_state.get(wkey, 3))


def _shift(state_key, n):
    day = date.fromisoformat(st.session_state[state_key])
    st.session_state[state_key] = min(date.today() + timedelta(days=366), day + timedelta(days=n)).isoformat()


def _close(state_key):
    st.session_state[state_key] = None


def _save(iso):
    item = _store()[iso]
    payload = {"tags": item["tags"], "severity": item["severity"]}
    try:
        r = requests.put(api.API_URL + "/daylog/" + iso, json=payload, headers=api._headers(), timeout=15)
        api._handle(r)
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is uvicorn running?")
        return
    except Exception as e:
        st.error(str(e))
        return
    st.session_state.pop("dl_dates", None)
    st.toast("Saved")
    st.success("Saved for " + iso)


def render(state_key, starts, closable=False):
    """Day log screen. The chosen day is stored as an ISO string in st.session_state[state_key]."""
    iso = st.session_state[state_key]
    day = date.fromisoformat(iso)
    st.markdown(_css(), unsafe_allow_html=True)

    try:
        cat = catalog()
        item = _load(iso)
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is uvicorn running?")
        return
    except Exception as e:
        st.error(str(e))
        return

    if closable:
        with st.container(key="dlclose"):
            st.button("\u2715", key="dl_close_btn", on_click=_close, args=(state_key,))

    cd = cycle_day(day, starts)
    sub = "Cycle day " + str(cd) if cd else day.strftime("%A")
    with st.container(key="dlhead"):
        c1, c2, c3 = st.columns(3)
        c1.button("\u2039", key="dl_prev", on_click=_shift, args=(state_key, -1))
        c2.markdown(
            "<div class='dl-date'>" + str(day.day) + " " + calendar.month_name[day.month] + " " + str(day.year)
            + "</div><div class='dl-sub'>" + sub + "</div>",
            unsafe_allow_html=True,
        )
        c3.button("\u203A", key="dl_next", on_click=_shift, args=(state_key, 1))

    q = st.text_input("Search", key="dl_search", placeholder="Search", label_visibility="collapsed").strip().lower()

    shown = 0
    for c in cat["categories"]:
        if q and q not in c["title"].lower() and not any(q in t.lower() for t in c["tags"]):
            continue
        shown += 1
        wkey = "dlp_" + iso + "_" + c["key"]
        current = [t for t in item["tags"].get(c["key"], []) if t in c["tags"]]
        with st.container(key="dlcard_" + c["key"]):
            st.markdown("<div class='dl-title'>" + c["title"] + "</div>", unsafe_allow_html=True)
            if c["hint"]:
                st.markdown("<div class='dl-hint'>" + c["hint"] + "</div>", unsafe_allow_html=True)
            st.pills(
                c["title"], c["tags"], selection_mode="multi", default=current,
                format_func=lambda t: EMOJI.get(t, "\u2022") + " " + t,
                key=wkey, label_visibility="collapsed",
                on_change=_sync_pills, args=(iso, c["key"], wkey),
            )

    if not shown:
        st.info("Nothing matches your search.")

    chosen_symptoms = [t for tags in item["tags"].values() for t in tags if t in cat["symptom_tags"]]
    if chosen_symptoms:
        with st.container(key="dlcard_symptoms_strength"):
            skey = "dls_" + iso
            st.slider(
                "How strong are your symptoms? (1 = mild, 5 = severe)", 1, 5,
                value=int(item["severity"]), key=skey, on_change=_sync_sev, args=(iso, skey),
            )

    with st.container(key="dlsave"):
        if st.button("Save", key="dl_save_" + iso):
            _save(iso)