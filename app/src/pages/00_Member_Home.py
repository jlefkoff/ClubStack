from modules.nav import SideBarLinks
import streamlit as st
import logging

logger = logging.getLogger(__name__)


st.set_page_config(layout="wide")

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome to Your Member Portal, {st.session_state['first_name']}.")
st.write("")
st.write("")
st.write("### What would you like to do today?")

if st.button("Browse Gear", type="primary", use_container_width=True):
    st.switch_page("pages/01_Browse_Gear.py")


if st.button("Member Profile", type="primary", use_container_width=True):
    st.switch_page("pages/09_Member_Profile.py")


if st.button("Submit a reimbursement", type="primary", use_container_width=True):
    st.switch_page("pages/31_Reimbursed.py")

if st.button("Buy Merch", type="primary", use_container_width=True):
    st.switch_page("pages/02_Buy_Merch.py")
