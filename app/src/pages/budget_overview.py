# pages/budget_overview.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Budget Overview", page_icon="💰")
SideBarLinks()

st.header("Budget Overview")

# ----- fetch budgets -----
def fetch_budgets():
    try:
        r = requests.get("http://api:4000/budget", timeout=10)
        r.raise_for_status()
        data = r.json()
        return pd.DataFrame(data if isinstance(data, list) else [])
    except Exception as e:
        st.error(f"Error fetching budgets: {e}")
        return pd.DataFrame()

df = fetch_budgets()
if df.empty:
    st.info("No budgets found.")
    st.stop()

# ----- friendly helpers -----
def friendly(v): return "—" if v in (None, "", [], {}) else v
def full_name(first, last):
    f, l = (first or "").strip(), (last or "").strip()
    return (f"{f} {l}".strip()) or "—"

# derived display fields
df = df.copy()
df["Author"] = df.apply(lambda r: full_name(r.get("AuthorFirstName"), r.get("AuthorLastName")), axis=1)
df["Approver"] = df.apply(lambda r: full_name(r.get("ApprovedByFirstName"), r.get("ApprovedByLastName")), axis=1)

# quick nav to accounts
nav = st.columns([1, 5])
with nav[0]:
    if hasattr(st, "switch_page"):
        if st.button("🏦 Budget Accounts", use_container_width=True):
            st.switch_page("pages/budget_accounts.py")
    else:
        st.link_button("🏦 Budget Accounts", "budget_accounts")

# tidy table
show = ["BudgetID", "FiscalYear", "Author", "Approver", "Status"]
pretty = df[show].rename(columns={
    "BudgetID": "Budget ID",
    "FiscalYear": "Fiscal Year",
    "Author": "Author",
    "Approver": "Approver",
    "Status": "Status",
}).applymap(friendly)

st.subheader("All Budgets")
st.dataframe(
    pretty.sort_values(["Fiscal Year", "Budget ID"], ascending=[False, True]),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("Open / Accounts")

can_switch = hasattr(st, "switch_page")

# per-row actions
for _, row in df.sort_values(["FiscalYear", "BudgetID"], ascending=[False, True]).iterrows():
    bid = int(row["BudgetID"])
    info, open_col, acct_col = st.columns([6, 1.5, 1.5])

    with info:
        st.write(
            f"**Budget #{bid}** — FY {int(row['FiscalYear'])} • "
            f"Author: {row['Author']} • Status: {row['Status']}"
        )

    with open_col:
        if st.button("Open", key=f"open_{bid}", use_container_width=True):
            st.session_state["selected_budget_id"] = bid
            if can_switch:
                st.switch_page("pages/budget_id.py")
            else:
                st.session_state["_open_link_ready"] = True

    with acct_col:
        if st.button("Accounts", key=f"acct_{bid}", use_container_width=True):
            if can_switch:
                st.switch_page("pages/budget_accounts.py")
            else:
                st.session_state["_acct_link_ready"] = True

    st.divider()

# fallbacks for very old Streamlit
if not can_switch:
    if st.session_state.get("_open_link_ready"):
        st.link_button("Go to Budget Details", "budget_id")
    if st.session_state.get("_acct_link_ready"):
        st.link_button("Go to Budget Accounts", "budget_accounts")
