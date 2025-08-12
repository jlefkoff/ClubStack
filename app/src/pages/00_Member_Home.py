from modules.nav import SideBarLinks
import streamlit as st
import logging
import requests
import datetime

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")

BASE_URL = "http://api:4000"

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome to Your Member Portal, {st.session_state['first_name']}.")
st.write("")

member_id = st.session_state["member_id"]

# Get member data
try:
    response = requests.get(f"{BASE_URL}/members/{member_id}").json()
    member_data = response["member"]
    
    activation_date_str = member_data.get("ActivationDate", None)
    if activation_date_str:
        # Parse the date string
        activation_date = datetime.datetime.strptime(activation_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        # Add one year
        valid_until = activation_date + datetime.timedelta(days=365)
        valid_until_str = valid_until.strftime("%B %d, %Y")
    else:
        valid_until_str = "Unknown"
    
    st.write(f"### Membership Valid Until: {valid_until_str}")
    
except Exception as e:
    st.error("Could not load member data")
    valid_until_str = "Unknown"

st.write("")
st.write("---")

# Create main grid layout
col1, col2, col3 = st.columns(3)

# ==================== COLUMN 1 ====================
with col1:
    # GEAR RESERVATIONS
    with st.container():
        st.subheader("🎒 My Gear Reservations")
        try:
            # Get current gear reservations for the member
            gear_response = requests.get(f"{BASE_URL}/gear/reservations/{member_id}")
            if gear_response.status_code == 200:
                reservations = gear_response.json()
                if reservations:
                    # Show next 3 upcoming reservations
                    upcoming_reservations = [r for r in reservations if datetime.datetime.strptime(r['CheckOutDate'], '%Y-%m-%d').date() >= datetime.date.today()][:3]
                    
                    if upcoming_reservations:
                        for reservation in upcoming_reservations:
                            with st.expander(f"Reservation #{reservation['ID']} - {reservation['CheckOutDate']}"):
                                st.write(f"**Check Out:** {reservation['CheckOutDate']}")
                                st.write(f"**Return:** {reservation['ReturnDate']}")
                                if 'Items' in reservation:
                                    st.write(f"**Items:** {', '.join(reservation['Items'])}")
                    else:
                        st.info("No upcoming reservations")
                        
                    if st.button("View All Reservations", key="gear_btn", use_container_width=True):
                        st.switch_page("pages/03_My_Gear.py")
                else:
                    st.info("No gear reservations")
            else:
                st.warning("Could not load gear reservations")
        except:
            st.warning("Gear service unavailable")
    
    st.write("")
    
    # EVENT RSVPs  
    with st.container():
        st.subheader("📅 My Event RSVPs")
        try:
            # Get member's event RSVPs
            rsvp_response = requests.get(f"{BASE_URL}/events/rsvps/member/{member_id}")
            if rsvp_response.status_code == 200:
                rsvps = rsvp_response.json()
                if rsvps:
                    # Show next 3 upcoming events
                    upcoming_events = sorted([r for r in rsvps if datetime.datetime.strptime(r['EventDate'], '%Y-%m-%d').date() >= datetime.date.today()], 
                                           key=lambda x: x['EventDate'])[:3]
                    
                    if upcoming_events:
                        for rsvp in upcoming_events:
                            status_icon = "✅" if rsvp['Status'] == 'Going' else "❓" if rsvp['Status'] == 'Maybe' else "❌"
                            with st.expander(f"{status_icon} {rsvp['EventTitle']} - {rsvp['EventDate']}"):
                                st.write(f"**Date:** {rsvp['EventDate']}")
                                st.write(f"**Status:** {rsvp['Status']}")
                                st.write(f"**Type:** {rsvp.get('EventType', 'Event')}")
                    else:
                        st.info("No upcoming RSVPs")
                        
                    if st.button("View All Events", key="events_btn", use_container_width=True):
                        st.switch_page("pages/05_Events.py")
                else:
                    st.info("No event RSVPs")
            else:
                st.warning("Could not load event RSVPs")
        except:
            st.warning("Events service unavailable")

# ==================== COLUMN 2 ====================
with col2:
    # EVENTS CALENDAR
    with st.container():
        st.subheader("🗓️ Upcoming Events")
        try:
            # Get upcoming events
            events_response = requests.get(f"{BASE_URL}/events")
            if events_response.status_code == 200:
                events = events_response.json()
                if events:
                    # Show next 4 upcoming events
                    for event in events[:4]:
                        event_date = datetime.datetime.strptime(event['Date'], '%Y-%m-%d').date()
                        days_until = (event_date - datetime.date.today()).days
                        
                        with st.container():
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.write(f"**{event['Title']}**")
                                st.write(f"📍 {event.get('Location', 'TBD')}")
                                st.write(f"📅 {event['Date']}")
                            with col_b:
                                if days_until == 0:
                                    st.write("🔥 **TODAY**")
                                elif days_until == 1:
                                    st.write("📅 **Tomorrow**")
                                elif days_until <= 7:
                                    st.write(f"📅 **{days_until}d**")
                                else:
                                    st.write(f"📅 {days_until}d")
                            st.write("---")
                else:
                    st.info("No upcoming events")
                    
                if st.button("View Full Calendar", key="calendar_btn", use_container_width=True):
                    st.switch_page("pages/05_Events.py")
            else:
                st.warning("Could not load events calendar")
        except:
            st.warning("Events service unavailable")
    
    st.write("")
    
    # COMMUNICATIONS
    with st.container():
        st.subheader("📧 Recent Communications")
        try:
            # Get recent communications/announcements for member
            comms_response = requests.get(f"{BASE_URL}/communications/{member_id}")
            if comms_response.status_code == 200:
                communications = comms_response.json()
                if communications:
                    # Show most recent 3 communications
                    for comm in communications[:3]:
                        comm_date = datetime.datetime.strptime(comm['SentAt'], '%Y-%m-%d %H:%M:%S').strftime('%m/%d')
                        
                        with st.expander(f"📧 {comm['Subject']} - {comm_date}"):
                            st.write(f"**From:** {comm.get('SenderName', 'Club Admin')}")
                            st.write(f"**Date:** {comm['SentAt']}")
                            if 'Preview' in comm:
                                st.write(f"**Preview:** {comm['Preview']}")
                            
                            # Mark as read button
                            if not comm.get('IsRead', True):
                                if st.button("Mark as Read", key=f"read_{comm['ID']}", use_container_width=True):
                                    # API call to mark as read
                                    requests.post(f"{BASE_URL}/communications/{comm['ID']}/read")
                                    st.rerun()
                else:
                    st.info("No recent communications")
                    
                if st.button("View All Messages", key="comms_btn", use_container_width=True):
                    st.switch_page("pages/07_Communications.py")
            else:
                st.warning("Could not load communications")
        except:
            st.warning("Communications service unavailable")

# ==================== COLUMN 3 ====================
with col3:
    # MY NOMINATIONS
    with st.container():
        st.subheader("🗳️ My Nominations")
        try:
            # Get pending nominations for the member
            nominations_response = requests.get(f"{BASE_URL}/elections/nominations/pending/{member_id}")
            if nominations_response.status_code == 200:
                nominations = nominations_response.json()
                if nominations:
                    st.write(f"**{len(nominations)} pending nomination(s)**")
                    
                    for nom in nominations:
                        with st.expander(f"🏛️ {nom['PositionTitle']} - {nom['ElectionDate']}"):
                            st.write(f"**Position:** {nom['PositionTitle']}")
                            st.write(f"**Nominated by:** {nom['NominatorName']}")
                            st.write(f"**Election Date:** {nom['ElectionDate']}")
                            st.write(f"**Deadline:** {nom['NominateBy']}")
                            
                            col_accept, col_decline = st.columns(2)
                            with col_accept:
                                if st.button("✅ Accept", key=f"accept_{nom['ID']}", use_container_width=True):
                                    accept_data = {"accepted": True}
                                    accept_response = requests.put(f"{BASE_URL}/elections/nominations/{nom['ID']}/accept", json=accept_data)
                                    if accept_response.status_code == 200:
                                        st.success("Nomination accepted!")
                                        st.rerun()
                            with col_decline:
                                if st.button("❌ Decline", key=f"decline_{nom['ID']}", use_container_width=True):
                                    decline_data = {"accepted": False}
                                    decline_response = requests.put(f"{BASE_URL}/elections/nominations/{nom['ID']}/accept", json=decline_data)
                                    if decline_response.status_code == 200:
                                        st.success("Nomination declined!")
                                        st.rerun()
                else:
                    st.info("No pending nominations")
            else:
                st.info("No nominations found")
                
            # Check for available ballots
            ballots_response = requests.get(f"{BASE_URL}/elections/ballots/member/{member_id}")
            if ballots_response.status_code == 200:
                ballots = ballots_response.json()
                unvoted_ballots = [b for b in ballots if not b['HasVoted']]
                
                if unvoted_ballots:
                    st.write("---")
                    st.write(f"**🗳️ {len(unvoted_ballots)} ballot(s) available**")
                    
                    for ballot in unvoted_ballots[:2]:  # Show max 2
                        if st.button(f"Vote for {ballot['PositionTitle']}", key=f"vote_{ballot['BallotID']}", use_container_width=True):
                            st.switch_page("pages/06_Voting.py")
                            
            if st.button("View Elections", key="elections_btn", use_container_width=True):
                st.switch_page("pages/06_Voting.py")
        except:
            st.warning("Elections service unavailable")
    
    st.write("")
    
    # QUICK ACTIONS
    with st.container():
        st.subheader("⚡ Quick Actions")
        
        if st.button("👤 Member Profile", key="profile", use_container_width=True, type="secondary"):
            st.switch_page("pages/09_Member_Profile.py")
        
        if st.button("💰 Submit Reimbursement", key="reimburse", use_container_width=True, type="secondary"):
            st.switch_page("pages/31_Reimbursed.py")

# ==================== BOTTOM SECTION ====================
st.write("")
st.write("---")

# Member stats row
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric("Member Since", activation_date_str.split(',')[1].strip() if activation_date_str else "Unknown")

with stat_col2:
    # Count gear reservations
    try:
        gear_count = len(requests.get(f"{BASE_URL}/gear/reservations/member/{member_id}").json())
        st.metric("Gear Reservations", gear_count)
    except:
        st.metric("Gear Reservations", "—")

with stat_col3:
    # Count event RSVPs
    try:
        rsvp_count = len(requests.get(f"{BASE_URL}/events/rsvps/member/{member_id}").json())
        st.metric("Event RSVPs", rsvp_count)
    except:
        st.metric("Event RSVPs", "—")

with stat_col4:
    # Count unread communications
    try:
        comms = requests.get(f"{BASE_URL}/communications/{member_id}").json()
        unread_count = len([c for c in comms.get('messages') if not c.get('IsRead', True)])
        st.metric("Unread Messages", unread_count)
    except:
        st.metric("Unread Messages", "—")