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


#rsvp 
with st.form("rsvp_form"):
    st.write("RSVP to this event")
    event_id = st.number_input("Event ID", value=event_info['ID'], step=1)
    member_id = st.number_input("Member ID", min_value=0, step=1)
    can_bring_car = st.text_input("Can you bring a car? (yes/no)", "")
    avail_start = st.text_input("Available Start (YYYY-MM-DD HH:MM)", "")
    avail_end = st.text_input("Available End (YYYY-MM-DD HH:MM)", "")

    submit_rsvp = st.form_submit_button("RSVP Now")

if submit_rsvp:
    payload = {
        "event_id": event_id,
        "member_id": member_id,
        "can_bring_car": can_bring_car,
        "avail_start": avail_start,
        "avail_end": avail_end
    }
    
    try:
        response = requests.post(
            f"http://api:4000/events/{event_info['ID']}/rsvp",
            json=payload
        )
        response.raise_for_status()
        st.success("You have successfully RSVP'd!")
        st.json(response.json())
        st.rerun()
    except Exception as e:
        st.error(f"Failed to RSVP: {e}")










# updating an event
if st.session_state.get("first_name", "").lower() == "chance":
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