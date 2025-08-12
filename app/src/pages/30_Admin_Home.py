from modules.nav import SideBarLinks
import streamlit as st
import requests
import logging

logger = logging.getLogger(__name__)


st.set_page_config(layout="wide")

SideBarLinks()

st.title("System Admin Home Page")


if st.button(
    "Permissions Overview",
    type="primary",
        use_container_width=True):
    st.switch_page("pages/permissions_overview.py")