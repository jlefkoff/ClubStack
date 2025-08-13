import os
import streamlit as st
from datetime import date
import requests

st.set_page_config(layout="wide")
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Create New Member")

API_BASE = os.getenv("API_BASE") or "http://web-api:4000"



# --- Inputs ---
st.subheader("Enter New Member Information")

# Required fields
first_name = st.text_input("First Name *")
last_name = st.text_input("Last Name *")
emer_contact_name = st.text_input("Emergency Contact Name *")
emer_contact_phone = st.text_input("Emergency Contact Phone *")

# Optional fields
preferred_name = st.text_input("Preferred Name (optional)")
graduation_year = st.number_input(
    "Graduation Year", min_value=2020, max_value=2035, step=1, value=2025
)
is_grad_student = st.checkbox("Graduate Student")
activation_date = st.date_input("Activation Date", value=date.today())

# Car information
st.subheader("Vehicle Information (Optional)")
has_car = st.checkbox("Member has a vehicle")

car_plate = None
car_state = None  
car_pass_count = None

if has_car:
    col1, col2, col3 = st.columns(3)
    with col1:
        car_plate = st.text_input("License Plate *")
    with col2:
        car_state = st.text_input("State *")
    with col3:
        car_pass_count = st.number_input("Parking Pass Count *", min_value=0, step=1)

# Submit button
if st.button("Create Member", use_container_width=True):
    # Validate required fields
    if not all([first_name.strip(), last_name.strip(), emer_contact_name.strip(), emer_contact_phone.strip()]):
        st.error("Please fill in all required (*) fields.")
        st.stop()

    # Validate car info if provided
    if has_car and not all([car_plate and car_plate.strip(), car_state and car_state.strip(), car_pass_count is not None]):
        st.error("Please complete all vehicle fields or uncheck 'Member has a vehicle'.")
        st.stop()

    # Build payload to match your API
    payload = {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "emer_contact_name": emer_contact_name.strip(),
        "emer_contact_phone": emer_contact_phone.strip(),
        "preferred_name": preferred_name.strip() if preferred_name.strip() else None,
        "graduation_year": graduation_year,
        "is_grad_student": is_grad_student,
        "activation_date": activation_date.strftime("%Y-%m-%d"),
        "car_plate": car_plate.strip() if has_car and car_plate else None,
        "car_state": car_state.strip() if has_car and car_state else None,
        "car_pass_count": car_pass_count if has_car and car_pass_count is not None else None
    }

    try:
        with st.spinner("Creating member..."):
            response = requests.post(
                f"{API_BASE}/members/",
                json=payload,
                timeout=10
            )
            response.raise_for_status()

        result = response.json()
        st.success(f"✅ Member {first_name} {last_name} created successfully!")
        st.info(f"Member ID: {result.get('member_id')}")
        
        # Option to create another member
        if st.button("Create Another Member"):
            st.rerun()

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to create member: {e}")
        
        # Show detailed error if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json().get('error', 'Unknown error')
                st.error(f"Server error: {error_detail}")
            except:
                st.error(f"HTTP Status: {e.response.status_code}")

    except Exception as e:
        st.error(f"Unexpected error: {e}")