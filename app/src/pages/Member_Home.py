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
        activation_date = datetime.datetime.strptime(
            activation_date_str, "%a, %d %b %Y %H:%M:%S %Z"
        )
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
                    for reservation in reservations:
                        with st.expander(
                            f"Reservation #{reservation['ID']} - {reservation['CheckOutDate']}"
                        ):
                            st.write(f"**Check Out:** {reservation['CheckOutDate']}")
                            st.write(f"**Return:** {reservation['ReturnDate']}")
                            st.write(f"**Item:** {reservation['Name']}")
                    if st.button(
                        "View All Reservations",
                        key="gear_btn",
                        use_container_width=True,
                    ):
                        st.switch_page("pages/My_Gear.py")
                else:
                    st.info("No gear reservations")
                if st.button(
                    "Reserve Gear", key="gear_page_btn", use_container_width=True
                ):
                    st.switch_page("pages/Browse_Gear.py")
            else:
                st.warning("Could not load gear reservations")
        except Exception as e:
            st.warning("Gear service unavailable")

    st.write("")

    # EVENT RSVPs
    with st.container():
        st.subheader("📅 My Event RSVPs")
        try:
            # Get member's event RSVPs
            rsvp_response = requests.get(f"{BASE_URL}/events/rsvp/{member_id}")
            if rsvp_response.status_code == 200:
                rsvps = rsvp_response.json()
                if rsvps:
                    # Fetch event details for each RSVP
                    upcoming_events = []

                    for rsvp in rsvps:
                        try:
                            # Get event details
                            event_response = requests.get(
                                f"{BASE_URL}/events/{rsvp['Event']}"
                            )
                            if event_response.status_code == 200:
                                event = event_response.json()

                                # Check if event is upcoming
                                try:
                                    event_date = datetime.datetime.strptime(
                                        event["EventDate"], "%a, %d %b %Y %H:%M:%S %Z"
                                    ).date()
                                    if event_date >= datetime.date.today():
                                        # Add RSVP info to event
                                        event["rsvp_info"] = rsvp
                                        upcoming_events.append(event)
                                except:
                                    # If date parsing fails, still show the event
                                    event["rsvp_info"] = rsvp
                                    upcoming_events.append(event)
                        except:
                            continue

                    # Sort by date and show top 3
                    upcoming_events = sorted(
                        upcoming_events, key=lambda x: x.get("EventDate", "")
                    )[:3]

                    if upcoming_events:
                        for event in upcoming_events:
                            rsvp = event["rsvp_info"]
                            # Format the date for display
                            try:
                                event_date = datetime.datetime.strptime(
                                    event["EventDate"], "%a, %d %b %Y %H:%M:%S %Z"
                                ).strftime("%Y-%m-%d")
                            except:
                                event_date = event["EventDate"]

                            with st.expander(f"✅ {event['Name']} - {event_date}"):
                                st.write(f"**Date:** {event_date}")
                                st.write(f"**Location:** {event['EventLoc']}")
                                st.write(f"**Meet Location:** {event['MeetLoc']}")
                                st.write(f"**Type:** {event['EventType']}")
                                if event.get("RecItems"):
                                    st.write(
                                        f"**Recommended Items:** {event['RecItems']}"
                                    )
                    else:
                        st.info("No upcoming RSVPs")

                    if st.button(
                        "View All Events", key="events_btn", use_container_width=True
                    ):
                        st.switch_page("pages/Events.py")
                else:
                    st.info("No event RSVPs")
            else:
                st.warning("Could not load event RSVPs")
        except Exception as e:
            logger.error(f"Error loading RSVPs: {e}")
            st.warning("Events service unavailable")

