from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import streamlit as st
import requests
import logging

logger = logging.getLogger(__name__)

SideBarLinks()
st.header("Buy Merch")
# Define the base URL for the API
BASE_URL = "http://api:4000"


# Function to fetch merch items from the API
def fetch_merch_items():
    try:
        response = requests.get(f"{BASE_URL}/merch")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the API. Please ensure the server is running.")
        logger.error("ConnectionError: Unable to connect to the API.")
        return []
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        logger.error(f"HTTPError: {http_err}")
        return []
    except Exception as err:
        st.error(f"An unexpected error occurred: {err}")
        logger.error(f"UnexpectedError: {err}")
        return []


# Fetch and display merch items
merch_items = fetch_merch_items()


def buy_item(item_name):
    response = requests.post(f"{BASE_URL}/sale", json={"item_name": item_name})
    if response.status_code == 200:
        st.success(f"You bought a {item_name}!")
    else:
        st.error("Failed to process the sale.")


# Display merch items in a grid
cols = st.columns(3)  # Adjust the number of columns as needed
for index, item in enumerate(merch_items):
    with cols[index % 3]:  # Distribute items across the columns
        st.write(f"**{item['Name']}** - **${item['Price']}")
        if st.button(f"Buy {item['Name']}", key=item["ID"]):
            buy_item(item["Name"])  # Call the buy_item function as needed

# Function to buy an item and update the database
