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


def buy_item(item_id: int, cash: bool = True):
    try:
        response = requests.post(
            f"{BASE_URL}/merch/merch-sales", json={"cash": cash, "ID": item_id}
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            st.success(f"You bought item ID {item_id}!")
        else:
            st.error("Failed to process the sale.")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to process the sale: {e}")


# Function to delete a merch item
def delete_merch_item(item_id):
    response = requests.delete(f"{BASE_URL}/merch/{item_id}")
    if response.status_code == 200:
        st.success(f"Deleted item with ID: {item_id}")
    else:
        st.error("Failed to delete the item.")

# Display merch items in a grid
cols = st.columns(3)  # Adjust the number of columns as needed
for index, item in enumerate(merch_items):
    with cols[index % 3]:  # Distribute items across the columns
        st.write(f"**{item['Name']}** - **${item['Price']}**")
        
        # Create a container for buttons
        button_col = st.columns(3)
        with button_col[0]:
            if st.button(f"Buy {item['Name']}", key=item['ID'], help="Purchase this item"):
             buy_item(item['Name'])  # Call the buy_item function as needed    
        if st.session_state.get('first_name') == 'Jacob':  
             with button_col[1]:
                 if st.button("Delete", key=f"delete_{item['ID']}"):
                   delete_merch_item(item['ID'])
                # Function to add a merch item

def add_merch_item(item_name, item_price):
                    response = requests.post(f"{BASE_URL}/merch/", json={"name": item_name, "price": item_price})
                    if response.status_code == 201:
                        st.success(f"Added {item_name} for ${item_price}!")
                    else:
                        st.error("Failed to add the item.")

 
if st.session_state.get('first_name') == 'Jacob' or st.session_state.get('first_name') == 'Jonah':                  # Input fields for new merch item
    st.subheader("Add New Merch Item")
    new_item_name = st.text_input("Item Name")
    new_item_price = st.number_input("Item Price", min_value=0.0, format="%.2f")
if st.session_state.get('first_name') == 'Jacob' or st.session_state.get('first_name') == 'Jonah':
    if st.button("Add Item"):
                    if new_item_name and new_item_price >= 0:
                        add_merch_item(new_item_name, new_item_price)
                    else:
                        st.error("Please provide a valid item name and price.")
                        # Refresh the merch items after adding a new item
                        merch_items = fetch_merch_items()
