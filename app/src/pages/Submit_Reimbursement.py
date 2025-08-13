import os
from urllib import response
import streamlit as st
from datetime import date
import requests

st.set_page_config(layout="wide")
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Submit Reimbursement Request")

API_BASE = os.getenv("API_BASE") or "http://localhost:4001"

# --- Inputs ---
st.subheader("Enter Reimbursement Details")

# Form to input reimbursement details
with st.form("reimbursement_form"):
    st.subheader("Enter Reimbursement Details")

    # Input fields for reimbursement request
    reimbursement_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    reimbursement_reason = st.text_area("Reason for Reimbursement")
    reimbursement_date = st.date_input("Date of Expense", value=datetime.now())

    # Submit button to add the reimbursement request
    submit_button = st.form_submit_button("Submit Reimbursement")

    if submit_button:
        if not reimbursement_reason or reimbursement_amount <= 0:
            st.error("Please provide a valid amount and reason for reimbursement.")
        else:
            # Creating a dictionary to store the reimbursement request
            reimbursement_request = {
                "member_id": st.session_state.get("member_id"),
                "first_name": st.session_state.get("first_name"),
                "last_name": st.session_state.get("last_name"),
                "amount": reimbursement_amount,
                "reason": reimbursement_reason,
                "date_of_expense": reimbursement_date.strftime("%Y-%m-%d"),
            }

            # Add the reimbursement request to session state (or database)
            if "reimbursement_requests" not in st.session_state:
                st.session_state["reimbursement_requests"] = (
                    []
                )  # Initialize list if not present

            st.session_state["reimbursement_requests"].append(
                reimbursement_request
            )  # Add new reimbursement request to the list

            st.success("Reimbursement request submitted successfully!")
            st.json(response.json())  # Show server response

            # Optionally, display all reimbursement requests (for debugging or confirmation)
            st.write("### Your Submitted Reimbursement Requests:")
            st.write(st.session_state["reimbursement_requests"])

    else:
        st.error("You must be logged in as a member to submit a reimbursement request.")
