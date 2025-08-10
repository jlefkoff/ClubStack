from modules.nav import SideBarLinks
import streamlit as st
import logging

logger = logging.getLogger(__name__)


st.set_page_config(layout="wide")

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome USAID Worker, {st.session_state['first_name']}.")
st.write("")
st.write("")
st.write("### What would you like to do today?")

if st.button(
    "Submit a reimbursement",
    type="primary",
        use_container_width=True):
    st.switch_page("pages/31_Reimbursed.py")

if st.button(
    "View the Simple API Demo",
    type="primary",
        use_container_width=True):
    st.switch_page("pages/12_API_Test.py")

if st.button(
    "View Classification Demo",
    type="primary",
        use_container_width=True):
    st.switch_page("pages/13_Classification.py")
