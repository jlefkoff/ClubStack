# pages/budget_overview.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Budget Overview", page_icon="💰")
SideBarLinks()
st.header("Budget Overview")

# ---- one button to Accounts ----
if hasattr(st, "switch_page"):
    if st.button("🏦 Budget Accounts", use_container_width=False):
        st.switch_page("pages/budget_accounts.py")
else:
    st.link_button("🏦 Budget Accounts", "budget_accounts")

# ---- (optional) quick list of budgets, minimal) ----
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
else:
    def friendly(v): return "—" if v in (None, "", [], {}) else v
    def full_name(first, last):
        f, l = (first or "").strip(), (last or "").strip()
        return (f"{f} {l}".strip()) or "—"

    df = df.copy()
    df["Author"] = df.apply(lambda r: full_name(r.get("AuthorFirstName"), r.get("AuthorLastName")), axis=1)
    df["Approver"] = df.apply(lambda r: full_name(r.get("ApprovedByFirstName"), r.get("ApprovedByLastName")), axis=1)

    show = ["BudgetID", "FiscalYear", "Author", "Approver", "Status"]
    pretty = df[show].rename(columns={
        "BudgetID": "Budget ID",
        "FiscalYear": "Fiscal Year",
        "Author": "Author",
        "Approver": "Approver",
        "Status": "Status",
    }).applymap(friendly)

    st.subheader("All Budgets")
    st.dataframe(pretty.sort_values(["Fiscal Year", "Budget ID"], ascending=[False, True]),
                 use_container_width=True, hide_index=True)
