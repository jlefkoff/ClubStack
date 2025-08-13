from modules.nav import SideBarLinks
import streamlit as st
import requests
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

# API base URL
API_BASE = "http://api:4000/elections"

st.title("🗳️ Election Administration")
st.write("Complete election management system for administrators")

# Create tabs for different admin functions
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📋 Overview",
        "🏛️ Setup",
        "👥 Nominations",
        "🗳️ Ballots & Voting",
        "🏆 Results",
        "📊 Reports",
    ]
)

# ==================== OVERVIEW TAB ====================
with tab1:
    st.header("Election Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Elections")
        try:
            response = requests.get(f"{API_BASE}/")
            if response.status_code == 200:
                elections = response.json()
                if elections:
                    for election in elections[:3]:  # Show top 3
                        with st.container():
                            st.write(f"**{election['TermName']}**")
                            st.write(f"Date: {election['Date']}")
                            st.write(f"Positions: {election['Positions']}")
                            st.write("---")
                else:
                    st.info("No elections found")
            else:
                st.error("Failed to load elections")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to API: {e}")

    with col2:
        st.subheader("Quick Actions")
        if st.button("🆕 Create New Election", use_container_width=True):
            st.session_state.show_create_election = True
        if st.button("👥 View All Nominations", use_container_width=True):
            st.session_state.active_tab = "Nominations"
        if st.button("📊 Generate Report", use_container_width=True):
            st.session_state.active_tab = "Reports"

# ==================== SETUP TAB ====================
with tab2:
    st.header("Election Setup")

    setup_tab1, setup_tab2, setup_tab3 = st.tabs(["Terms", "Positions", "Elections"])

    # TERMS SUBTAB
    with setup_tab1:
        st.subheader("Academic Terms")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.write("**Create New Term**")
            with st.form("create_term"):
                term_name = st.text_input("Term Name", placeholder="e.g., Fall 2024")
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")

                if st.form_submit_button("Create Term", use_container_width=True):
                    data = {
                        "name": term_name,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                    }
                    try:
                        response = requests.post(f"{API_BASE}/terms", json=data)
                        if response.status_code == 201:
                            st.success("Term created successfully!")
                            st.rerun()
                        else:
                            st.error(
                                f"Error: {response.json().get('error', 'Unknown error')}"
                            )
                    except:
                        st.error("Could not connect to API")

        with col2:
            st.write("**Existing Terms**")
            try:
                response = requests.get(f"{API_BASE}/terms")
                if response.status_code == 200:
                    terms = response.json()
                    for term in terms:
                        with st.container():
                            st.write(f"**{term['Name']}**")
                            st.write(f"{term['StartDate']} to {term['EndDate']}")
                            st.write("---")
                else:
                    st.error("Failed to load terms")
            except:
                st.error("Could not connect to API")

    # POSITIONS SUBTAB
    with setup_tab2:
        st.subheader("Officer Positions")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.write("**Create New Position**")
            with st.form("create_position"):
                position_title = st.text_input(
                    "Position Title", placeholder="e.g., President"
                )
                ballot_order = st.number_input("Ballot Order", min_value=1, step=1)

                if st.form_submit_button("Create Position", use_container_width=True):
                    data = {"title": position_title, "ballot_order": ballot_order}
                    try:
                        response = requests.post(f"{API_BASE}/positions", json=data)
                        if response.status_code == 201:
                            st.success("Position created successfully!")
                            st.rerun()
                        else:
                            st.error(
                                f"Error: {response.json().get('error', 'Unknown error')}"
                            )
                    except requests.exceptions.RequestException as e:
                        st.error(f"Could not connect to API: {e}")

        with col2:
            st.write("**Existing Positions**")
            try:
                response = requests.get(f"{API_BASE}/positions")
                if response.status_code == 200:
                    positions = response.json()
                    for pos in positions:
                        st.write(f"**{pos['Title']}** (Order: {pos['BallotOrder']})")
                else:
                    st.error("Failed to load positions")
            except:
                st.error("Could not connect to API")

    # ELECTIONS SUBTAB
    with setup_tab3:
        st.subheader("Create Election")

        with st.form("create_election"):
            col1, col2 = st.columns(2)

            with col1:
                # Get terms for dropdown
                try:
                    terms_response = requests.get(f"{API_BASE}/terms")
                    terms = (
                        terms_response.json()
                        if terms_response.status_code == 200
                        else []
                    )
                    term_options = {term["Name"]: term["ID"] for term in terms}
                    selected_term = st.selectbox(
                        "Term", options=list(term_options.keys())
                    )

                    election_date = st.date_input("Election Date")
                    nominate_by = st.date_input("Nomination Deadline")

                except:
                    st.error("Could not load terms")
                    selected_term = None

            with col2:
                # Get positions for multi-select
                try:
                    positions_response = requests.get(f"{API_BASE}/positions")
                    positions = (
                        positions_response.json()
                        if positions_response.status_code == 200
                        else []
                    )
                    position_options = {pos["Title"]: pos["ID"] for pos in positions}
                    selected_positions = st.multiselect(
                        "Positions", options=list(position_options.keys())
                    )
                except:
                    st.error("Could not load positions")
                    selected_positions = []

            if st.form_submit_button("Create Election", use_container_width=True):
                if selected_term and selected_positions:
                    data = {
                        "term_id": term_options[selected_term],
                        "positions": [
                            position_options[pos] for pos in selected_positions
                        ],
                        "date": election_date.strftime("%Y-%m-%d"),
                        "nominate_by": nominate_by.strftime("%Y-%m-%d"),
                    }
                    try:
                        response = requests.post(f"{API_BASE}/", json=data)
                        if response.status_code == 201:
                            st.success("Election created successfully!")
                            st.rerun()
                        else:
                            st.error(
                                f"Error: {response.json().get('error', 'Unknown error')}"
                            )
                    except:
                        st.error("Could not connect to API")
                else:
                    st.error("Please select term and positions")

