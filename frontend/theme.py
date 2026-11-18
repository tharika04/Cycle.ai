import inspect
import math
from pathlib import Path

import streamlit as st

HERE = Path(__file__).parent
SIDEBAR_PAGES = {"5_Chatbot.py"}

NAV = [
    ("Home", "\U0001F3E0", ["app.py"]),
    ("Calendar", "\U0001F4C5", ["pages/1_Dashboard.py"]),
    ("Track", "\u2795", ["pages/2_Log_Data.py"]),
    ("Chatbot", "\U0001F4AC", ["pages/5_Chatbot.py"]),
    ("Self-Care", "\U0001F338", ["pages/14_Self_Care.py"]),
]

TILES = [
    ("exercise", "\U0001F9D8", "Exercise & Food", ["pages/4_Diet_Exercise.py"]),
    ("meal", "\U0001F957", "Meal Planner", ["pages/12_Meal_Planner.py"]),
    ("water", "\U0001F4A7", "Daily Tracker", ["pages/8_Daily_Tracker.py"]),
    ("insight", "\U0001F50D", "Insights", ["pages/6_Insights_Report.py"]),
    ("health", "\U0001FA7A", "Health Check", ["pages/10_Health_Check.py"]),
    ("chat", "\U0001F4AC", "Ask HerRhythm", ["pages/5_Chatbot.py"]),
]

