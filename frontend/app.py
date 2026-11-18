import html

import requests
import streamlit as st

import api_client as api
import home_ui
import theme

st.set_page_config(
    page_title="HerRhythm", page_icon="\U0001F338", layout="centered",
    initial_sidebar_state="collapsed",
)
theme.apply_theme(sidebar=False)

PHASE_TIPS = {
    "menstrual": "Rest, stay warm and hydrated, and eat iron-rich foods. Gentle walking helps.",
    "follicular": "Energy is rising. A good time for strength training and new projects.",
    "ovulation": "Many people feel most energetic and social around now.",
    "luteal": "PMS may show up. Magnesium-rich foods and light exercise can help.",
    "late": "Your period is later than predicted. Log it when it starts.",
}


def login_view():
    import login_art; st.image(login_art.banner_svg(), width="stretch"); st.markdown(login_art.css(), unsafe_allow_html=True)
    st.markdown(
        "<div class='hello-big'>Hello,</div><div class='tagline'>Your cycle, your rhythm.</div>",
        unsafe_allow_html=True,
    )
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_clicked = st.form_submit_button("Log in")
        if login_clicked:
            try:
                st.session_state["token"] = api.login(email, password)
                st.rerun()
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend. Is uvicorn running?")
            except Exception as e:
                st.error(str(e))

    with register_tab:
        with st.form("register_form"):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=10, max_value=100, value=20)
            email_r = st.text_input("Email", key="reg_email")
            password_r = st.text_input("Password (min 6 characters)", type="password", key="reg_pw")
            register_clicked = st.form_submit_button("Create account")
        if register_clicked:
            try:
                api.register(name, int(age), email_r, password_r)
                st.success("Account created. Now log in from the Login tab.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend. Is uvicorn running?")
            except Exception as e:
                st.error(str(e))


def home_view():
    theme.bottom_nav(); import look; look.apply()
    st.markdown(home_ui.CSS, unsafe_allow_html=True)

    name = st.session_state.get("name")
    if name is None:
        try:
            name = api._get("/account/export")["profile"]["name"] or ""
        except Exception:
            name = ""
        st.session_state["name"] = name

    try:
        pred = api.get_prediction()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Is uvicorn running?")
        st.stop()
    except Exception as e:
        st.error(str(e))
        st.stop()
    has_data = pred.get("status") == "ok"

    with st.container(key="homehead"):
        c1, c2 = st.columns([6, 1])
        c1.markdown(
            "<div class='hh'><div class='av'>" + html.escape((name[:1] or "H").upper()) + "</div><div>"
            "<div class='hi'>Hello, " + html.escape(name) + "! \U0001F44B</div>"
            "<div class='sub'>You're doing great!</div></div></div>",
            unsafe_allow_html=True,
        )
        bell = theme.first_existing(["pages/11_Reminders.py"])
        if bell:
            with c2:
                with st.container(key="homebell"):
                    st.page_link(bell, label="Reminders", icon="\U0001F514")

    with st.container(key="card_next"):
        if has_data:
            left = int(pred["days_until_next_period"])
            sub = "Next Period in" if left > 0 else "Next Period"
            big = (str(left) + " days") if left > 0 else ("Today" if left == 0 else str(-left) + " days late")
            from datetime import date as _d
            exp = _d.fromisoformat(pred["next_period_start"]).strftime("%b %d, %Y")
            txt = "<div class='sub'>" + sub + "</div><div class='big'>" + big + "</div><div class='exp'>Expected: " + exp + "</div>"
        else:
            txt = "<div class='sub'>Next Period</div><div class='big'>Add your last period</div><div class='exp'>Tap + to log it</div>"
        st.markdown("<div class='np'><div class='ic'>\U0001F4C5</div><div>" + txt + "</div></div>", unsafe_allow_html=True)

    with st.container(key="ring"):
        import cycle_marks
        cycle_marks.show_wheel(pred if has_data else None)

    if has_data:
        pct = min(100, round(100 * int(pred["day_in_cycle"]) / max(int(pred["avg_cycle_length"]), 1)))
        st.markdown(
            "<div class='cp'><div class='row'><span>Cycle Progress</span><span>" + str(pct) + "%</span></div>"
            "<div class='bar'><div style='width:" + str(pct) + "%'></div></div></div>",
            unsafe_allow_html=True,
        )
        if pred["confidence"] == "low":
            st.caption("Confidence is low. Log at least 3 cycles for better predictions.")

    tiles = [("care", "\U0001F497", "Self-Care", "pages/14_Self_Care.py")]
    with st.container(key="hometiles"):
        cols = st.columns(1)
        for col, (k, em, label, path) in zip(cols, tiles):
            if theme.first_existing([path]):
                with col:
                    with st.container(key="ht_" + k):
                        st.markdown("<div class='em'>" + em + "</div>", unsafe_allow_html=True)
                        st.page_link(path, label=label)

    with st.container(key="card_tip"):
        phase = pred["current_phase"] if has_data else None
        tip = PHASE_TIPS.get(phase, "Log your first period to get daily guidance.")
        st.markdown(
            "<div class='tip'><div class='ic'>\U0001F4A1</div><div><div class='t'>Today's Tip</div>"
            "<div class='d'>" + tip + "</div></div></div>",
            unsafe_allow_html=True,
        )

    st.caption("Estimates based on your logs, not medical advice.")


if "token" not in st.session_state:
    login_view()
else:
    home_view()