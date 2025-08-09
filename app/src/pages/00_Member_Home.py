from modules.nav import SideBarLinks
import streamlit as st
import logging

logger = logging.getLogger(__name__)


st.set_page_config(layout="wide")

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Member, {st.session_state['first_name']}.")
st.write("")
st.write("")
st.write("### What would you like to do today?")

if st.button(
    "View Member Profile",
    type="primary",
        use_container_width=True):
    st.switch_page("pages/03_Member_Profile.py")

if st.button("View World Map Demo", type="primary", use_container_width=True):
    st.switch_page("pages/02_Map_Demo.py")
