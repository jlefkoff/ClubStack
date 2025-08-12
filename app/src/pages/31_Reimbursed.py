import os
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

reimbursment_member_id = st.number_input("Member ID", min_value=1, step=1)
reimbursement_amount = st.number_input("Amount (USD)", min_value=0.01, step=0.01, format="%.2f")
reimbursement_reason = st.text_area("Reason for Reimbursement")
reimbursement_date = st.date_input("Date of Expense", value=date.today())
category = st.selectbox("Category", ["supplies", "travel", "event", "food", "other"], index=0)

# --- Submit ---
if st.button("Submit Reimbursement", use_container_width=True):
    if reimbursement_amount <= 0 or not reimbursement_reason.strip():
        st.error("Please provide a valid amount and reason for reimbursement.")
        st.stop()

    reimbursement_request = {
        "member_id": int(reimbursment_member_id),
        "amount_cents": int(round(reimbursement_amount * 100)),
        "currency": "USD",
        "category": category,
        "description": reimbursement_reason.strip(),
        "purchase_date": reimbursement_date.strftime("%Y-%m-%d"),
    }

    try:
        # Make POST request to API
        response = requests.post(
            f"{API_BASE}/reimbursements/",
            headers={"Content-Type": "application/json"},
            json=reimbursement_request
        )
        response.raise_for_status()  # Raise error for HTTP 4xx/5xx

        st.success("Reimbursement request submitted successfully!")
        st.json(response.json())  # Show server response

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to submit reimbursement: {e}")
