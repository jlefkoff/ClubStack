from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import world_bank_data as wb
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import requests


# data from api
data = {}
data = requests.get("http://api:4000/events").json()

logger = logging.getLogger(__name__)

# Sidebar navigation
SideBarLinks()

# Page header
st.header("Browse Events")

# Personalized greeting
st.write(f"### Hi, {st.session_state['first_name']}.")


st.header("Browse Events")
st.dataframe(data)
data_frame = pd.DataFrame(data)

# Select event to view details
selected_event = st.selectbox("Select an event to view details:", data_frame["Name"])

# Store selected event in session state so next page can use it
if st.button("Go to Event Details"):
    event_id = data_frame.loc[data_frame["Name"] == selected_event, "ID"].values[0]
    st.session_state["selected_event_id"] = event_id
    st.switch_page("pages/42_Event_Details.py")  

# participation stats
st.subheader("Event Participation Report")

event_report = {
    "Event Name": data_frame["Name"],
    "Spots Filled (%)": ((data_frame["PartySize"] / data_frame["MaxSize"]) * 100).round(2)
}

report_df = pd.DataFrame(event_report)

st.bar_chart(report_df.set_index("Event Name"))




# creating an event
if st.session_state.get("first_name", "").lower() == "chance":
    if "create_event_mode" not in st.session_state:
        st.session_state.create_event_mode = False

    # Toggle form visibility
    if st.button("Create Event"):
        st.session_state.create_event_mode = True

    # Only show form if we're in create mode
    if st.session_state.create_event_mode:
        with st.form("create_event_form"):
            author = st.number_input("Author", min_value=0, value=0)
            name = st.text_input("Name", "")
            description = st.text_area("Description", "")
            event_loc = st.text_input("Event Location", "")
            event_type = st.text_input("Event Type", "")
           #  ID = st.text_input("ID", "")
            lead_org = st.text_input("Lead Organization", "")
            max_size = st.number_input("Max Size", min_value=1)
            party_size = st.number_input("Party Size", 0, max_value = 0)
            meet_loc = st.text_input("Meeting Location", "")
            rec_items = st.text_area("Recommended Items", "")
            randomized = st.checkbox("Randomized", value=False)

            submitted = st.form_submit_button("Save Event")
            cancel = st.form_submit_button("Cancel")

        if submitted:
            payload = {
                "Author": author,
                "Name": name,
                "Description": description,
                "EventLoc": event_loc,
                "EventType": event_type,
               #  "ID": ID,
                "LeadOrg": lead_org,
                "MaxSize": max_size,
                "PartySize": party_size,
                "MeetLoc": meet_loc,
                "RecItems": rec_items,
                "Randomized": randomized
            }
            try:
                response = requests.post("http://api:4000/events", json=payload)
                response.raise_for_status()
                st.success("Event created successfully!")
                st.json(response.json())
                st.session_state.create_event_mode = False
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to add event: {e}")

        if cancel:
            st.session_state.create_event_mode = False
            st.rerun()

# delete an event
if st.session_state.get("first_name", "").lower() == "chance":
    if "delete_event_mode" not in st.session_state:
        st.session_state.delete_event_mode = False

    # Toggle form visibility
    if st.button("Delete Event"):
        st.session_state.delete_event_mode = True

    if st.session_state.delete_event_mode:
        with st.form("delete_event_form"):
            event_id = st.text_input("Event ID to delete", "")
        
            submitted = st.form_submit_button("Delete Event")
            cancel = st.form_submit_button("Cancel")
        if submitted:
            try:
                response = requests.delete(f"http://api:4000/events/{event_id}")
                response.raise_for_status()
                st.success("Event deleted successfully!")
                st.json(response.json())
                st.session_state.delete_event_mode = False
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to delete event: {e}")

        if cancel:
            st.session_state.delete_event_mode = False
            st.rerun()
