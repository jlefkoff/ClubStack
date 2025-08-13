from modules.nav import SideBarLinks
import streamlit as st
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

BASE_URL = "http://api:4000"

st.title("🗳️ Election Voting")
st.write("Cast your votes for upcoming elections")

# Get member ID from session
member_id = st.session_state.get("member_id")

if not member_id:
    st.error("Please log in to access voting.")
    st.stop()

# Fetch member's available ballots
try:
    ballots_response = requests.get(f"{BASE_URL}/elections/ballots/member/{member_id}")
    if ballots_response.status_code == 200:
        ballots = ballots_response.json()
    else:
        st.error("Could not load your ballots.")
        ballots = []
except Exception as e:
    st.error("Elections service unavailable.")
    ballots = []

if not ballots:
    st.info("No ballots are currently available for you.")
    st.stop()

# Separate voted and unvoted ballots
voted_ballots = [b for b in ballots if b["HasVoted"]]
unvoted_ballots = [b for b in ballots if not b["HasVoted"]]

# Create tabs for active and completed voting
tab1, tab2 = st.tabs(["🗳️ Active Ballots", "✅ Completed Votes"])

# ==================== ACTIVE BALLOTS TAB ====================
with tab1:
    if unvoted_ballots:
        st.subheader(f"You have {len(unvoted_ballots)} ballot(s) to complete")

        for ballot in unvoted_ballots:
            with st.container():
                st.write("---")
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"### 🏛️ {ballot['PositionTitle']}")
                    st.write(f"**Election:** {ballot['TermName']}")
                    st.write(f"**Date:** {ballot['ElectionDate']}")

                with col2:
                    st.write("**Status:** ⏳ Not Voted")

                    # Get ballot details and options for this ballot
                try:
                    ballot_response = requests.get(
                        f"{BASE_URL}/elections/ballots/{ballot['BallotID']}"
                    )
                    if ballot_response.status_code == 200:
                        ballot_data = ballot_response.json()
                        options = ballot_data.get("options", [])

                        if options:
                            st.write("**Candidates:**")

                            # Create voting form for this ballot
                            with st.form(f"vote_form_{ballot['BallotID']}"):
                                # Use selectbox for cleaner UI (remove radio buttons)
                                candidate_options = {
                                    f"{opt['CandidateName']}": opt["OptionID"]
                                    for opt in options
                                }
                                selected_candidate = st.selectbox(
                                    "Choose candidate:",
                                    options=[""] + list(candidate_options.keys()),
                                    key=f"select_{ballot['BallotID']}",
                                )

                                col_vote, col_info = st.columns([1, 2])

                                with col_vote:
                                    submit_vote = st.form_submit_button(
                                        "🗳️ Cast Vote",
                                        type="primary",
                                        use_container_width=True,
                                    )

                                with col_info:
                                    st.info("⚠️ Votes cannot be changed once submitted")

                                # Handle vote submission
                                if submit_vote:
                                    if selected_candidate and selected_candidate != "":
                                        selected_option_id = candidate_options[
                                            selected_candidate
                                        ]

                                        # Confirm vote
                                        if st.session_state.get(
                                            f"confirm_vote_{ballot['BallotID']}", False
                                        ):
                                            # Submit the vote
                                            vote_data = {
                                                "member_id": member_id,
                                                "ballot_id": ballot["BallotID"],
                                                "ballot_option_id": selected_option_id,
                                            }

                                            try:
                                                vote_response = requests.post(
                                                    f"{BASE_URL}/elections/votes",
                                                    json=vote_data,
                                                )

                                                if vote_response.status_code == 201:
                                                    st.success(
                                                        f"✅ Vote cast successfully for {ballot['PositionTitle']}!"
                                                    )
                                                    st.balloons()

                                                    # Clear confirmation state
                                                    del st.session_state[
                                                        f"confirm_vote_{ballot['BallotID']}"
                                                    ]

                                                    # Refresh page
                                                    st.rerun()
                                                else:
                                                    error_msg = (
                                                        vote_response.json().get(
                                                            "error", "Unknown error"
                                                        )
                                                    )
                                                    st.error(
                                                        f"Error casting vote: {error_msg}"
                                                    )
                                            except Exception as e:
                                                st.error(f"Could not submit vote: {e}")
                                        else:
                                            # Show confirmation
                                            st.warning(
                                                f"⚠️ Confirm your vote for **{selected_candidate}** in {ballot['PositionTitle']}"
                                            )
                                            st.session_state[
                                                f"confirm_vote_{ballot['BallotID']}"
                                            ] = True
                                            st.rerun()
                                    else:
                                        st.error(
                                            "Please select a candidate before voting."
                                        )
                        else:
                            st.warning("No candidates available for this position.")
                    else:
                        st.error("Could not load ballot details.")
                except Exception as e:
                    st.error(f"Error loading ballot details: {e}")
    else:
        st.info("🎉 You have completed all available ballots!")

        if voted_ballots:
            st.write("Check the 'Completed Votes' tab to review your submissions.")

# ==================== COMPLETED VOTES TAB ====================
with tab2:
    if voted_ballots:
        st.subheader(f"You have voted on {len(voted_ballots)} ballot(s)")

        for ballot in voted_ballots:
            with st.expander(f"✅ {ballot['PositionTitle']} - {ballot['TermName']}"):
                st.write(f"**Position:** {ballot['PositionTitle']}")
                st.write(f"**Election:** {ballot['TermName']}")
                st.write(f"**Date:** {ballot['ElectionDate']}")
                st.write("**Status:** ✅ Vote Submitted")

                # Optionally show vote confirmation (without revealing the actual vote)
                st.success("Your vote has been recorded and cannot be changed.")
    else:
        st.info("You haven't voted on any ballots yet.")

# ==================== ELECTION INFORMATION ====================
st.write("")
st.write("---")
st.subheader("📋 Election Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Voting Guidelines:**")
    st.write("• One vote per position")
    st.write("• Votes cannot be changed once submitted")
    st.write("• All votes are anonymous")
    st.write("• Voting deadlines are strictly enforced")

with col2:
    st.write("**Need Help?**")
    st.write("Contact an administrator if you:")
    st.write("• Cannot see expected ballots")
    st.write("• Encounter technical issues")
    st.write("• Have questions about candidates")

    if st.button("📞 Contact Admin", type="secondary"):
        st.info("Please reach out to your club administrators for assistance.")

# ==================== SUMMARY STATISTICS ====================
st.write("")
st.write("---")

# Show voting statistics
stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.metric("Total Ballots", len(ballots))

with stat_col2:
    st.metric("Completed", len(voted_ballots))

with stat_col3:
    st.metric("Remaining", len(unvoted_ballots))

# Auto-refresh option for active elections
if unvoted_ballots:
    st.write("")
    if st.button("🔄 Refresh Ballots", type="secondary"):
        st.rerun()
