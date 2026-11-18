import html

import streamlit as st

import api_client as api

st.set_page_config(page_title="Profile", page_icon="\U0001F464", layout="centered")
api.require_login(); import theme; theme.setup()

CSS = """
<style>
.pf { display:flex; flex-direction:column; align-items:center; text-align:center; margin:0.4rem 0 1.2rem 0; }
.pf .av { width:92px; height:92px; border-radius:50%; margin:0 0 0.7rem 0; display:flex; align-items:center;
  justify-content:center; background:linear-gradient(135deg,#ffcf9f,#ff8fb0); color:#fff; font-weight:800;
  font-size:2.4rem; border:4px solid #ffffff; box-shadow:0 8px 20px rgba(214,90,140,0.28); }
.pf .nm { font-weight:800; font-size:1.4rem; line-height:1.2; }
.pf .em { color:#8a7f85; font-size:0.9rem; margin-top:0.15rem; }
.st-key-profmenu, .st-key-proflogout { width:100%; }
.st-key-profmenu [data-testid="stPageLink"] { width:100% !important; }
.st-key-profmenu a { display:flex !important; align-items:center; justify-content:flex-start !important; gap:14px;
  width:100% !important; box-sizing:border-box; min-height:54px; padding:0.7rem 1.1rem; margin-bottom:0.5rem;
  background:rgba(255,255,255,0.84); border-radius:16px; box-shadow:0 6px 16px rgba(214,90,140,0.12); }
.st-key-profmenu a [data-testid="stIconEmoji"], .st-key-profmenu a [data-testid="stIconMaterial"]
  { width:30px; flex:none; text-align:center; font-size:1.25rem; }
.st-key-profmenu a p { margin:0; font-weight:600; text-align:left; }
.st-key-profmenu a::after { content:"\\203A"; margin-left:auto; font-size:1.5rem; line-height:1; color:#a08894; }
.st-key-proflogout .stButton { width:100%; }
.st-key-proflogout .stButton > button { width:100%; min-height:50px; }
</style>
"""

prof = st.session_state.get("profile")
if prof is None:
    try:
        prof = api._get("/account/export")["profile"]
    except Exception:
        prof = {"name": "", "email": ""}
    st.session_state["profile"] = prof
name = prof.get("name") or ""
email = prof.get("email") or ""

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(
    "<div class='pf'><div class='av'>" + html.escape((name[:1] or "H").upper()) + "</div>"
    "<div class='nm'>" + html.escape(name or "Your profile") + "</div>"
    "<div class='em'>" + html.escape(email) + "</div></div>",
    unsafe_allow_html=True,
)

rows = [
    ("Cycle History", "\U0001F552", ["pages/2_Log_Data.py"]),
    ("Health Reports", "\U0001F4CB", ["pages/6_Insights_Report.py"]),
    ("Health Check", "\U0001FA7A", ["pages/10_Health_Check.py"]),
    ("Reminders", "\U0001F514", ["pages/11_Reminders.py"]),
    ("Settings", "\u2699\uFE0F", ["pages/99_Settings.py", "pages/9_Settings.py"]),
]
with st.container(key="profmenu"):
    for label, icon, candidates in rows:
        path = theme.first_existing(candidates)
        if path:
            st.page_link(path, label=label, icon=icon)

with st.container(key="proflogout"):
    if st.button("Log out"):
        for k in ("token", "name", "profile", "chat", "dl_store", "dl_dates"):
            st.session_state.pop(k, None)
        st.switch_page("app.py")