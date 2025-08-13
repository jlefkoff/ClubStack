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
data_frame = pd.DataFrame(data)

# Sidebar navigation
SideBarLinks()

# Page header
st.header("Browse Events")

# Personalized greeting
st.write(f"### Hi, {st.session_state['first_name']}.")


# Ensure we have an event selected
if "selected_event_id" not in st.session_state:
    st.error("No event selected. Go back to the events list.")
    st.stop()

event_id = st.session_state["selected_event_id"]
event_info = data_frame[data_frame["ID"] == event_id]

# displaying event details
event_info = event_info.iloc[0].to_dict()

st.header(f"Event Details — {event_info['Name']}")

for key, value in event_info.items():
    st.write(f"**{key}:** {value}")



# display event roster
response = requests.get(f"http://api:4000/events/{event_info['ID']}/roster")
response.raise_for_status()
data = response.json()
st.subheader(f"Roster for Event {data['event_id']}")
if data["roster"]:
    for member in data["roster"]:
        st.write(f"- {member}")



# updating an event
# updating an event
if st.session_state.get("first_name", "").lower() in ("chance", "jacob"):
    # Initialize edit mode state
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    
    if not st.session_state.edit_mode:
        if st.button("Update Event"):
            st.session_state.edit_mode = True
            st.rerun()
    else:
        # Edit form is now persistent
        with st.form("update_event_form"):
            # Create inputs for each editable field — customize as needed
            name = st.text_input("Name", value=event_info.get("Name", ""))
            description = st.text_area("Description", value=event_info.get("Description", ""))
            event_loc = st.text_input("Event Location", value=event_info.get("EventLoc", ""))
            event_type = st.text_input("Event Type", value=event_info.get("EventType", ""))
            lead_org = st.text_input("Lead Organization", value=event_info.get("LeadOrg", ""))
            max_size = st.number_input("Max Size", value=event_info.get("MaxSize", 1), min_value=1)
            party_size = st.number_input("Party Size", value=event_info.get("PartySize", 0), min_value=0, max_value=max_size)
            meet_loc = st.text_input("Meeting Location", value=event_info.get("MeetLoc", ""))
            rec_items = st.text_area("Recommended Items", value=event_info.get("RecItems", ""))

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Save Changes", type="primary")
            with col2:
                cancel = st.form_submit_button("Cancel")

        # Handle form submission - OUTSIDE the form but inside the edit_mode condition
        if submitted:
            # Prepare payload with updated fields
            payload = {
                "Name": name,
                "Description": description,
                "EventLoc": event_loc,
                "EventType": event_type,
                "LeadOrg": lead_org,
                "MaxSize": max_size,
                "PartySize": party_size,
                "MeetLoc": meet_loc,
                "RecItems": rec_items,
            }
            try:
                response = requests.put(f"http://api:4000/events/{event_id}", json=payload)
                response.raise_for_status()
                st.success("Event updated successfully!")
                st.session_state.edit_mode = False
                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to update event: {e}")

        if cancel:
            st.session_state.edit_mode = False
            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()