# ==================== NOMINATIONS TAB ====================
with tab3:
    st.header("Nomination Management")

    nom_tab1, nom_tab2 = st.tabs(["Submit Nominations", "View Nominations"])

    # SUBMIT NOMINATIONS
    with nom_tab1:
        st.subheader("Submit New Nomination")

        with st.form("submit_nomination"):
            col1, col2, col3 = st.columns(3)

            with col1:
                nominator_id = st.number_input(
                    "Nominator Member ID", min_value=1, step=1
                )

            with col2:
                nominee_id = st.number_input("Nominee Member ID", min_value=1, step=1)

            with col3:
                # Get positions for dropdown
                try:
                    positions_response = requests.get(f"{API_BASE}/positions")
                    positions = (
                        positions_response.json()
                        if positions_response.status_code == 200
                        else []
                    )
                    position_options = {pos["Title"]: pos["ID"] for pos in positions}
                    selected_position = st.selectbox(
                        "Position", options=list(position_options.keys())
                    )
                except:
                    st.error("Could not load positions")
                    selected_position = None

            if st.form_submit_button("Submit Nomination", use_container_width=True):
                if selected_position:
                    data = {
                        "nominator": nominator_id,
                        "nominee": nominee_id,
                        "position": position_options[selected_position],
                    }
                    try:
                        response = requests.post(f"{API_BASE}/nominations", json=data)
                        if response.status_code == 201:
                            st.success("Nomination submitted successfully!")
                            st.rerun()
                        else:
                            st.error(
                                f"Error: {response.json().get('error', 'Unknown error')}"
                            )
                    except:
                        st.error("Could not connect to API")

    # VIEW NOMINATIONS
    with nom_tab2:
        st.subheader("View Nominations by Election")

        try:
            elections_response = requests.get(f"{API_BASE}/")
            elections = (
                elections_response.json()
                if elections_response.status_code == 200
                else []
            )

            if elections:
                election_options = {
                    f"{e['TermName']} - {e['Date']}": e["ID"] for e in elections
                }
                selected_election = st.selectbox(
                    "Select Election", options=list(election_options.keys())
                )

                if selected_election:
                    election_id = election_options[selected_election]

                    # Get nominations for selected election
                    noms_response = requests.get(
                        f"{API_BASE}/nominations/election/{election_id}"
                    )
                    if noms_response.status_code == 200:
                        nominations = noms_response.json()

                        if nominations:
                            for nom in nominations:
                                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                                with col1:
                                    st.write(f"**{nom['PositionTitle']}**")
                                with col2:
                                    st.write(f"Nominee: {nom['NomineeName']}")
                                with col3:
                                    st.write(f"Nominator: {nom['NominatorName']}")
                                with col4:
                                    status = nom["Accepted"]
                                    if status is None:
                                        st.write("🟡 Pending")
                                        if st.button(
                                            "Accept",
                                            key=f"accept_{nom['ID']}",
                                            use_container_width=True,
                                        ):
                                            accept_data = {"accepted": True}
                                            accept_response = requests.put(
                                                f"{API_BASE}/nominations/{nom['ID']}/accept",
                                                json=accept_data,
                                            )
                                            if accept_response.status_code == 200:
                                                st.rerun()
                                        if st.button(
                                            "Decline",
                                            key=f"decline_{nom['ID']}",
                                            use_container_width=True,
                                        ):
                                            decline_data = {"accepted": False}
                                            decline_response = requests.put(
                                                f"{API_BASE}/nominations/{nom['ID']}/accept",
                                                json=decline_data,
                                            )
                                            if decline_response.status_code == 200:
                                                st.rerun()
                                    elif status:
                                        st.write("✅ Accepted")
                                    else:
                                        st.write("❌ Declined")

                                st.write("---")
                        else:
                            st.info("No nominations found for this election")
            else:
                st.info("No elections found")
        except:
            st.error("Could not load nominations")

