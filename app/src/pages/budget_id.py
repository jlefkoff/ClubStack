# pages/budget_id.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Budget Details", page_icon="📂")

# Sidebar nav
SideBarLinks()

st.header("Budget Details")

# Ensure we have a selected budget id
if "selected_budget_id" not in st.session_state:
    st.error("No budget selected. Go back to the budgets list.")
    st.stop()

budget_id = int(st.session_state["selected_budget_id"])

# --- Fetch budgets and locate this one ---
try:
    resp = requests.get("http://api:4000/budget", timeout=10)
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    st.error(f"Failed to load budget data: {e}")
    st.stop()

df = pd.DataFrame(data if isinstance(data, list) else [])
if df.empty or "BudgetID" not in df.columns:
    st.error("Budget data is empty or malformed.")
    st.stop()

row = df[df["BudgetID"] == budget_id]
if row.empty:
    st.error(f"Budget #{budget_id} not found.")
    st.stop()

budget = row.iloc[0].to_dict()

# --- Key label mapping for display ---
key_labels = {
    "BudgetID": "Budget ID",
    "FiscalYear": "Fiscal Year",
    "AuthorFirstName": "Author First Name",
    "AuthorLastName": "Author Last Name",
    "ApprovedByFirstName": "Approver First Name",
    "ApprovedByLastName": "Approver Last Name",
    "Status": "Status",
}

# Display budget info with nice labels
st.subheader(f"Budget #{budget_id}")
for key, value in budget.items():
    label = key_labels.get(key, key.replace("_", " ").title())
    st.write(f"**{label}:** {value if value not in [None, ''] else '—'}")

st.divider()
st.subheader("Actions")

# ---- Approve budget (PUT) ----
if budget.get("Status") != "APPROVED":
    if st.button("✅ Approve Budget", use_container_width=True):
        try:
            payload = {**budget, "Status": "APPROVED"}
            r = requests.put(f"http://api:4000/budget/{budget_id}", json=payload, timeout=10)
            r.raise_for_status()
            st.success("Budget approved.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to approve budget: {e}")
else:
    st.info("This budget is already APPROVED.")

# ---- Delete budget (DELETE) ----
with st.expander("Danger Zone – Delete Budget"):
    st.warning("Deleting will remove this budget permanently.")
    confirm = st.checkbox("I understand and want to delete this budget.")
    if st.button("🗑️ Delete Budget", disabled=not confirm, use_container_width=True):
        try:
            r = requests.delete(f"http://api:4000/budget/{budget_id}", timeout=10)
            r.raise_for_status()
            st.success(f"Budget #{budget_id} deleted.")
            st.session_state.pop("selected_budget_id", None)
        except Exception as e:
            st.error(f"Failed to delete budget: {e}")
