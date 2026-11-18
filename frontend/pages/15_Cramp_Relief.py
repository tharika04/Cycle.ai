import streamlit as st

import api_client as api
import routines

st.set_page_config(page_title="Cramp Relief", page_icon="\U0001F9D8", layout="centered")
api.require_login(); import theme; theme.setup()

routines.render()