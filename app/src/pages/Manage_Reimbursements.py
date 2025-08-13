import requests
import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

# Check if user has permission (treasurer or admin)
is_treasurer = st.session_state.get("role") in ["treasurer", "administrator", "vp"]

if is_treasurer:
    st.title("💰 Manage Reimbursement Requests")
    
    # Fetch reimbursement data
    try:
        reimbursement_data = requests.get("http://api:4000/reimbursements").json()
        
        if not reimbursement_data:
            st.info("No reimbursement requests found.")
        else:
            # Create DataFrame
            df = pd.DataFrame(reimbursement_data)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_requests = len(df)
                st.metric("Total Requests", total_requests)
            
            with col2:
                pending_requests = len(df[df["Status"] == "PENDING"])
                st.metric("Pending", pending_requests)
            
            with col3:
                approved_requests = len(df[df["Status"] == "APPROVED"])
                st.metric("Approved", approved_requests)
            
            with col4:
                total_amount = pd.to_numeric(df["Total"], errors="coerce").sum()
                st.metric("Total Amount", f"${total_amount:.2f}")
            
            st.write("---")
            
            # Filters
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                # Status filter
                status_options = ["All"] + list(df["Status"].unique())
                selected_status = st.selectbox("Filter by Status", options=status_options)
            
            with col_filter2:
              # Member filter - fetch names using API for each unique MemberID
              member_ids = df["MemberID"].unique().tolist()
              member_names = {}
              for member_id in member_ids:
                try:
                  resp = requests.get(f"http://api:4000/members/{member_id}")
                  if resp.status_code == 200:
                    data = resp.json()
                    member_data = data.get('member', {})  # Extract the member object
                    # Prefer PreferredName if available, else FirstName
                    first_name = member_data.get('PreferredName') or member_data.get('FirstName', '')
                    last_name = member_data.get('LastName', '')
                    full_name = f"{first_name} {last_name}".strip()
                    member_names[member_id] = full_name
                  else:
                    member_names[member_id] = f"ID {member_id}"
                except Exception:
                  member_names[member_id] = f"ID {member_id}"

              # Map MemberID to MemberName in df
              df["MemberName"] = df["MemberID"].map(member_names)

              member_options = ["All"] + sorted(set(member_names.values()))
              selected_member = st.selectbox("Filter by Member", options=member_options)
            
            # Apply filters
            filtered_df = df.copy()
            
            if selected_status != "All":
                filtered_df = filtered_df[filtered_df["Status"] == selected_status]
            
            if selected_member != "All":
                filtered_df = filtered_df[filtered_df["MemberName"] == selected_member]
            
            st.write(f"### Showing {len(filtered_df)} Reimbursement Requests")
            
            if len(filtered_df) > 0:
                # Display reimbursements with action buttons
                for index, row in filtered_df.iterrows():
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{row['MemberName']}** (ID: {row['MemberID']})")
                            # st.write(f"📅 {row['RequestDate']}")
                        
                        with col2:
                            st.write(f"**${float(row['Total']):.2f}**")
                            if pd.notna(row['Description']) and row['Description'].strip():
                                st.write(f"📝 {row['Description'][:50]}{'...' if len(str(row['Description'])) > 50 else ''}")
                            else:
                                st.write("📝 No description provided")
                        
                        with col3:
                            # Status badge
                            if row['Status'] == 'SUBMITTED':
                                st.write("🟡 **SUBMITTED**")
                            elif row['Status'] == 'APPROVED':
                                st.write("✅ **APPROVED**")
                            elif row['Status'] == 'REJECTED':
                                st.write("❌ **REJECTED**")
                            else:
                                st.write(f"**{row['Status']}**")
                        
                        with col4:
                            # Approve button (only for submitted requests)
                            if row['Status'] == 'SUBMITTED':
                                if st.button("✅ Approve", key=f"approve_{row['ID']}", type="primary"):
                                    try:
                                        response = requests.put(f"http://api:4000/reimbursements/{row['ID']}/approve")
                                        if response.status_code == 200:
                                            st.success(f"Approved reimbursement for {row['MemberName']}")
                                            st.rerun()
                                        else:
                                            st.error("Failed to approve reimbursement")
                                    except Exception as e:
                                        st.error(f"Error approving reimbursement: {e}")
                            else:
                                st.write("")  # Empty space for alignment
                        
                        with col5:
                            # View details button
                            if st.button("👁️ Details", key=f"details_{row['ID']}", help="View full details"):
                                st.session_state[f"show_details_{row['ID']}"] = not st.session_state.get(f"show_details_{row['ID']}", False)
                        
                        # Show details if toggled
                        if st.session_state.get(f"show_details_{row['ID']}", False):
                            st.info(f"""
                            **Full Details for Reimbursement #{row['ID']}:**
                            - **Member:** {row['MemberName']} (ID: {row['MemberID']})
                            - **Amount:** ${float(row['Total']):.2f}
                            - **Status:** {row['Status']}
                            - **Description:** {row['Description'] if pd.notna(row['Description']) else 'No description provided'}
                            """)
                        
                        st.write("---")
                
                # Bulk actions for pending requests
                pending_in_filter = filtered_df[filtered_df["Status"] == "PENDING"]
                if len(pending_in_filter) > 0:
                    st.write("### Bulk Actions")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if st.button("✅ Approve All Pending", type="secondary"):
                            success_count = 0
                            for _, row in pending_in_filter.iterrows():
                                try:
                                    response = requests.put(f"http://api:4000/reimbursements/{row['ID']}/approve")
                                    if response.status_code == 200:
                                        success_count += 1
                                except:
                                    pass
                            
                            if success_count > 0:
                                st.success(f"Approved {success_count} reimbursements!")
                                st.rerun()
                            else:
                                st.error("Failed to approve reimbursements")
                    
                    with col2:
                        st.info(f"This will approve {len(pending_in_filter)} pending reimbursements in the current filter")
                
                # Export functionality
                st.write("---")
                st.write("### Export Data")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Export filtered data as CSV
                    csv_data = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Filtered Data (CSV)",
                        data=csv_data,
                        file_name=f"reimbursements_filtered_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Export all data as CSV
                    csv_all = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download All Data (CSV)",
                        data=csv_all,
                        file_name=f"reimbursements_all_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            else:
                st.info("No reimbursements match the selected filters.")
                
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching reimbursement data: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

else:
    st.error("🚫 Access Denied: Only treasurers and administrators can view reimbursement requests.")
    st.info("Please contact your club administrator if you believe you should have access to this page.")