# ==================== COLUMN 2 ====================
with col2:
    # EVENTS CALENDAR - Compact Version
    with st.container():
        st.subheader("🗓️ Upcoming Events")
        try:
            # Get upcoming events
            events_response = requests.get(f"{BASE_URL}/events")
            if events_response.status_code == 200:
                events = events_response.json()
                if events:
                    # Filter and sort upcoming events
                    upcoming_events = []
                    for event in events:
                        try:
                            event_date = datetime.datetime.strptime(
                                event["EventDate"], "%Y-%m-%d"
                            ).date()
                            if event_date >= datetime.date.today():
                                days_until = (event_date - datetime.date.today()).days
                                event["days_until"] = days_until
                                upcoming_events.append(event)
                        except:
                            continue

                    upcoming_events = sorted(
                        upcoming_events, key=lambda x: x["days_until"]
                    )[:4]

                    for event in upcoming_events:
                        # Compact event display
                        with st.container():
                            # Single row layout with clickable RSVP
                            col_event, col_rsvp = st.columns([3, 1])

                            with col_event:
                                st.write(
                                    f"**{event['Name'][:25]}{'...' if len(event['Name']) > 25 else ''}**"
                                )
                                st.write(
                                    f"📅 {event['EventDate']} • 📍 {event.get('MeetLoc', 'TBD')}"
                                )

                            with col_rsvp:
                                days_until = event["days_until"]
                                if days_until == 0:
                                    st.write("🔥 TODAY")
                                elif days_until <= 3:
                                    st.write(f"⚡ {days_until}d")
                                else:
                                    st.write(f"{days_until}d")

                                # RSVP Button
                                # Check if user already RSVP'd to this event
                                user_rsvp_key = f"rsvp_success_{event['ID']}"

                                if st.session_state.get(user_rsvp_key, False):
                                    st.write("✅ **RSVP'd**")
                                else:
                                    if st.button(
                                        "RSVP",
                                        key=f"rsvp_{event['ID']}",
                                        use_container_width=True,
                                        type="secondary",
                                    ):
                                        # Quick RSVP - default to "Going"
                                        rsvp_data = {
                                            "member_id": member_id,
                                            "event_id": event["ID"],
                                            "avail_start": f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
                                            "avail_end": f"{datetime.datetime.now() + datetime.timedelta(days=7):%Y-%m-%d %H:%M:%S}",
                                        }
                                        try:
                                            rsvp_response = requests.post(
                                                f"{BASE_URL}/events/rsvp",
                                                json=rsvp_data,
                                            )
                                            if rsvp_response.status_code in [200, 201]:
                                                st.session_state[user_rsvp_key] = True
                                                st.rerun()
                                            else:
                                                st.error("Failed to RSVP")
                                        except Exception as ex:
                                            logger.error(f"Error submitting RSVP: {ex}")
                                            st.error("Could not submit RSVP")
                        st.write("---")
                else:
                    st.info("No upcoming events")

                if st.button(
                    "View Full Calendar", key="calendar_btn", use_container_width=True
                ):
                    st.switch_page("pages/05_Events.py")
            else:
                st.warning("Could not load events calendar")
        except Exception as e:
            st.warning("Events service unavailable")

    st.write("")

    # COMMUNICATIONS - Compact Version
    with st.container():
        st.subheader("📧 Recent Communications")
        try:
            # Get recent communications/announcements for member
            comms_response = requests.get(f"{BASE_URL}/communications/{member_id}")
            if comms_response.status_code == 200:
                communications = comms_response.json()
                if (
                    communications
                    and "messages" in communications
                    and communications["messages"]
                ):
                    # Show most recent 2 communications (reduced from 3)
                    for comm in communications["messages"][:2]:
                        comm_date = datetime.datetime.strptime(
                            comm["DateSent"], "%a, %d %b %Y %H:%M:%S %Z"
                        ).strftime("%m/%d")

                        # Compact communication display
                        with st.container():
                            col_comm, col_status = st.columns([4, 1])

                            with col_comm:
                                st.write(
                                    f"**{comm['Subject'][:30]}{'...' if len(comm['Subject']) > 30 else ''}**"
                                )
                                st.write(f"📅 {comm_date}")

                            with col_status:
                                if not comm.get("IsRead", True):
                                    if st.button(
                                        "📖",
                                        key=f"read_{comm['ID']}",
                                        help="Mark as Read",
                                    ):
                                        requests.post(
                                            f"{BASE_URL}/communications/{comm['ID']}/read"
                                        )
                                        st.rerun()
                                else:
                                    st.write("✅")
                        st.write("---")
                else:
                    st.info("No recent communications")

                if st.button(
                    "View All Messages", key="comms_btn", use_container_width=True
                ):
                    st.switch_page("pages/Communications.py")
            else:
                st.warning("Could not load communications")
        except Exception as e:
            st.warning("Communications service unavailable")
            st.error(f"Error: {str(e)}")

