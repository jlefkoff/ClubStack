# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar
# of the app

import streamlit as st


# ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/40_About.py", label="About", icon="🧠")


# ------------------------ Examples for Role of pol_strat_advisor --------
def PolStratAdvHomeNav():
    st.sidebar.page_link("pages/00_Member_Home.py", label="Club Member Home", icon="👤")


def WorldBankVizNav():
    st.sidebar.page_link("pages/01_Browse_Gear.py", label="Browse Gear", icon="🏕️")


def MapDemoNav():
    st.sidebar.page_link("pages/02_Buy_Merch.py", label="Buy Merch", icon="💰")


def MyGearNav():
    st.sidebar.page_link("pages/My_Gear.py", label="My Gear", icon="⚙️")

# ------------------------ Examples for Role of usaid_worker -------------
def ApiTestNav():
    st.sidebar.page_link("pages/12_API_Test.py", label="Test the API", icon="🛜")


def PredictionNav():
    st.sidebar.page_link(
        "pages/11_Prediction.py", label="Regression Prediction", icon="📈"
    )


def ClassificationNav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Classification Demo", icon="🌺"
    )


def NgoDirectoryNav():
    st.sidebar.page_link("pages/14_NGO_Directory.py", label="NGO Directory", icon="📁")


def AddNgoNav():
    st.sidebar.page_link("pages/15_Add_NGO.py", label="Add New NGO", icon="➕")


# ------------------------ System Admin Role ------------------------
def AdminPageNav():
    st.sidebar.page_link(
        "pages/41_Events.py",
        # "pages/30_Admin_Home.py",
        label="System Admin",
        icon="🖥️")
    st.sidebar.page_link(
        "pages/41_Events.py",
        label="Event Management",
        icon="📅")


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
            PolStratAdvHomeNav()
            WorldBankVizNav()
            MapDemoNav()
            MyGearNav()

        if st.session_state["role"] == "treasurer":
            PolStratAdvHomeNav()
            WorldBankVizNav()
            MapDemoNav()

        if st.session_state["role"] == "vp":
            PredictionNav()
            ApiTestNav()
            ClassificationNav()
            NgoDirectoryNav()
            AddNgoNav()
            WorldBankVizNav()
            MapDemoNav()
            

        if st.session_state["role"] == "administrator":
            AdminPageNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
