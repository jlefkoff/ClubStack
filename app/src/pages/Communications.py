from modules.nav import SideBarLinks
import streamlit as st
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

# Define the base URL for the API
BASE_URL = "http://api:4000"
member_id = st.session_state.get("member_id")
user_role = st.session_state.get("role", "member")

st.title("📧 Communications")

# Check if user can send communications
is_admin = user_role in ["administrator", "vp", "president", "secretary"]

# Create tabs based on user role
if is_admin:
    tab1, tab2 = st.tabs(["📨 Send Messages", "📥 My Messages"])
    
    # ==================== SEND MESSAGES TAB ====================
    with tab1:
        st.header("Send Mass Communication")
        
        # Fetch all members for recipient selection
        try:
            members_response = requests.get(f"{BASE_URL}/members")
            if members_response.status_code == 200:
                all_members = members_response.json()
                
                # Ensure all_members is a list
                if isinstance(all_members, dict) and 'members' in all_members:
                    all_members = all_members['members']
                elif not isinstance(all_members, list):
                    st.error("Unexpected data format from members API")
                    all_members = []

                # Initialize selected members if not exists
                if 'selected_members' not in st.session_state:
                    st.session_state.selected_members = []

                # Quick selection buttons (must be outside the form)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Select All", type="secondary", use_container_width=True):
                        st.session_state.selected_members = [m['ID'] for m in all_members if isinstance(m, dict)]
                        st.rerun()
                with col_b:
                    if st.button("Clear All", type="secondary", use_container_width=True):
                        st.session_state.selected_members = []
                        st.rerun()

                with st.form("send_communication"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        subject = st.text_input("Subject", placeholder="Enter message subject...")
                        content = st.text_area("Message", placeholder="Enter your message...", height=150)

                    with col2:
                        st.subheader("Recipients")

                        # Filter by role option
                        role_filter = st.selectbox("Filter by Role", ["All", "member", "treasurer", "vp", "president", "secretary", "administrator"])

                        if role_filter != "All":
                            filtered_members = [m for m in all_members if isinstance(m, dict) and m.get('Role', 'member') == role_filter]
                        else:
                            filtered_members = all_members

                        # Member selection with checkboxes
                        st.write("**Select Members:**")
                        
                        # Create a container for member checkboxes with max height
                        with st.container():
                            if len(filtered_members) > 0:
                                # Display members with checkboxes
                                for member in sorted(filtered_members, key=lambda x: f"{x.get('FirstName', '')} {x.get('LastName', '')}"):
                                    if isinstance(member, dict):
                                        member_name = f"{member.get('FirstName', 'Unknown')} {member.get('LastName', 'User')}"
                                        is_selected = member['ID'] in st.session_state.selected_members
                                        
                                        # Use a unique key for each checkbox
                                        checkbox_key = f"member_checkbox_{member['ID']}"
                                        selected = st.checkbox(
                                            f"{member_name} (ID: {member['ID']})", 
                                            key=checkbox_key, 
                                            value=is_selected
                                        )
                                        
                                        # Update selection state
                                        if selected and member['ID'] not in st.session_state.selected_members:
                                            st.session_state.selected_members.append(member['ID'])
                                        elif not selected and member['ID'] in st.session_state.selected_members:
                                            st.session_state.selected_members.remove(member['ID'])
                            else:
                                st.info("No members found for selected role filter")

                        st.write(f"**Selected: {len(st.session_state.selected_members)} members**")

                    # Send button - THIS IS THE MISSING SUBMIT BUTTON
                    submitted = st.form_submit_button("📤 Send Message", type="primary", use_container_width=True)

                    if submitted:
                        if not subject or not content:
                            st.error("Please fill in both subject and message")
                        elif not st.session_state.get('selected_members'):
                            st.error("Please select at least one recipient")
                        else:
                            # Send the communication
                            communication_data = {
                                "subject": subject,
                                "content": content,
                                "recipients": st.session_state.selected_members
                            }

                            try:
                                response = requests.post(f"{BASE_URL}/communications", json=communication_data)
                                if response.status_code == 201:
                                    st.success(f"✅ Message sent successfully to {len(st.session_state.selected_members)} members!")
                                    # Clear form
                                    st.session_state.selected_members = []
                                else:
                                    error_msg = response.json().get('error', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else 'Unknown error'
                                    st.error(f"Failed to send message: {error_msg}")
                            except Exception as e:
                                st.error(f"Error sending message: {str(e)}")
            else:
                st.error("Could not load members list")

        except Exception as e:
            st.error(f"Error loading members: {str(e)}")
            logger.error(f"Error loading members: {e}")
    
    # ==================== MY MESSAGES TAB ====================
    with tab2:
        st.header("My Received Messages")
        
        try:
            # Get messages for the current user
            messages_response = requests.get(f"{BASE_URL}/communications/{member_id}")
            if messages_response.status_code == 200:
                data = messages_response.json()
                messages = data.get('messages', [])
                
                if messages:
                    # Search and filter options
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        search_term = st.text_input("🔍 Search messages...", placeholder="Search by subject or content")
                    with col2:
                        days_filter = st.selectbox("Show messages from", ["All time", "Last 7 days", "Last 30 days", "Last 90 days"])
                    
                    # Apply filters
                    filtered_messages = messages
                    
                    # Date filter
                    if days_filter != "All time":
                        days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
                        cutoff_days = days_map[days_filter]
                        cutoff_date = datetime.now() - timedelta(days=cutoff_days)
                        
                        filtered_messages = []
                        for msg in messages:
                            try:
                                msg_date = datetime.strptime(msg['DateSent'], '%a, %d %b %Y %H:%M:%S %Z')
                                if msg_date >= cutoff_date:
                                    filtered_messages.append(msg)
                            except:
                                # If date parsing fails, include the message
                                filtered_messages.append(msg)
                    
                    # Search filter
                    if search_term:
                        filtered_messages = [
                            msg for msg in filtered_messages 
                            if search_term.lower() in msg.get('Subject', '').lower() 
                            or search_term.lower() in msg.get('Content', '').lower()
                        ]
                    
                    st.write(f"**Showing {len(filtered_messages)} of {len(messages)} messages**")
                    st.write("---")
                    
                    # Display messages
                    for message in filtered_messages:
                        # Format date
                        try:
                            msg_date = datetime.strptime(message['DateSent'], '%a, %d %b %Y %H:%M:%S %Z')
                            formatted_date = msg_date.strftime('%B %d, %Y at %I:%M %p')
                        except:
                            formatted_date = message['DateSent']
                        
                        # Message card
                        with st.expander(f"📧 {message['Subject']} - {formatted_date}"):
                            st.write(f"**Subject:** {message['Subject']}")
                            st.write(f"**Date:** {formatted_date}")
                            st.write(f"**Message:**")
                            st.write(message['Content'])
                            
                            # Delete button for admins
                            if st.button(f"🗑️ Delete", key=f"delete_{message['ID']}", help="Delete this message"):
                                try:
                                    delete_response = requests.delete(f"{BASE_URL}/communications/{message['ID']}")
                                    if delete_response.status_code == 200:
                                        st.success("Message deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete message")
                                except:
                                    st.error("Error deleting message")
                else:
                    st.info("📭 No messages received yet")
            else:
                st.error("Could not load messages")
        except Exception as e:
            st.error(f"Error loading messages: {str(e)}")

else:
    # ==================== MEMBER VIEW (READ ONLY) ====================
    st.header("My Messages")
    
    try:
        # Get messages for the current user
        messages_response = requests.get(f"{BASE_URL}/communications/{member_id}")
        if messages_response.status_code == 200:
            data = messages_response.json()
            messages = data.get('messages', [])
            
            if messages:
                # Search functionality
                search_term = st.text_input("🔍 Search messages...", placeholder="Search by subject or content")
                
                # Apply search filter
                if search_term:
                    filtered_messages = [
                        msg for msg in messages 
                        if search_term.lower() in msg.get('Subject', '').lower() 
                        or search_term.lower() in msg.get('Content', '').lower()
                    ]
                else:
                    filtered_messages = messages
                
                st.write(f"**{len(filtered_messages)} messages**")
                st.write("---")
                
                # Display messages
                for message in filtered_messages:
                    # Format date
                    try:
                        msg_date = datetime.strptime(message['DateSent'], '%a, %d %b %Y %H:%M:%S %Z')
                        formatted_date = msg_date.strftime('%B %d, %Y at %I:%M %p')
                    except:
                        formatted_date = message['DateSent']
                    
                    # Message card
                    with st.expander(f"📧 {message['Subject']} - {formatted_date}"):
                        st.write(f"**Subject:** {message['Subject']}")
                        st.write(f"**Date:** {formatted_date}")
                        st.write(f"**Message:**")
                        st.write(message['Content'])
            else:
                st.info("📭 No messages received yet")
        else:
            st.error("Could not load messages")
    except Exception as e:
        st.error(f"Error loading messages: {str(e)}")

# Footer
st.write("")
st.write("---")
if is_admin:
    st.info("💡 **Admin Tip**: You can send messages to specific members or all members at once. Use role filters to target specific groups.")
else:
    st.info("💡 **Tip**: This is where you'll receive important club announcements and updates from leadership.")