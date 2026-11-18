import requests
import streamlit as st
import api_client as api

st.set_page_config(page_title="HerRhythm", page_icon="\U0001F338", layout="wide")
st.title("HerRhythm")
st.caption("AI-based menstrual and reproductive health tracker")

if "token" in st.session_state:
    st.success("You are logged in. Use the sidebar to open Dashboard, Log Data, or Symptoms.")
    st.info("Informational only, not medical advice.")
    if st.button("Log out"):
        del st.session_state["token"]
        st.rerun()
    st.stop()

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