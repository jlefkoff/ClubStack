import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks()

# Assuming the role is set to 'Treasurer' (you can replace this with proper role management)
is_treasurer = True

if is_treasurer:
    st.title("View All Reimbursement Requests")

    # Check if there are any reimbursement requests
    if 'reimbursement_requests' in st.session_state and st.session_state['reimbursement_requests']:
        # Convert the reimbursement requests to a DataFrame for display
        reimbursement_data = st.session_state['reimbursement_requests']
        
        # Create a DataFrame for easy display and filtering
        df = pd.DataFrame(reimbursement_data)

        # Show the table with all reimbursement requests
        st.write("### All Submitted Reimbursement Requests")
        st.dataframe(df)

        # Filter by Member ID
        member_ids = df['member_id'].unique()  # Get unique member IDs from the requests
        selected_member_id = st.selectbox("Select Member ID to Filter", options=member_ids)

        # Filter the dataframe based on selected member_id
        filtered_df = df[df['member_id'] == selected_member_id]

        st.write(f"### Reimbursement Requests for Member ID: {selected_member_id}")
        st.dataframe(filtered_df)

    else:
        st.write("No reimbursement requests found.")

else:
    st.error("You do not have permission to view this page. Only the Treasurer can view reimbursement requests.")
