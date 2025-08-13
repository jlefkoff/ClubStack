from modules.nav import SideBarLinks
import streamlit as st
import logging

logger = logging.getLogger(__name__)


st.set_page_config(layout="wide")

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}.")
st.write("### What would you like to do today?")
st.write("")


if st.button("Manage Reimbursements", type="primary", use_container_width=True):
    st.switch_page("pages/Manage_Reimbursements.py")
