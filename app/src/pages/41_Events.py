from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import world_bank_data as wb
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

# display all relevant sidebar links
SideBarLinks()


st.header("Current Events")

#name of user
st.write(f"### Hi, {st.session_state['first_name']}.")

# all actions associated with events
page = st.sidebar.radio("Choose action", [
    "List All Events", 
    "Event Details", 
    "Event Roster", 
    "Participation Stats", 
    "RSVP to Event"
])

# list all events from the api 
if page == "List All Events":
    events = events_bp.list_events()
    if events:
        st.table(pd.DataFrame(events))
    else:
        st.info("No events found.")

# retrieve event details from a specific event ID
elif page == "Event Details":
    event_id = st.number_input("Enter Event ID", step=1, min_value=1)
    if st.button("Get Details"):
        event = events_bp.get_event(event_id)
        if event:
            st.json(event)
        else:
            st.error("Event not found.")

# display roster for a specific event ID
elif page == "Event Roster":
    event_id = st.number_input("Enter Event ID", step=1, min_value=1, key="roster_id")
    if st.button("View Roster"):
        roster = events_bp.get_roster(event_id)
        if roster:
            st.table(pd.DataFrame(roster))
        else:
            st.warning("No participants yet.")

# show graph of participation of events
elif page == "Participation Stats":
    report = events_bp.get_report()
    df = pd.DataFrame(report)
    if not df.empty:
        st.table(df)
        fig = px.bar(df, x="name", y="participants", title="Participation Stats")
        st.plotly_chart(fig)
    else:
        st.info("No participation data yet.")

# rsvp to an event 
elif page == "RSVP to Event":
    event_id = st.number_input("Enter Event ID", step=1, min_value=1, key="rsvp_id")
    name = st.text_input("Your Name")
    if st.button("RSVP"):
        events_bp.rsvp_event(event_id, name)
        st.success("You have successfully RSVP’d!")
