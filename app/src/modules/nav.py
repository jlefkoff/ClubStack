# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar
# of the app

import streamlit as st


# ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/About.py", label="About", icon="🧠")


# ------------------------ For member role ------------------------
def MemberHomeNav():
    st.sidebar.page_link("pages/Member_Home.py", label="Club Member Home", icon="👤")


def GearBrowseNav():
    st.sidebar.page_link("pages/Browse_Gear.py", label="Browse Gear", icon="🏕️")


def MerchBuyNav():
    st.sidebar.page_link("pages/Buy_Merch.py", label="Buy Merch", icon="💰")


def SubmitReimbursementNav():
    st.sidebar.page_link(
        "pages/Submit_Reimbursement.py", label="Submit Reimbursement", icon="🧾"
    )


def MyGearNav():
    st.sidebar.page_link("pages/My_Gear.py", label="My Gear", icon="⚙️")

def CommunicationsNav():
    st.sidebar.page_link("pages/Communications.py", label="Communications", icon="📬")


# ------------------------ For role of Treasurer -------------
def TreasurerBudgetOverview():
    st.sidebar.page_link("pages/Budget_Overview.py", label="Budget Overview", icon="💰")


def TreasurerReimbursementsNav():
    st.sidebar.page_link(
        "pages/Manage_Reimbursements.py", label="Reimbursement Overview", icon="🧾"
    )


# ------------------------ For role of VP ------------------------


def Permissions():
    st.sidebar.page_link(
        "pages/permissions_overview.py", label="Permissions", icon="🔐"
    )


# ------------------------ System Admin Role ------------------------
def AdminPageNav():
    st.sidebar.page_link("pages/Admin_Home.py", label="System Admin", icon="🖥️")


def AdminElectionsNav():
    st.sidebar.page_link("pages/Admin_Elections.py", label="Elections", icon="🗳️")


def ViewProfile():
    st.sidebar.page_link("pages/View_Profile.py", label="View Members")


# --------------------------------Links Function -------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/logo.svg", width=200)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:

        if st.session_state["role"] == "member":
            MemberHomeNav()
            MerchBuyNav()
            MyGearNav()
            GearBrowseNav()
            SubmitReimbursementNav()
            CommunicationsNav()

        if st.session_state["role"] == "treasurer":
            MemberHomeNav()
            MerchBuyNav()
            MyGearNav()
            GearBrowseNav()
            SubmitReimbursementNav()
            TreasurerReimbursementsNav()
            TreasurerBudgetOverview()
            CommunicationsNav()

        if st.session_state["role"] == "vp":
            MemberHomeNav()
            MerchBuyNav()
            MyGearNav()
            GearBrowseNav()
            SubmitReimbursementNav()
            CommunicationsNav()

        if st.session_state["role"] == "administrator":
            MemberHomeNav()
            MerchBuyNav()
            MyGearNav()
            GearBrowseNav()
            SubmitReimbursementNav()
            TreasurerReimbursementsNav()
            TreasurerBudgetOverview()
            AdminPageNav()
            Permissions()
            AdminElectionsNav()
            ViewProfile()
            CommunicationsNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
