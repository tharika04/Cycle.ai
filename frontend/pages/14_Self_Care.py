import streamlit as st

import api_client as api
import theme

st.set_page_config(page_title="Self-Care", page_icon="\U0001F338", layout="centered")
api.require_login(); import theme; theme.setup()

st.title("Self-Care")
theme.tile_grid(theme.TILES, key="a")
st.subheader("More")
theme.tile_grid(theme.MORE, key="b")

if st.button("Log out"):
    for k in ("token", "name", "chat"):
        st.session_state.pop(k, None)
    st.switch_page("app.py")