# ==================== BALLOTS & VOTING TAB ====================
with tab4:
    st.header("Ballot Management")

    ballot_tab1, ballot_tab2 = st.tabs(["Generate Ballots", "Monitor Voting"])

    # GENERATE BALLOTS
    with ballot_tab1:
        st.subheader("Generate Ballots for Election")

        try:
            elections_response = requests.get(f"{API_BASE}/")
            elections = (
                elections_response.json()
                if elections_response.status_code == 200
                else []
            )

            if elections:
                election_options = {
                    f"{e['TermName']} - {e['Date']}": e["ID"] for e in elections
                }
                selected_election = st.selectbox(
                    "Select Election",
                    options=list(election_options.keys()),
                    key="ballot_election",
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Generate Ballots", use_container_width=True, type="primary"
                    ):
                        election_id = election_options[selected_election]
                        try:
                            response = requests.post(
                                f"{API_BASE}/elections/{election_id}/generate-ballots"
                            )
                            if response.status_code == 201:
                                result = response.json()
                                st.success(
                                    f"Generated {len(result['ballots'])} ballots successfully!"
                                )
                                for ballot in result["ballots"]:
                                    st.write(
                                        f"- {ballot['position']}: {ballot['options_count']} candidates"
                                    )
                            else:
                                st.error(
                                    f"Error: {response.json().get('error', 'Unknown error')}"
                                )
                        except:
                            st.error("Could not connect to API")

                with col2:
                    st.info(
                        "This will create ballots for all positions with accepted nominations that don't already have winners."
                    )
        except:
            st.error("Could not load elections")

    # MONITOR VOTING
    with ballot_tab2:
        st.subheader("Voting Progress")

        member_id = st.number_input(
            "Enter Member ID to view their ballots",
            min_value=1,
            step=1,
            key="voting_member",
        )

        if st.button("View Member Ballots"):
            try:
                response = requests.get(f"{API_BASE}/ballots/member/{member_id}")
                if response.status_code == 200:
                    ballots = response.json()
                    if ballots:
                        for ballot in ballots:
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.write(f"**{ballot['PositionTitle']}**")
                            with col2:
                                st.write(f"Election: {ballot['ElectionDate']}")
                            with col3:
                                st.write(f"Term: {ballot['TermName']}")
                            with col4:
                                if ballot["HasVoted"]:
                                    st.write("✅ Voted")
                                else:
                                    st.write("⏳ Not Voted")
                    else:
                        st.info("No ballots found for this member")
                else:
                    st.error("Could not load ballots")
            except:
                st.error("Could not connect to API")

