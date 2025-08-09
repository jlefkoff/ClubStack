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

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header("Browse Gear")

# You can access the session state to make a more customized/personalized
# app experience
st.write(f"### Hi, {st.session_state['first_name']}.")

    # Sample gear data
gear_data = {
        "Gear": ["Tent", "Sleeping Bag", "Backpack", "Cooking Set"],
        "Available": [10, 5, 8, 12],
        "Price per Day": [15, 10, 20, 25]
    }

gear_df = pd.DataFrame(gear_data)

    # Display the gear data
st.dataframe(gear_df)

    # Allow users to reserve gear
st.subheader("Reserve Gear")
selected_gear = st.selectbox("Select Gear to Reserve", gear_df["Gear"])
reserve_quantity = st.number_input("Quantity", min_value=1, max_value=gear_df.loc[gear_df["Gear"] == selected_gear, "Available"].values[0])

if st.button("Reserve"):
        available = gear_df.loc[gear_df["Gear"] == selected_gear, "Available"].values[0]
        if reserve_quantity <= available:
            st.success(f"You have reserved {reserve_quantity} {selected_gear}(s).")
        else:
            st.error("Not enough gear available for reservation.")
            if st.session_state.get('first_name') == 'Jacob':
                st.subheader("Manage Gear Items")
                
                # Input fields for adding new gear
                new_gear = st.text_input("New Gear Item")
                new_available = st.number_input("Available Quantity", min_value=0)
                new_price = st.number_input("Price per Day", min_value=0.0)

                if st.button("Add Gear"):
                    if new_gear and new_available > 0 and new_price >= 0:
                        gear_df.loc[len(gear_df)] = [new_gear, new_available, new_price]
                        st.success(f"{new_gear} has been added.")
                    else:
                        st.error("Please provide valid gear details.")

                # Select gear to delete
                gear_to_delete = st.selectbox("Select Gear to Delete", gear_df["Gear"])
                
                if st.button("Delete Gear"):
                    gear_df = gear_df[gear_df["Gear"] != gear_to_delete]
                    st.success(f"{gear_to_delete} has been deleted.")