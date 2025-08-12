import os
import requests
from modules.nav import SideBarLinks
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Set the header of the page
st.header("Your Profile")

# API Configuration
API_BASE = os.getenv("API_BASE") or "http://web-api:4000"

# Get member ID input
member_id = st.number_input("Enter Member ID", min_value=1, step=1)

if not member_id:
    st.info("Please enter a member ID to view profile.")
    st.stop()

# Fetch and display member profile
try:
    response = requests.get(f"{API_BASE}/members/{member_id}")
    if response.status_code == 200:
        profile = response.json()["member"]
        
        st.subheader("Profile Information")
        
        st.write(f"**Name:** {profile.get('FirstName')} {profile.get('LastName')}")
        
        if profile.get('PreferredName'):
            st.write(f"**Preferred Name:** {profile.get('PreferredName')}")
        
        if profile.get('GraduationYear'):
            st.write(f"**Graduation Year:** {profile.get('GraduationYear')}")
        
        student_type = "Graduate Student" if profile.get('IsGradStudent') else "Undergraduate Student"
        st.write(f"**Student Type:** {student_type}")
        
        if profile.get('ActivationDate'):
            st.write(f"**Member Since:** {profile.get('ActivationDate')}")
        
        if profile.get('CarPlate'):
            st.write(f"**Car:** {profile.get('CarPlate')} ({profile.get('CarState')})")
        
        st.write(f"**Emergency Contact:** {profile.get('EmerContactName')} - {profile.get('EmerContactPhone')}")
        
        if profile.get('Allergies'):
            st.write(f"**Allergies:** {profile.get('Allergies')}")
        
        st.write("---")
        
        # Edit Profile Section
        st.subheader("Edit Profile")
        
        with st.form("edit_member_form"):
            first_name = st.text_input("First Name", value=profile.get('FirstName', ''))
            last_name = st.text_input("Last Name", value=profile.get('LastName', ''))
            preferred_name = st.text_input("Preferred Name", value=profile.get('PreferredName', ''))
            graduation_year = st.number_input("Graduation Year", 
                                            value=profile.get('GraduationYear') or 2025, 
                                            min_value=2020, max_value=2035)
            is_grad_student = st.checkbox("Graduate Student", 
                                        value=profile.get('IsGradStudent', False))
            
            car_plate = st.text_input("Car Plate", value=profile.get('CarPlate', ''))
            car_state = st.text_input("Car State", value=profile.get('CarState', ''))
            car_pass_count = st.number_input("Car Pass Count", 
                                           value=profile.get('CarPassCount') or 0, 
                                           min_value=0)
            
            emer_contact_name = st.text_input("Emergency Contact Name", 
                                            value=profile.get('EmerContactName', ''))
            emer_contact_phone = st.text_input("Emergency Contact Phone", 
                                             value=profile.get('EmerContactPhone', ''))
            
            if st.form_submit_button("Update Member"):
                update_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "preferred_name": preferred_name if preferred_name else None,
                    "graduation_year": graduation_year,
                    "is_grad_student": is_grad_student,
                    "car_plate": car_plate if car_plate else None,
                    "car_state": car_state if car_state else None,
                    "car_pass_count": car_pass_count if car_pass_count > 0 else None,
                    "emer_contact_name": emer_contact_name,
                    "emer_contact_phone": emer_contact_phone
                }
                
                try:
                    # Note: You'll need to add a PUT endpoint to your members API
                    update_response = requests.put(f"{API_BASE}/members/{member_id}", 
                                                 json=update_data)
                    if update_response.status_code == 200:
                        st.success("Member updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update member.")
                except Exception as e:
                    st.error(f"Error updating member: {e}")
            
    else:
        st.error("Could not load your profile information.")
        
except Exception as e:
    st.error(f"Failed to load profile: {e}")