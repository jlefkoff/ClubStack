# pages/budget_overview.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
from datetime import date

# --- NAV + HEADER ---
SideBarLinks()
st.header("Budgets")

# --- SESSION INITIALIZATION (no API; mock/persist in-session) ---
if "budgets" not in st.session_state:
    st.session_state.budgets = [
        {
            "id": 1,
            "name": "Fall Backpacking Trips",
            "owner": "outdoors@neu.edu",
            "start_date": "2025-09-01",
            "end_date":   "2025-12-15",
            "cap": 5000.0,
            "spent": 2700.0,
            "status": "Active",
        },
        {
            "id": 2,
            "name": "Winter Gear Refresh",
            "owner": "gear@neu.edu",
            "start_date": "2025-01-05",
            "end_date":   "2025-03-15",
            "cap": 3000.0,
            "spent": 3100.0,
            "status": "Closed",
        },
        {
            "id": 3,
            "name": "Spring Climbing Trips",
            "owner": "climbing@neu.edu",
            "start_date": "2025-03-01",
            "end_date":   "2025-05-20",
            "cap": 4200.0,
            "spent": 1950.0,
            "status": "Active",
        },
    ]

# Helper to materialize DataFrame with derived columns
def budgets_df():
    df = pd.DataFrame(st.session_state.budgets).copy()
    if df.empty:
        return df
    df["remaining"] = (df["cap"] - df["spent"]).round(2)
    # Avoid division by zero; utilization in [0, 1]
    df["utilization"] = (df["spent"] / df["cap"]).where(df["cap"] > 0, 0.0).clip(0, 1.0)
    # Nicely formatted numbers for the table
    df["cap_fmt"] = df["cap"].map(lambda x: f"${x:,.2f}")
    df["spent_fmt"] = df["spent"].map(lambda x: f"${x:,.2f}")
    df["remaining_fmt"] = df["remaining"].map(lambda x: f"${x:,.2f}")
    return df

df = budgets_df()

# --- FILTERS ---
with st.container():
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        owners = ["All"] + (sorted(df["owner"].unique().tolist()) if not df.empty else [])
        owner_filter = st.selectbox("Owner", owners, index=0)
    with c2:
        statuses = ["All"] + (sorted(df["status"].unique().tolist()) if not df.empty else [])
        status_filter = st.selectbox("Status", statuses, index=0)
    with c3:
        st.caption("Create a new budget below ⤵")

# Apply filters
if not df.empty:
    if owner_filter != "All":
        df = df[df["owner"] == owner_filter]
    if status_filter != "All":
        df = df[df["status"] == status_filter]

# --- TABLE ---
st.subheader("All Budgets")
if df.empty:
    st.info("No budgets to show yet. Create one below.")
else:
    show_cols = ["name", "owner", "start_date", "end_date", "cap_fmt", "spent_fmt", "remaining_fmt", "status"]
    col_rename = {
        "name": "Name",
        "owner": "Owner",
        "start_date": "Start",
        "end_date": "End",
        "cap_fmt": "Cap",
        "spent_fmt": "Spent",
        "remaining_fmt": "Remaining",
        "status": "Status",
    }
    st.dataframe(
        df[show_cols].rename(columns=col_rename),
        use_container_width=True,
        hide_index=True,
    )

    # Progress bars for quick visual of utilization
    st.divider()
    st.subheader("Utilization")
    for _, row in df.iterrows():
        pct = float(row["utilization"])
        st.progress(pct, text=f"{row['name']}: {row['spent_fmt']} / {row['cap_fmt']} ({int(pct*100)}%)")

# --- CREATE BUDGET (inline form; no API) ---
st.divider()
st.subheader("Create Budget")

with st.form("create_budget_form", clear_on_submit=True):
    name = st.text_input("Budget name", placeholder="e.g., Summer Canoeing Trips")
    owner = st.text_input("Owner (email or name)", value=st.session_state.get("user", {}).get("email", ""))
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Start date", value=date.today())
    with c2:
        end = st.date_input("End date", value=date.today())
    cap = st.number_input("Spending cap ($)", min_value=0.0, step=50.0)
    status = st.selectbox("Status", ["Active", "Planned", "Closed"], index=0)
    submitted = st.form_submit_button("Create")

if submitted:
    # basic validation
    if not name:
        st.error("Please provide a budget name.")
    elif end < start:
        st.error("End date cannot be earlier than start date.")
    elif cap <= 0:
        st.error("Cap must be greater than $0.")
    else:
        # Create a new in-session record
        new_id = (max(b["id"] for b in st.session_state.budgets) + 1) if st.session_state.budgets else 1
        st.session_state.budgets.append({
            "id": new_id,
            "name": name,
            "owner": owner or "unknown@neu.edu",
            "start_date": str(start),
            "end_date": str(end),
            "cap": float(cap),
            "spent": 0.0,
            "status": status,
        })
        st.success(f"Created budget '{name}'.")
        st.rerun()
