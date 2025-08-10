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
response = requests.get(f"http://api:4000/events/{event_info['ID']}")
if response.status_code == 200:
    roster = event_info.get("roster", [])
    st.subheader("Event Roster")
    if roster:
        roster_df = pd.DataFrame(roster)
        st.dataframe(roster_df)  # Show all info for each member
    else:
        st.write("No participants yet.")
else:
    st.error("Failed to fetch event data.")



# rsvp for event
if st.button("RSVP to this Event"):
    current_size = len(st.session_state["event_rosters"][event_id])
    max_size = event_info["MaxSize"]
    user_name = st.session_state.get("first_name", "Guest")

    if current_size >= max_size:
        st.error("Sorry, this event is fully booked.")
    elif user_name in st.session_state["Roster"][event_id]:
        st.warning("You have already RSVP’d to this event.")
    else:
        st.session_state["event_rosters"][event_id].append(user_name)
        st.success(f"Thanks {user_name}, you are now RSVP’d!")
        # Update PartySize locally (optional)
        event_info["PartySize"] = current_size + 1



# update event if you are the vp
if st.session_state.get("first_name", "").lower() == "jacob":
    if st.button("Update Event"):
        # You can trigger your update logic here,
        # e.g., navigate to an edit page or open a form
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

            submitted = st.form_submit_button("Save Changes")
            cancel = st.form_submit_button("Cancel")

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
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to update event: {e}")

        if cancel:
            st.session_state.edit_mode = False
            st.experimental_rerun()