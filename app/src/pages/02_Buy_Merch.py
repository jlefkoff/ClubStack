from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import streamlit as st
import pydeck as pdk
import pandas as pd
from urllib.error import URLError
import logging

logger = logging.getLogger(__name__)


SideBarLinks()

# add the logo
#add_logo("assets/logo.png", height=400)
# set up the page
    # Sample merch items
merch_items = [
        {"name": "T-Shirt", "price": 20},
        {"name": "Hoodie", "price": 40},
        {"name": "Cap", "price": 15},
    ]

    # Display merch items
for item in merch_items:
        st.write(f"{item['name']} - ${item['price']}")
        if st.button(f"Buy {item['name']}"):
            st.success(f"You bought a {item['name']}!")

    # Check session state for user 'jacob'
if st.session_state.get('username') == 'jacob':
        st.markdown("### Manage Merch Items")
        new_item_name = st.text_input("Item Name")
        new_item_price = st.number_input("Item Price", min_value=0)

        if st.button("Add Item"):
            if new_item_name and new_item_price:
                merch_items.append({"name": new_item_name, "price": new_item_price})
                st.success(f"Added {new_item_name} - ${new_item_price}!")

        item_to_remove = st.selectbox("Select item to remove", [item['name'] for item in merch_items])
        if st.button("Remove Item"):
            merch_items = [item for item in merch_items if item['name'] != item_to_remove]
            st.success(f"Removed {item_to_remove}!")