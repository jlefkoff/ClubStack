import requests
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import logging

from datetime import datetime
from datetime import timedelta

logger = logging.getLogger(__name__)

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Set the header of the page
st.header("Browse Gear")

# Access the session state for a personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")

# Fetch gear data from the API
data = requests.get("http://api:4000/gear").json()
gear_df = pd.DataFrame(data)

# Display the gear data
st.dataframe(gear_df)

# Allow users to reserve gear
st.subheader("Reserve Gear")
selected_gear = st.selectbox("Select Gear to Reserve", gear_df["Name"])
available_quantity = (
    gear_df.loc[gear_df["Name"] == selected_gear, "Quantity"].values[0]
    if not gear_df.loc[gear_df["Name"] == selected_gear, "Status"].isnull().any()
    and gear_df.loc[gear_df["Name"] == selected_gear, "Status"].values[0] == "AVAILABLE"
    else 0
)
if available_quantity < 1:
    st.warning(
        f"No '{selected_gear}' available for reservation. (Quantity: {available_quantity})"
    )

available = (
    gear_df.loc[gear_df["Name"] == selected_gear, "Quantity"].values[0]
    if not gear_df.loc[gear_df["Name"] == selected_gear, "Status"].isnull().any()
    and gear_df.loc[gear_df["Name"] == selected_gear, "Status"].values[0] == "AVAILABLE"
    else 0
)

check_out_date = st.date_input("Check Out Date")
max_return_date = check_out_date + timedelta(weeks=1)
return_date = st.date_input("Return Date", max_value=max_return_date)

if st.button("Reserve Gear"):
    # Make a reservation via API
    reservation_data = {
        "user_id": st.session_state.get("member_id"),
        "item_id": int(gear_df.loc[gear_df["Name"] == selected_gear, "ID"].values[0]),
        "start_date": check_out_date.strftime("%Y-%m-%d"),
        "end_date": return_date.strftime("%Y-%m-%d"),
    }
    response = requests.post("http://api:4000/gear/reservation", json=reservation_data)
    if response.status_code == 200:
        st.success(f"You have reserved {selected_gear}(s).")
    else:
        st.error("Failed to reserve gear.")
        logger.error(f"Response: {response.text}")

if st.session_state.get("first_name") == "Jacob":
    st.subheader("Manage Gear Items")

    # Input fields for adding new gear
    new_gear = st.text_input("New Gear Item")
    new_available = st.number_input("Available Quantity", min_value=0)
    new_price = st.number_input("Price per Day", min_value=0.0)

    if st.button("Add Gear"):
        if new_gear and new_available > 0 and new_price >= 0:
            new_gear_data = {
                "Name": new_gear,
                "Quantity": int(new_available),
                "Price": str(new_price),  # Ensure price is a string
                "Status": "AVAILABLE",  # Default status
                "Location": "Gear Room A",  # Default location
                "Size": "N/A",  # Default size
                "Picture": "",  # Placeholder for picture
                "PurchaseOrder": 0,  # Default purchase order
                "Availability": "Available for checkout",  # Default availability
            }
            response = requests.post("http://api:4000/", json=new_gear_data)
            if response.status_code == 201:
                st.success(f"{new_gear} has been added.")
            else:
                st.error("Failed to add gear.")
        else:
            st.error("Please provide valid gear details.")

    # Select gear to delete
    gear_to_delete = st.selectbox("Select Gear to Delete", gear_df["Name"])

    if st.button("Delete Gear"):
        gear_id = gear_df.loc[gear_df["Name"] == gear_to_delete, "ID"].values[0]
        response = requests.delete(f"http://api:4000/{gear_id}")
        if response.status_code == 204:
            gear_df = gear_df[gear_df["Name"] != gear_to_delete]
            st.success(f"{gear_to_delete} has been deleted.")
        else:
            st.error("Failed to delete gear.")
