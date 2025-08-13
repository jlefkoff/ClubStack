import os
import streamlit as st
from datetime import date
import requests

st.set_page_config(layout="wide")
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Submit Reimbursement Request")

API_BASE = "http://api:4000"

# Get member ID from session state
member_id = st.session_state.get("member_id")


# --- Inputs ---
st.subheader("Enter Reimbursement Information")

# Required fields
description = st.text_area("Description/Reason for Reimbursement *", 
                          placeholder="e.g., Business trip expenses, Office supplies")

# Items section
st.subheader("Expense Items")

# Initialize session state for items
if "reimbursement_items" not in st.session_state:
    st.session_state.reimbursement_items = []

# Add item form
with st.form("add_item_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        item_description = st.text_input("Item Description *", 
                                       placeholder="e.g., Hotel stay, Gas receipt")
    
    with col2:
        item_price = st.number_input("Price ($) *", min_value=0.01, format="%.2f", step=0.01)
    
    if st.form_submit_button("Add Item"):
        if not item_description.strip():
            st.error("Please provide an item description.")
        elif item_price <= 0:
            st.error("Please provide a valid price.")
        else:
            new_item = {
                "description": item_description.strip(),
                "price": float(item_price)
            }
            st.session_state.reimbursement_items.append(new_item)
            st.success(f"Added: {item_description} - ${item_price:.2f}")
            st.rerun()

# Display current items
if st.session_state.reimbursement_items:
    st.write("#### Current Items")
    
    total_amount = 0
    for i, item in enumerate(st.session_state.reimbursement_items):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{item['description']}**")
        
        with col2:
            st.write(f"${item['price']:.2f}")
        
        with col3:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.reimbursement_items.pop(i)
                st.rerun()
        
        total_amount += item['price']
    
    st.write(f"**Total Amount: ${total_amount:.2f}**")
    
    # Clear all items button
    if st.button("Clear All Items"):
        st.session_state.reimbursement_items = []
        st.rerun()
else:
    st.info("No items added yet. Please add expense items above.")

# Submit button
if st.button("Submit Reimbursement", use_container_width=True):
    # Validate required fields
    if not description.strip():
        st.error("Please provide a description for the reimbursement.")
        st.stop()
    
    if not st.session_state.reimbursement_items:
        st.error("Please add at least one expense item.")
        st.stop()

    # Build payload to match your API
    payload = {
        "member_id": member_id,
        "description": description.strip(),
        "total": total_amount,
        "items": st.session_state.reimbursement_items
    }

    try:
        with st.spinner("Submitting reimbursement..."):
            response = requests.post(
                f"{API_BASE}/reimbursements/",
                json=payload,
                timeout=10
            )
            response.raise_for_status()

        result = response.json()
        st.success(f"✅ Reimbursement submitted successfully!")
        st.info(f"Reimbursement ID: {result.get('reimbursement_id')}")
        st.info(f"Status: {result.get('status', 'Pending')}")
        
        # Clear items after successful submission
        st.session_state.reimbursement_items = []
        
        # Option to submit another reimbursement
        if st.button("Submit Another Reimbursement"):
            st.rerun()

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to submit reimbursement: {e}")
        
        # Show detailed error if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json().get('error', 'Unknown error')
                st.error(f"Server error: {error_detail}")
            except:
                st.error(f"HTTP Status: {e.response.status_code}")

    except Exception as e:
        st.error(f"Unexpected error: {e}")