# ==================== RESULTS TAB ====================
with tab5:
    st.header("Election Results")

    result_tab1, result_tab2 = st.tabs(["View Results", "Declare Winners"])

    # VIEW RESULTS
    with result_tab1:
        st.subheader("Ballot Results")

        ballot_id = st.number_input(
            "Enter Ballot ID", min_value=1, step=1, key="results_ballot"
        )

        if st.button("View Results"):
            try:
                response = requests.get(f"{API_BASE}/ballots/{ballot_id}/results")
                if response.status_code == 200:
                    results = response.json()

                    st.write(f"**Total Votes: {results['total_votes']}**")
                    st.write("---")

                    for candidate in results["results"]:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{candidate['CandidateName']}**")
                        with col2:
                            st.write(f"Votes: {candidate['VoteCount']}")
                        with col3:
                            percentage = (
                                (candidate["VoteCount"] / results["total_votes"] * 100)
                                if results["total_votes"] > 0
                                else 0
                            )
                            st.write(f"{percentage:.1f}%")

                        # Progress bar
                        if results["total_votes"] > 0:
                            st.progress(candidate["VoteCount"] / results["total_votes"])
                        st.write("---")
                else:
                    st.error("Could not load results")
            except:
                st.error("Could not connect to API")

    # DECLARE WINNERS
    with result_tab2:
        st.subheader("Declare Election Winners")

        col1, col2 = st.columns(2)
        with col1:
            ballot_id_winner = st.number_input(
                "Ballot ID", min_value=1, step=1, key="winner_ballot"
            )
        with col2:
            winner_member_id = st.number_input(
                "Winner Member ID", min_value=1, step=1, key="winner_member"
            )

        if st.button("Declare Winner", type="primary"):
            data = {"member_id": winner_member_id}
            try:
                response = requests.post(
                    f"{API_BASE}/ballots/{ballot_id_winner}/declare-winner", json=data
                )
                if response.status_code == 201:
                    st.success("Winner declared successfully!")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except:
                st.error("Could not connect to API")

# ==================== REPORTS TAB ====================
with tab6:
    st.header("Election Reports")

    try:
        elections_response = requests.get(f"{API_BASE}/")
        elections = (
            elections_response.json() if elections_response.status_code == 200 else []
        )

        if elections:
            election_options = {
                f"{e['TermName']} - {e['Date']}": e["ID"] for e in elections
            }
            selected_election = st.selectbox(
                "Select Election for Report",
                options=list(election_options.keys()),
                key="report_election",
            )

            if selected_election:
                election_id = election_options[selected_election]

                # Get winners for this election
                winners_response = requests.get(
                    f"{API_BASE}/elections/{election_id}/winners"
                )
                if winners_response.status_code == 200:
                    winners = winners_response.json()

                    st.subheader("Election Winners")
                    if winners:
                        for winner in winners:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**{winner['PositionTitle']}**")
                            with col2:
                                st.write(f"{winner['WinnerName']}")
                    else:
                        st.info("No winners declared yet")

                # Get nomination statistics
                nominations_response = requests.get(
                    f"{API_BASE}/nominations/election/{election_id}"
                )
                if nominations_response.status_code == 200:
                    nominations = nominations_response.json()

                    st.subheader("Nomination Statistics")
                    total_nominations = len(nominations)
                    accepted_nominations = len(
                        [n for n in nominations if n["Accepted"] is True]
                    )
                    pending_nominations = len(
                        [n for n in nominations if n["Accepted"] is None]
                    )

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Nominations", total_nominations)
                    with col2:
                        st.metric("Accepted", accepted_nominations)
                    with col3:
                        st.metric("Pending", pending_nominations)
        else:
            st.info("No elections found")
    except:
        st.error("Could not load election data")
