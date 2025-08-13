from modules.nav import SideBarLinks
import streamlit as st
import requests
import logging

logger = logging.getLogger(__name__)


st.set_page_config(layout="wide")

SideBarLinks()

st.title("VP Home Page")

if st.button("Add an Event", type="primary", use_container_width=True):
    st.switch_page("pages/41_Events.py")
if st.button("Budget Overview", type="primary", use_container_width=True):
    st.switch_page("pages/Budget_Overview.py")
