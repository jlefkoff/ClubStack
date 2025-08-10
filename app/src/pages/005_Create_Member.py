import streamlit as st
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")


from modules.nav import SideBarLinks
SideBarLinks()


st.title("Create New Member")

# Form to input new member data
with st.form("new_member_form"):
    st.subheader("Enter New Member Information")
        
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    member_id = st.text_input("Member ID")
    join_date = st.date_input("Join Date", value=datetime.now())

    # Submit button to add the new member
    submit_button = st.form_submit_button("Add Member")

    if submit_button:
        if not first_name or not last_name or not email or not member_id:
            st.error("Please fill in all fields.")
        else:
            # Add the new member to session state or a database
            new_member = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "member_id": member_id,
                "join_date": join_date.strftime('%Y-%m-%d')
            }
                
            # Here we store the new member in session state for simplicity (in real apps, use a database)
            if 'members' not in st.session_state:
                st.session_state['members'] = []  
            
                st.session_state['members'].append(new_member)  
                
                st.success(f"New member {first_name} {last_name} added successfully!")

                # View the members
                st.write("### All Members:")
                st.write(st.session_state['members'])

