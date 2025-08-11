import os
import streamlit as st
from datetime import date
import requests

st.set_page_config(layout="wide")
from modules.nav import SideBarLinks
SideBarLinks()

st.title("Create New Member")

API_BASE = os.getenv("API_BASE") or "http://localhost:4001"


st.subheader("Enter New Member Information")

# Required
first_name = st.text_input("First Name *")
last_name = st.text_input("Last Name *")
emer_contact_name = st.text_input("Emergency Contact Name *")
emer_contact_phone = st.text_input("Emergency Contact Phone *")

# Optional (non-car)
preferred_name = st.text_input("Preferred Name (optional)")
graduation_year = st.number_input("Graduation Year (optional)", min_value=1900, max_value=2100, step=1, value=2025)
is_grad_student = st.checkbox("Graduate student?")
activation_date = date.today()  # Always today's date

# Car section — appears immediately when checked
has_car = st.checkbox("Has a car?")
car_plate = car_state = None
car_pass_count = None
if has_car:
    st.markdown("**Car Details**")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        car_plate = st.text_input("Car Plate *")
    with c2:
        car_state = st.text_input("Car State *", max_chars=20)
    with c3:
        car_pass_count = st.number_input("Passenger Count *", min_value=0, step=1)

if st.button("Add Member", use_container_width=True):
    # Validate required
    if not first_name.strip() or not last_name.strip() or not emer_contact_name.strip() or not emer_contact_phone.strip():
        st.error("Please fill in all required (*) fields.")
        st.stop()

    # Validate car if checked
    if has_car and (not car_plate or not car_state or car_pass_count is None):
        st.error("Please complete all car fields or uncheck 'Has a car?'.")
        st.stop()

    # Build payload
    payload = {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "preferred_name": preferred_name.strip() or None,
        "graduation_year": int(graduation_year) if graduation_year else None,
        "is_grad_student": bool(is_grad_student),
        "activation_date": activation_date.strftime("%Y-%m-%d"),
        "car_plate": car_plate.strip() if has_car and car_plate else None,
        "car_state": car_state.strip() if has_car and car_state else None,
        "car_pass_count": int(car_pass_count) if has_car and car_pass_count is not None else None,
        "emer_contact_name": emer_contact_name.strip(),
        "emer_contact_phone": emer_contact_phone.strip(),
    }

    try:
        resp = requests.post(
            f"{API_BASE}/members/",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=20
        )
        resp.raise_for_status()
        st.success(f"New member {first_name} {last_name} added successfully!")
        st.json(resp.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to add new member: {e}")
