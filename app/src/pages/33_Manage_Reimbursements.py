import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks()


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

        # Optional: Allow filtering by amount, date, etc.
        st.subheader("Filter Reimbursement Requests")
        
        filter_amount = st.slider("Filter by Amount", 0.0, float(df['amount'].max()), 0.0)
        filtered_df = df[df['amount'] >= filter_amount]
        
        st.write("### Filtered Reimbursement Requests")
        st.dataframe(filtered_df)

    else:
        st.write("No reimbursement requests found.")

else:
    st.error("You do not have permission to view this page. Only the Treasurer can view reimbursement requests.")
