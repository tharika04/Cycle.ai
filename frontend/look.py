import inspect
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

import streamlit as st

# which bottom-bar tab to highlight (1 Home, 2 Calendar, 3 Track, 4 Chatbot, 5 Profile)
ACTIVE = {
    "app.py": 1, "1_Dashboard.py": 2, "2_Log_Data.py": 3, "5_Chatbot.py": 4,
    "16_Profile.py": 5, "9_Settings.py": 5, "99_Settings.py": 5,
}


def _leaf(flip):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 190">']
    if flip:
        parts.append('<g transform="translate(120 0) scale(-1 1)">')
    parts.append('<path d="M60 186 C54 130 72 76 62 8" fill="none" stroke="#d9789c" stroke-width="2.2" stroke-linecap="round"/>')
    for i, y in enumerate(range(160, 24, -28)):
        side = -1 if i % 2 == 0 else 1
        cx = 60 + side * 13 - (i * 0.4)
        parts.append(
            '<ellipse cx="%.1f" cy="%d" rx="7.5" ry="17" fill="#e58aa9" transform="rotate(%d %.1f %d)"/>'
            % (cx, y, side * 38, cx, y)
        )
    parts.append('<ellipse cx="62" cy="10" rx="6" ry="14" fill="#e58aa9"/>')
    if flip:
        parts.append("</g>")
    parts.append("</svg>")
    return "data:image/svg+xml," + quote("".join(parts), safe="")


@lru_cache(maxsize=1)
def _leaves():
    return _leaf(False), _leaf(True)


def css(active):
    a, b = _leaves()
    rules = [
        '.stApp { background: url("%s") no-repeat right 6px bottom 84px / 84px auto, '
        'url("%s") no-repeat left 4px top 130px / 70px auto, '
        "linear-gradient(180deg, #ffe3ee 0%%, #ffd7e6 45%%, #ffe9f2 100%%) !important; "
        "background-attachment: fixed, fixed, scroll !important; }" % (a, b),
        ".block-container { max-width: 560px !important; background: transparent !important; box-shadow: none !important;"
        " margin: 0 auto !important; padding-top: 1.2rem !important; padding-left: 1.1rem !important;"
        " padding-right: 1.1rem !important; }",
        '[data-testid="stForm"], [data-testid="stMetric"], [data-testid="stPlotlyChart"], [data-testid="stDataFrame"],'
        ' [data-testid="stExpander"], [data-testid="stChatMessage"], [class*="st-key-card_"], [class*="st-key-dlcard_"]'
        " { background: rgba(255,255,255,0.74) !important; border: 1px solid rgba(255,255,255,0.95) !important;"
        " border-radius: 22px !important; box-shadow: 0 8px 24px rgba(214,90,140,0.14) !important; }",
        '[data-testid="stForm"] { padding: 1.1rem !important; }',
        '[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div'
        " { background: #fde7f0 !important; border: 1px solid #f9cfe0 !important; border-radius: 16px !important; }",
        '[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within'
        " { border-color: #e8508a !important; box-shadow: 0 0 0 3px rgba(232,80,138,0.15) !important; }",
        '.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.78); border-radius: 999px; padding: 4px; gap: 4px;'
        " border: 1px solid #fbd3e2; }",
        '.stTabs [data-baseweb="tab"] { border-radius: 999px; height: 38px; padding: 0 16px; flex: 1; justify-content: center; }',
        '.stTabs [aria-selected="true"] { background: linear-gradient(90deg,#f0457a,#d6336c) !important; }',
        '.stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span { color: #ffffff !important; font-weight: 700; }',
        '.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }',
        'button[data-testid^="stBaseButton-segmented_control"] { border-radius: 999px !important; }',
        'button[data-testid="stBaseButton-segmented_controlActive"] { background: linear-gradient(90deg,#f0457a,#d6336c) !important;'
        " color: #ffffff !important; border-color: transparent !important; }",
        '[data-testid="stAlert"] { border-radius: 18px; border: 1px solid rgba(255,255,255,0.9); }',
        "h1 { font-size: 1.7rem !important; font-weight: 800 !important; }",
        ".st-key-bottomnav { border-radius: 26px 26px 0 0 !important; background: rgba(255,255,255,0.94) !important;"
        " border-top: none !important; box-shadow: 0 -6px 24px rgba(214,90,140,0.20) !important; }",
    ]
    if active in (1, 2, 4, 5):
        rules.append(
            '.st-key-bottomnav [data-testid="stColumn"]:nth-child(%d) a, '
            '.st-key-bottomnav [data-testid="column"]:nth-child(%d) a { background: #ffe3ec; }' % (active, active)
        )
        rules.append(
            '.st-key-bottomnav [data-testid="stColumn"]:nth-child(%d) a p, '
            '.st-key-bottomnav [data-testid="column"]:nth-child(%d) a p { color: #f0457a; font-weight: 700; }' % (active, active)
        )
    return "<style>" + "".join(rules) + "</style>"


def apply():
    """Shared look for every logged-in page. Call once per page, after the theme is set up."""
    caller = None
    for fr in inspect.stack()[1:]:
        p = Path(fr.filename)
        if p.name == "app.py" or "pages" in p.parts:
            caller = p.name
            break
    st.markdown(css(ACTIVE.get(caller, 0)), unsafe_allow_html=True)