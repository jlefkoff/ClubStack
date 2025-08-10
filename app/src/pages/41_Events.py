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


# # Sample event data
# event_data = {
#     "Event ID": [1, 2, 3, 4],
#     "Event Name": ["Hiking Trip", "Cooking Workshop", "Charity Run", "Photography Walk"],
#     "Date": ["2025-08-20", "2025-08-25", "2025-09-01", "2025-09-10"],
#     "Location": ["Blue Ridge Park", "Community Center", "City Stadium", "Old Town"],
#     "Available Spots": [15, 10, 50, 20],
#     "Total Spots": [20, 15, 100, 25]
# }
# event_df = pd.DataFrame(data)

# # Display events list
# st.dataframe(event_df)

# # RSVP to an event
# st.subheader("RSVP for an Event")
# selected_event = st.selectbox("Select Event to RSVP", event_df["Event Name"])
# spots_available = event_df.loc[event_df["Event Name"] == selected_event, "Available Spots"].values[0]
# rsvp_count = st.number_input("Number of Participants", min_value=1, max_value=spots_available)

# if st.button("RSVP"):
#     if rsvp_count <= spots_available:
#         st.success(f"You have successfully RSVP'd {rsvp_count} spot(s) for '{selected_event}'.")
#     else:
#         st.error("Not enough spots available for this event.")

# # View event details
# st.subheader("View Event Details")
# detail_event = st.selectbox("Select Event to View Details", event_df["Event Name"])
# event_details = event_df[event_df["Event Name"] == detail_event]
# st.table(event_details)

# # View event roster (sample non-live data)
# st.subheader("View Event Roster")
# sample_roster = {
#     "Participant Name": ["Alice", "Bob", "Charlie", "Diana"],
#     "RSVP Count": [1, 2, 1, 3]
# }
# roster_df = pd.DataFrame(sample_roster)
# st.dataframe(roster_df)

# # Event participation report (sample statistics)
# st.subheader("Event Participation Report")
# event_report = {
#     "Event Name": event_df["Event Name"],
#     "Spots Filled (%)": round((event_df["Total Spots"] - event_df["Available Spots"]) / event_df["Total Spots"] * 100, 2)
# }
# report_df = pd.DataFrame(event_report)
# st.bar_chart(report_df.set_index("Event Name"))
# 


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




if st.session_state.get("first_name", "").lower() == "jacob":
    if st.button("Create Event"):
        # You can trigger your update logic here,
        # e.g., navigate to an edit page or open a form
        with st.form("create_event_form"):
            # Create inputs for each editable field — customize as needed
            author = st.text_input("ID", "")
            name = st.text_input("Name", "")
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