MORE = [
    ("mood", "\U0001F52E", "Mood Forecast", ["pages/8_Mood_Forecast.py"]),
    ("trends", "\U0001F4C9", "Cycle Trends", ["pages/7_Cycle_Trends.py"]),
    ("body", "\U0001F9CD", "Body Map", ["pages/13_Body_Map.py"]),
    ("remind", "\U0001F514", "Reminders", ["pages/11_Reminders.py"]),
    ("settings", "\u2699\ufe0f", "Settings", ["pages/99_Settings.py", "pages/9_Settings.py"]),
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, .stApp, [class*="css"] { font-family: 'Poppins', 'Segoe UI', sans-serif; }
.stApp { background: linear-gradient(180deg, #fff0f5 0%, #ffffff 280px); }
.block-container { padding-top: 1.2rem; padding-bottom: 7rem; max-width: 820px; }
#MainMenu, footer { visibility: hidden; } [data-testid="stBottom"] { bottom: 66px !important; }
header[data-testid="stHeader"] { background: transparent; }
h1, h2, h3 { font-weight: 700; letter-spacing: -0.01em; }

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 999px; border: none; font-weight: 600; padding: 0.55rem 1.4rem;
  background: linear-gradient(135deg, #ff6b95, #f0457a); color: #ffffff;
  box-shadow: 0 4px 14px rgba(240, 69, 122, 0.3);
}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover { filter: brightness(1.06); color: #ffffff; }
.stButton > button:disabled { opacity: 0.45; }

[data-testid="stMetric"] {
  background: #ffffff; border-radius: 18px; padding: 0.8rem 1rem;
  border: 1px solid #ffe3ec; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}
[data-testid="stForm"] {
  border-radius: 22px; border: 1px solid #ffd6e3; background: #ffffff; padding: 1rem;
}
[data-testid="stAlert"] { border-radius: 16px; }
[data-testid="stChatMessage"] { border-radius: 18px; background: #ffffff; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.stTextInput input, .stNumberInput input, .stDateInput input, [data-baseweb="select"] > div { border-radius: 14px !important; }
.stTabs [aria-selected="true"] { color: #f0457a; }

.hello-big { text-align: center; font-size: 2.8rem; font-weight: 800; margin-top: -0.5rem; line-height: 1.1; }
.tagline { text-align: center; color: #8a7f85; margin-bottom: 1rem; }
.hello-row { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.4rem; }
.avatar {
  width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #ffd166, #ff6b95); color: #ffffff; font-weight: 700; font-size: 1.3rem;
}
.hello-text { font-weight: 700; font-size: 1.25rem; }
.legend { text-align: center; font-size: 0.8rem; color: #6d6469; margin-bottom: 0.8rem; }
.legend span { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin: 0 4px 0 12px; }

.st-key-wheel { max-width: 380px; margin: 0 auto; }

[class*="st-key-card_"] {
  background: #ffffff; border-radius: 20px; padding: 1rem 1.1rem;
  border: 1px solid #ffe3ec; box-shadow: 0 3px 14px rgba(0, 0, 0, 0.05);
}

[class*="st-key-tiles"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.6rem; }
[class*="st-key-tiles"] [data-testid="stColumn"], [class*="st-key-tiles"] [data-testid="column"] {
  min-width: 0 !important; flex: 1 1 0 !important; width: auto !important;
}
[class*="st-key-tile_"] {
  border-radius: 20px; padding: 0.8rem 0.7rem 0.4rem 0.7rem; min-height: 140px;
  border: 2px solid #ffd6e3; background: #fff5f8; box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
}
.tile-icon { font-size: 2rem; line-height: 1.1; }
.tile-title { font-weight: 600; font-size: 0.82rem; margin: 0.3rem 0 0.2rem 0; line-height: 1.25; }
[class*="st-key-tile_"] a p { font-size: 0.75rem; }
[class*="st-key-tile_exercise"] { background: linear-gradient(135deg, #fff0f5, #ffe0ea); border-color: #ffb3c7; }
[class*="st-key-tile_meal"] { background: linear-gradient(135deg, #fff8ec, #ffe9cc); border-color: #ffcf99; }
[class*="st-key-tile_water"] { background: linear-gradient(135deg, #effcfa, #d9f7f2); border-color: #99e6dc; }
[class*="st-key-tile_insight"] { background: linear-gradient(135deg, #fff0f6, #ffdcea); border-color: #ffb3d1; }
[class*="st-key-tile_health"] { background: linear-gradient(135deg, #f0f5ff, #dde8ff); border-color: #b3c9ff; }
[class*="st-key-tile_chat"] { background: linear-gradient(135deg, #f8f1ff, #eadbff); border-color: #d4b8ff; }
[class*="st-key-tile_mood"] { background: linear-gradient(135deg, #f8f1ff, #eadbff); border-color: #d4b8ff; }
[class*="st-key-tile_trends"] { background: linear-gradient(135deg, #f0f5ff, #dde8ff); border-color: #b3c9ff; }
[class*="st-key-tile_body"] { background: linear-gradient(135deg, #fff0f5, #ffe0ea); border-color: #ffb3c7; }
[class*="st-key-tile_remind"] { background: linear-gradient(135deg, #fffbe8, #fff1b8); border-color: #ffe27a; }
[class*="st-key-tile_settings"] { background: linear-gradient(135deg, #f6f6f8, #e9e9ee); border-color: #d0d0d6; }

.st-key-bottomnav {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000; background: #ffffff;
  border-top: 1px solid #ffd6e3; box-shadow: 0 -4px 18px rgba(0, 0, 0, 0.07);
  padding: 0.35rem 0.5rem calc(0.35rem + env(safe-area-inset-bottom));
}
.st-key-bottomnav [data-testid="stHorizontalBlock"] {
  flex-wrap: nowrap !important; gap: 0.2rem; max-width: 820px; margin: 0 auto;
}
.st-key-bottomnav [data-testid="stColumn"], .st-key-bottomnav [data-testid="column"] {
  min-width: 0 !important; flex: 1 1 0 !important; width: auto !important;
}
.st-key-bottomnav a {
  flex-direction: column; gap: 0; justify-content: center; align-items: center;
  text-align: center; padding: 0.25rem 0; border-radius: 14px;
}
.st-key-bottomnav a p { font-size: 0.68rem; margin: 0; font-weight: 500; }
.st-key-bottomnav [data-testid="stColumn"]:nth-child(3) a,
.st-key-bottomnav [data-testid="column"]:nth-child(3) a {
  background: linear-gradient(135deg, #ff6b95, #f0457a); color: #ffffff; border-radius: 50%;
  width: 54px; height: 54px; margin: -24px auto 0 auto; box-shadow: 0 6px 16px rgba(240, 69, 122, 0.4);
}
.st-key-bottomnav [data-testid="stColumn"]:nth-child(3) a p,
.st-key-bottomnav [data-testid="column"]:nth-child(3) a p { color: #ffffff; font-size: 0.6rem; }

@media (max-width: 640px) {
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  [data-testid="stColumn"], [data-testid="column"] {
    min-width: calc(50% - 0.75rem) !important; flex: 1 1 calc(50% - 0.75rem) !important;
  }
}
</style>
"""

HIDE_SIDEBAR_NAV = '<style>[data-testid="stSidebarNav"] { display: none; }</style>'
HIDE_SIDEBAR = (
    '<style>[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], '
    '[data-testid="collapsedControl"] { display: none !important; }</style>'
)


def first_existing(candidates):
    for c in candidates:
        if (HERE / c).exists():
            return c
    return None


def apply_theme(sidebar=False):
    st.markdown(CSS + (HIDE_SIDEBAR_NAV if sidebar else HIDE_SIDEBAR), unsafe_allow_html=True)


def bottom_nav():
    with st.container(key="bottomnav"):
        cols = st.columns(5)
        for col, (label, icon, candidates) in zip(cols, NAV):
            path = first_existing(candidates)
            if path:
                with col:
                    st.page_link(path, label=label, icon=icon)


def setup(sidebar=None):
    """Call once per page, right after the login check."""
    if sidebar is None:
        caller = Path(inspect.currentframe().f_back.f_code.co_filename).name
        sidebar = caller in SIDEBAR_PAGES
    apply_theme(sidebar=sidebar)
    bottom_nav()


def tile_grid(items, key):
    avail = []
    for k, icon, title, candidates in items:
        path = first_existing(candidates)
        if path:
            avail.append((k, icon, title, path))
    with st.container(key="tiles_" + key):
        for i in range(0, len(avail), 3):
            row = avail[i:i + 3]
            cols = st.columns(3)
            for col, (k, icon, title, path) in zip(cols, row):
                with col:
                    with st.container(key="tile_" + k + "_" + key):
                        st.markdown(
                            "<div class='tile-icon'>" + icon + "</div><div class='tile-title'>" + title + "</div>",
                            unsafe_allow_html=True,
                        )
                        st.page_link(path, label="Open", icon=":material/arrow_forward:")


def _flower(cx, cy, r, petal, rot=0, n=6):
    parts = ['<g transform="translate(%s %s) rotate(%s)">' % (cx, cy, rot)]
    for i in range(n):
        parts.append(
            '<ellipse cx="0" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" transform="rotate(%.1f)"/>'
            % (-r * 0.62, r * 0.28, r * 0.55, petal, i * 360 / n)
        )
    parts.append('<circle r="%.1f" fill="#3a3336"/></g>' % (r * 0.2))
    return "".join(parts)


def floral_banner_svg():
    flowers = [
        (60, 70, 36, "#ff5c86", 0), (185, 38, 26, "#f5d5bd", 20), (300, 80, 38, "#e6dcde", 10),
        (355, 165, 24, "#ff5c86", 35), (45, 170, 26, "#f5d5bd", 15), (150, 160, 32, "#ff5c86", 5),
        (255, 165, 22, "#e6dcde", 40), (110, 25, 16, "#e6dcde", 0),
    ]
    body = "".join(_flower(*f) for f in flowers)
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 210">' + body + "</svg>"


def cycle_wheel_svg(pred):
    if pred:
        L = int(pred["avg_cycle_length"])
        P = int(pred.get("last_period_length") or pred["avg_period_length"])
        day = int(pred["day_in_cycle"])
        phase = pred["current_phase"].title()
        left = int(pred["days_until_next_period"])
        if left > 0:
            line3 = "Period in %d days" % left
        elif left == 0:
            line3 = "Period expected today"
        else:
            line3 = "%d days late" % (-left)
        line1 = "Day %d" % day
        marker = min(max(day, 1), L)
    else:
        L, P, marker = 28, 5, None
        line1, phase, line3 = "Welcome", "Add your last period", "Tap Track below"

    ov = L - 13
    fertile = set(range(ov - 5, ov + 2))
    cx = cy = 200
    R = 158
    r = 12 if L <= 38 else 10

    def pos(d):
        a = math.radians(-90 + (d - 1) * 360 / L)
        return cx + R * math.cos(a), cy + R * math.sin(a)

    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">']
    p.append(
        '<defs><radialGradient id="g" cx="50%" cy="35%" r="75%">'
        '<stop offset="0%" stop-color="#ff8fb0"/><stop offset="100%" stop-color="#f0457a"/>'
        "</radialGradient></defs>"
    )
    p.append('<circle cx="200" cy="200" r="190" fill="#f1ecee"/>')
    p.append('<circle cx="200" cy="200" r="130" fill="#ffffff"/>')
    for d in range(1, L + 1):
        x, y = pos(d)
        if pred and d <= P:
            fill, txt = "#ff4d79", "#ffffff"
        elif pred and d == ov:
            fill, txt = "#f4c542", "#ffffff"
        elif pred and d in fertile:
            fill, txt = "#8fdcb4", "#ffffff"
        else:
            fill, txt = "#ffffff", "#9a8f94"
        p.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (x, y, r, fill))
        p.append(
            '<text x="%.1f" y="%.1f" font-size="11" text-anchor="middle" fill="%s" '
            'font-family="Arial, sans-serif">%d</text>' % (x, y + 4, txt, d)
        )
    if marker:
        x, y = pos(marker)
        p.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="none" stroke="#2b2b2b" stroke-width="3"/>' % (x, y, r + 5))
    p.append('<circle cx="200" cy="200" r="108" fill="url(#g)"/>')
    p.append('<text x="200" y="190" font-size="34" font-weight="700" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif">%s</text>' % line1)
    p.append('<text x="200" y="218" font-size="17" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif">%s</text>' % phase)
    p.append('<text x="200" y="244" font-size="14" text-anchor="middle" fill="#ffe6ee" font-family="Arial, sans-serif">%s</text>' % line3)
    p.append("</svg>")
    return "".join(p)
if not any(t[0] == 'cramp' for t in TILES): TILES.append(('cramp', '\U0001F9D8', 'Cramp Relief', ['pages/15_Cramp_Relief.py']))


_setup_original = setup


def setup(sidebar=None):
    if sidebar is None:
        caller = Path(inspect.currentframe().f_back.f_code.co_filename).name
        sidebar = caller in SIDEBAR_PAGES
    _setup_original(sidebar)
    import look
    look.apply()


TILES[:0] = [t for t in MORE if t[0] == 'symptoms'] if not any(t[0] == 'symptoms' for t in TILES) else []
MORE[:] = [t for t in MORE if t[0] != 'symptoms']

if not any(t[0] == 'symptoms' for t in TILES): TILES.insert(0, ('symptoms', '\U0001F4C8', 'Symptoms', ['pages/3_Symptoms.py']))

NAV[4] = ('Profile', '\U0001F464', ['pages/16_Profile.py'])

MORE[:] = [t for t in MORE if t[0] not in ('remind', 'settings')]
