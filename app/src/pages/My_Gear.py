import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Set the header of the page
st.header("Your Gear")

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")


# Display user's gear reservations
st.subheader("Your Gear Reservations")
user_reservations = requests.get(
    f"http://api:4000/gear/reservations/{st.session_state.get('member_id')}"
).json()  # Assuming this endpoint returns user's reservations
st.dataframe(pd.DataFrame(user_reservations))

if st.session_state.get("first_name") == "Jacob":
    st.subheader("Manage Gear Items")

    # Input fields for adding new gear
    new_gear = st.text_input("New Gear Item")
    new_available = st.number_input("Available Quantity", min_value=0)
    new_price = st.number_input("Price per Day", min_value=0.0)

    if st.button("Add Gear"):
        if new_gear and new_available > 0 and new_price >= 0:
            response = requests.post(
                "http://api:4000/add_gear",
                json={"gear": new_gear, "available": new_available, "price": new_price},
            )
            if response.status_code == 200:
                st.success(f"{new_gear} has been added.")
            else:
                st.error("Failed to add gear.")

    # Select gear to delete
    gear_to_delete = st.selectbox("Select Gear to Delete", gear_df["Gear"])

    if st.button("Delete Gear"):
        response = requests.delete(f"http://api:4000/delete_gear/{gear_to_delete}")
        if response.status_code == 200:
            st.success(f"{gear_to_delete} has been deleted.")
        else:
            st.error("Failed to delete gear.")
