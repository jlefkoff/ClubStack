import streamlit as st
from modules.nav import SideBarLinks
from streamlit_extras.app_logo import add_logo

SideBarLinks()

st.write("# About this App")

st.markdown(
    """
    This is a demo app for CS3200, Database Design for the Summer 2 Semester 2025.

    It is desgined to provide an all-in-one club management platform for members, gear, merch, and events.
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
