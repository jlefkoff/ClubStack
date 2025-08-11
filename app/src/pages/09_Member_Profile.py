import streamlit as st
from modules.nav import SideBarLinks
from datetime import datetime

# Set page config for layout
st.set_page_config(layout="wide")

# Add sidebar links (using the imported function)
SideBarLinks()

# Ensure session state variables are available
if 'first_name' not in st.session_state:
    st.session_state['first_name'] = 'Guest'
if 'last_name' not in st.session_state:
    st.session_state['last_name'] = 'User'
if 'member_id' not in st.session_state:
    st.session_state['member_id'] = 'Not Assigned'
if 'email' not in st.session_state:
    st.session_state['email'] = 'not_assigned@example.com'
if 'join_date' not in st.session_state:
    st.session_state['join_date'] = datetime.now().strftime('%Y-%m-%d')

# Display member profile
st.title(f"Member Profile: {st.session_state['first_name']} {st.session_state['last_name']}")
st.write(f"### Member ID: {st.session_state['member_id']}")
st.write(f"### Email: {st.session_state['email']}")
st.write(f"### Join Date: {st.session_state['join_date']}")

# Update profile form
st.subheader("Update Profile Information")
updated_first_name = st.text_input("First Name", value=st.session_state['first_name'])
updated_last_name = st.text_input("Last Name", value=st.session_state['last_name'])
updated_email = st.text_input("Email", value=st.session_state['email'])
updated_member_id = st.text_input("Member ID", value=st.session_state['member_id'])
updated_join_date = st.date_input("Join Date", value=datetime.strptime(st.session_state['join_date'], '%Y-%m-%d'))

# Button to update the session state
if st.button("Update Profile", use_container_width=True):
    st.session_state['first_name'] = updated_first_name
    st.session_state['last_name'] = updated_last_name
    st.session_state['email'] = updated_email
    st.session_state['member_id'] = updated_member_id
    st.session_state['join_date'] = updated_join_date.strftime('%Y-%m-%d')
    st.success("Profile updated successfully!")