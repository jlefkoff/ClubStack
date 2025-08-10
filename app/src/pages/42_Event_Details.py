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
event_info = data_frame[data_frame["ID"] == event_id]

# displaying event details
event_info = event_info.iloc[0].to_dict()

st.header(f"Event Details — {event_info['Name']}")

for key, value in event_info.items():
    st.write(f"**{key}:** {value}")


# rsvp for event
if st.button("RSVP to this Event"):
    current_size = len(st.session_state["event_rosters"][event_id])
    max_size = event_info["MaxSize"]
    user_name = st.session_state.get("first_name", "Guest")

    if current_size >= max_size:
        st.error("Sorry, this event is fully booked.")
    elif user_name in st.session_state["event_rosters"][event_id]:
        st.warning("You have already RSVP’d to this event.")
    else:
        st.session_state["event_rosters"][event_id].append(user_name)
        st.success(f"Thanks {user_name}, you are now RSVP’d!")
        # Update PartySize locally (optional)
        event_info["PartySize"] = current_size + 1