import streamlit as st
import requests

st.sidebar.page_link("Home.py", label="Home", icon="🏠")
st.title("💰 Budget Overview")

API_BASE = "http://api:4000/budget"

# GET: budgets
budgets = []
try:
    r = requests.get(API_BASE, timeout=15)
    r.raise_for_status()
    budgets = r.json() if isinstance(r.json(), list) else r.json().get("results", [])
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


st.markdown("---")

# POST: create
st.subheader("Create a New Budget Proposal")
with st.form("new_budget_form"):
    fy = st.text_input("Fiscal Year", placeholder="e.g., 2026")
    amt = st.number_input("Amount", min_value=0.00, step=0.01, format="%.2f")
    desc = st.text_area("Description")
    go = st.form_submit_button("Create Budget")
    if go:
        if not fy.strip():
            st.warning("Fiscal Year is required.")
        elif amt <= 0:
            st.warning("Amount must be greater than 0.")
        else:
            try:
                payload = {"FiscalYear": fy.strip(), "Amount": float(amt), "Description": desc.strip()}
                resp = requests.post(API_BASE, json=payload, timeout=15)
                if resp.ok:
                    st.success("Budget proposal created successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.status_code} — {resp.text[:400]}")
            except requests.RequestException as e:
                st.error(f"Error creating budget: {e}")