# ==================== COLUMN 3 ====================
with col3:
    # MY NOMINATIONS
    with st.container():
        st.subheader("🗳️ My Nominations")
        try:
            # Get pending nominations for the member
            nominations_response = requests.get(
                f"{BASE_URL}/elections/nominations/pending/{member_id}"
            )
            if nominations_response.status_code == 200:
                nominations = nominations_response.json()
                if nominations:
                    st.write(f"**{len(nominations)} pending nomination(s)**")

                    for nom in nominations:
                        with st.expander(
                            f"🏛️ {nom['PositionTitle']} - {nom['ElectionDate']}"
                        ):
                            st.write(f"**Position:** {nom['PositionTitle']}")
                            st.write(f"**Nominated by:** {nom['NominatorName']}")
                            st.write(f"**Election Date:** {nom['ElectionDate']}")
                            st.write(f"**Deadline:** {nom['NominateBy']}")

                            col_accept, col_decline = st.columns(2)
                            with col_accept:
                                if st.button(
                                    "✅ Accept",
                                    key=f"accept_{nom['ID']}",
                                    use_container_width=True,
                                ):
                                    accept_data = {"accepted": True}
                                    accept_response = requests.put(
                                        f"{BASE_URL}/elections/nominations/{nom['ID']}/accept",
                                        json=accept_data,
                                    )
                                    if accept_response.status_code == 200:
                                        st.success("Nomination accepted!")
                                        st.rerun()
                            with col_decline:
                                if st.button(
                                    "❌ Decline",
                                    key=f"decline_{nom['ID']}",
                                    use_container_width=True,
                                ):
                                    decline_data = {"accepted": False}
                                    decline_response = requests.put(
                                        f"{BASE_URL}/elections/nominations/{nom['ID']}/accept",
                                        json=decline_data,
                                    )
                                    if decline_response.status_code == 200:
                                        st.success("Nomination declined!")
                                        st.rerun()
                else:
                    st.info("No pending nominations")
            else:
                st.info("No nominations found")

            # Check for available ballots
            ballots_response = requests.get(
                f"{BASE_URL}/elections/ballots/member/{member_id}"
            )
            if ballots_response.status_code == 200:
                ballots = ballots_response.json()
                unvoted_ballots = [b for b in ballots if not b["HasVoted"]]

                if unvoted_ballots:
                    st.write("---")
                    st.write(f"**🗳️ {len(unvoted_ballots)} ballot(s) available**")

                    for ballot in unvoted_ballots[:2]:  # Show max 2
                        if st.button(
                            f"Vote for {ballot['PositionTitle']}",
                            key=f"vote_{ballot['BallotID']}",
                            use_container_width=True,
                        ):
                            st.switch_page("pages/Voting.py")

            if st.button(
                "View Elections", key="elections_btn", use_container_width=True
            ):
                st.switch_page("pages/Voting.py")
        except Exception as e:
            st.error(f"Error loading nominations: {e}")
            st.warning("Elections service unavailable")

    st.write("")

    # QUICK ACTIONS
    with st.container():
        st.subheader("⚡ Quick Actions")

        if st.button(
            "👤 Member Profile",
            key="profile",
            use_container_width=True,
            type="secondary",
        ):
            st.switch_page("pages/Member_Profile.py")

        if st.button(
            "💰 Submit Reimbursement",
            key="reimburse",
            use_container_width=True,
            type="secondary",
        ):
            st.switch_page("pages/Submit_Reimbursement.py")

# ==================== BOTTOM SECTION ====================
st.write("")
st.write("---")

# Member stats row
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric(
        "Member Since",
        activation_date_str.split(",")[1].strip() if activation_date_str else "Unknown",
    )

with stat_col2:
    # Count gear reservations
    try:
        gear_count = len(
            requests.get(f"{BASE_URL}/gear/reservations/{member_id}").json()
        )
        st.metric("Gear Reservations", gear_count)
    except Exception as e:
        st.error(f"Error fetching gear: {e}")
        st.metric("Gear Reservations", "—")

with stat_col3:
    # Count event RSVPs
    try:
        rsvp_count = len(requests.get(f"{BASE_URL}/events/rsvp/{member_id}").json())
        st.metric("Event RSVPs", rsvp_count)
    except:
        st.metric("Event RSVPs", "—")

with stat_col4:
    # Count unread communications
    try:
        comms = requests.get(f"{BASE_URL}/communications/{member_id}").json()
        count = len([msg for msg in comms.get("messages", [])])
        st.metric("Messages", count)
    except:
        st.metric("Messages", "—")
