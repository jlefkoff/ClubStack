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


# Fake full event dataset (normally you'd fetch this from your API)
event_data = {
    1: {"name": "Hiking Trip", "date": "2025-08-20", "location": "Blue Ridge Park"},
    2: {"name": "Cooking Workshop", "date": "2025-08-25", "location": "Community Center"},
    3: {"name": "Charity Run", "date": "2025-09-01", "location": "City Stadium"},
    4: {"name": "Photography Walk", "date": "2025-09-10", "location": "Old Town"},
}

# Sample roster
sample_rosters = {
    1: [{"name": "Alice", "count": 1}, {"name": "Bob", "count": 2}],
    2: [{"name": "Charlie", "count": 1}, {"name": "Diana", "count": 3}],
    3: [{"name": "Eve", "count": 4}],
    4: [{"name": "Frank", "count": 2}, {"name": "Grace", "count": 1}],
}

# Ensure we have an event selected
if "selected_event_id" not in st.session_state:
    st.error("No event selected. Go back to the events list.")
    st.stop()

event_id = st.session_state["selected_event_id"]
event_info = event_data[event_id]

# Display event details
st.header(f"Event Details — {event_info['name']}")
st.write(f"**Event ID:** {event_id}")
st.write(f"**Date:** {event_info['date']}")
st.write(f"**Location:** {event_info['location']}")

# Display roster
st.subheader("Event Roster")
roster_df = pd.DataFrame(sample_rosters[event_id])
st.dataframe(roster_df)

# RSVP for event
if "rsvps" not in st.session_state:
    st.session_state.rsvps = set()

if st.button("RSVP for this Event"):
    if event_id in st.session_state.rsvps:
        st.warning("✅ You’ve already RSVP’d for this event.")
    else:
        st.session_state.rsvps.add(event_id)
        st.success(f"🎉 RSVP successful for {event_info['name']}!")