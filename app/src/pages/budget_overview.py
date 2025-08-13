import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE = "http://api:4000/budget"

# GET: budgets
budgets = []
try:
    r = requests.get(API_BASE, timeout=15)
    r.raise_for_status()
    data = r.json()
    budgets = data if isinstance(data, list) else data.get("results", [])
except requests.RequestException as e:
    st.error(f"Error fetching budgets: {e}")

st.subheader("All Budgets")
if budgets:
    for b in budgets:
        bid = b.get("BudgetID")
        label = (
            f"📄 Budget #{bid} • Fiscal Year {b.get('FiscalYear','')} • "
            f"{b.get('Status','')} • Author First Name: {b.get('AuthorFirstName','')} • "
            f"Author Last Name: {b.get('AuthorLastName','')}"
        )

        if st.button(label, key=f"open_{bid}"):
            st.session_state["budget_id"] = bid
            st.switch_page("pages/budget_id.py")

        # Add spending report button
        if st.button("Spending Report", key=f"report_{bid}"):
            st.session_state["budget_id"] = bid
            st.switch_page("pages/budget_id_report.py")

        # 👉 New: View Accounts button (per budget)
        if st.button("View Accounts", key=f"acct_{bid}"):
            st.session_state["budget_id"] = bid
            st.switch_page("pages/budget_accounts.py")
else:
    st.info("No budgets found.")

st.markdown("---")

# POST: create (NOTE: your backend POST is a stub; it returns 201 but does not persist yet)
st.subheader("Create a New Budget Proposal")
with st.form("new_budget_form"):
    # API expects Author as a MEMBER ID (int), not names
    status = st.selectbox(
        "Status (optional)", ["", "SUBMITTED", "APPROVED", "PAST"], index=0
    )

    # integers with no decimals
    fy = st.number_input(
        "Fiscal Year", min_value=2000, max_value=2100, step=1, format="%d"
    )

    submitted = st.form_submit_button("Create Budget")
    cancel = st.form_submit_button("Cancel")

    if submitted:
        payload = {
            "FiscalYear": int(fy),
            "Author": st.session_state['member_id'],
        }
        if status:
            payload["Status"] = status

        try:
            resp = requests.post(f"{API_BASE}/", json=payload, timeout=15)
            # Show server response to confirm what happened
            try:
                body = resp.json()
            except Exception:
                body = {"raw": resp.text[:1000]}
            if 200 <= resp.status_code < 300:
                st.success(
                    "Request sent."
                )
                st.json(body)
            else:
                st.error(f"Error: {resp.status_code}")
                st.json(body)
        except requests.RequestException as e:
            st.error(f"Error creating budget: {e}")
