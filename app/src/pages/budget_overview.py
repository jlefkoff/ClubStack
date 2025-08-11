# pages/budget_overview.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import requests
import logging

st.set_page_config(page_title="Budgets", page_icon="💰")

# Sidebar navigation
SideBarLinks()

st.header("Browse Budgets")

logger = logging.getLogger(__name__)

# ---- Get data from API ----
try:
    resp = requests.get("http://api:4000/budget", timeout=10)
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    st.error(f"Failed to load budgets: {e}")
    st.stop()

# Make a DataFrame (empty-safe)
df = pd.DataFrame(data if isinstance(data, list) else [])

if df.empty:
    st.info("No budgets found.")
    st.stop()

# Helper to combine names, handling nulls
def _name(first, last):
    f = (first or "").strip()
    l = (last or "").strip()
    return (f"{f} {l}").strip() or "—"

# Create display columns
df["Author"] = df.apply(lambda r: _name(r.get("AuthorFirstName"), r.get("AuthorLastName")), axis=1)
df["Approved By"] = df.apply(lambda r: _name(r.get("ApprovedByFirstName"), r.get("ApprovedByLastName")), axis=1)

# Show a tidy table
show_cols = ["BudgetID", "FiscalYear", "Author", "Approved By", "Status"]
st.dataframe(
    df[show_cols].sort_values(["FiscalYear", "BudgetID"], ascending=[False, True]),
    hide_index=True,
    use_container_width=True,
)

st.divider()
st.subheader("Open a Budget")

# If your Streamlit supports native switch_page
can_switch = hasattr(st, "switch_page")

# Render an "Open" button per budget
for _, row in df.sort_values(["FiscalYear", "BudgetID"], ascending=[False, True]).iterrows():
    bid = int(row["BudgetID"])
    cols = st.columns([6, 1])
    with cols[0]:
        st.write(f"**Budget #{bid}** — FY {int(row['FiscalYear'])} • Author: {row['Author']} • Status: {row['Status']}")
    with cols[1]:
        if st.button("Open", key=f"open_{bid}", use_container_width=True):
            st.session_state["selected_budget_id"] = bid
            if can_switch:
                st.switch_page("pages/budget_id.py")
            else:
                # Fallback for older Streamlit: prompt a link
                st.session_state["_open_link_ready"] = True
    st.divider()

if not can_switch and st.session_state.get("_open_link_ready"):
    # This relies on the page existing in /pages and default routing
    st.link_button("Go to Budget Details", "budget_id")
