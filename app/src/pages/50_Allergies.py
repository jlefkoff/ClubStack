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
data = requests.get("http://api:4000/allergies").json()

logger = logging.getLogger(__name__)
data_frame = pd.DataFrame(data)

# Sidebar navigation
SideBarLinks()

# Page header
st.header("Member Allergies")

# Personalized greeting
st.write(f"### Hi, {st.session_state['first_name']}.")

# generate report
if st.button("Generate Allergy Report"):
    try:
        response = requests.get("http://api:4000/allergies/report")
        response.raise_for_status()
        data = response.json()  # Expecting a list of dicts like your example

        if data:
            df = pd.DataFrame(data)
            st.subheader("Allergy Report")
            st.table(df)
        else:
            st.info("No data found in the allergy report.")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch allergy report: {e}")


# create new allergy
if "show_allergy_form" not in st.session_state:
    st.session_state.show_allergy_form = False

if st.button("Add New Allergy"):
    st.session_state.show_allergy_form = True

if st.session_state.show_allergy_form:
    with st.form("allergy_form"):
        allergy_name = st.text_input("Allergy Name")

        submitted = st.form_submit_button("Create Allergy")
        cancel = st.form_submit_button("Cancel")

    if submitted:
        payload = {
            "Name": allergy_name,
        }
        try:
            response = requests.post("http://api:4000/allergies/", json=payload)
            response.raise_for_status()
            st.success("Allergy created successfully!")
            st.json(response.json())
            st.session_state.show_allergy_form = False
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to create allergy: {e}")

    if cancel:
        st.session_state.show_allergy_form = False


# display existing allergies
st.subheader("Allergies List")

response = requests.get("http://api:4000/allergies/")
response.raise_for_status()
allergies = response.json()

if allergies:
    df = pd.DataFrame(allergies)
    st.table(df)
else:
    st.info("No allergies found.")
