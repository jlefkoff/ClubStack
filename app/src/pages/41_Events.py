from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import world_bank_data as wb
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging


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
# event_df = pd.DataFrame(event_data)

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


# Sample event data
event_data = {
    "Event ID": [1, 2, 3, 4],
    "Event Name": ["Hiking Trip", "Cooking Workshop", "Charity Run", "Photography Walk"],
    "Date": ["2025-08-20", "2025-08-25", "2025-09-01", "2025-09-10"],
    "Location": ["Blue Ridge Park", "Community Center", "City Stadium", "Old Town"],
}
event_df = pd.DataFrame(event_data)

st.header("Browse Events")
st.dataframe(event_df)

# Select event to view details
selected_event = st.selectbox("Select an event to view details:", event_df["Event Name"])

# Store selected event in session state so next page can use it
if st.button("Go to Event Details"):
    event_id = event_df.loc[event_df["Event Name"] == selected_event, "Event ID"].values[0]
    st.session_state["selected_event_id"] = event_id
    st.switch_page("pages/42_Event_Details.py")  # requires Streamlit >=1.25
