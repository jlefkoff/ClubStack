# pages/budget_overview.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
from datetime import date
import requests


# data from api
data = {}
data = requests.get("http://api:4000/budget").json()

logger = logging.getLogger(__name__)
data_frame = pd.DataFrame(data)


st.set_page_config(page_title="Budgets", page_icon="💰")
SideBarLinks()
st.header("💰 Budgets")



# ---------- Filters ----------
fc1, fc2, fc3 = st.columns([2, 2, 1])
with fc1:
    owners = ["All"] + (sorted(df["owner"].unique().tolist()) if not df.empty else [])
    owner_filter = st.selectbox("Owner", owners, index=0)
with fc2:
    statuses = ["All"] + (sorted(df["status"].unique().tolist()) if not df.empty else [])
    status_filter = st.selectbox("Status", statuses, index=0)
with fc3:
    st.caption("Create a new budget below ⤵")

if not df.empty:
    if owner_filter != "All":
        df = df[df["owner"] == owner_filter]
    if status_filter != "All":
        df = df[df["status"] == status_filter]

# ---------- Table ----------
# st.subheader("All Budgets")
# if df.empty:
#     st.info("No budgets to show yet. Create one below.")
# else:
#     show_cols = ["name", "owner", "start_date", "end_date", "cap_fmt", "spent_fmt", "remaining_fmt", "status"]
#     col_rename = {
#         "name": "Name", "owner": "Owner", "start_date": "Start", "end_date": "End",
#         "cap_fmt": "Cap", "spent_fmt": "Spent", "remaining_fmt": "Remaining", "status": "Status",
#     }
#     st.dataframe(
#         df[show_cols].rename(columns=col_rename),
#         use_container_width=True,
#         hide_index=True,
#     )

    st.divider()
    st.subheader("Utilization & Open")

    # Native switch_page if available
    can_switch = hasattr(st, "switch_page")

    for _, row in df.iterrows():
        left, right = st.columns([6, 2])
        with left:
            st.write(f"**{row['name']}** · {row['owner']} · {row['start_date']} → {row['end_date']}")
            pct = float(row["utilization"])
            st.progress(pct, text=f"{row['spent_fmt']} / {row['cap_fmt']} ({int(pct*100)}%)")
        with right:
            if st.button("Open", key=f"open_{row['id']}", use_container_width=True):
                st.session_state.selected_budget_id = int(row["id"])
                if can_switch:
                    # ✅ Directly navigate to the detail page file
                    st.switch_page("pages/budget_id.py")
                else:
                    # Fallback: show a link the user can click
                    st.session_state._show_open_link = True
        st.divider()

    # Fallback link if st.switch_page is not available
    if not hasattr(st, "switch_page") and st.session_state.get("_show_open_link"):
        st.link_button("Go to Budget Details", "budget_id")  # relies on default pages routing

# ---------- Create Budget ----------
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
    if not name:
        st.error("Please provide a budget name.")
    elif end < start:
        st.error("End date cannot be earlier than start date.")
    elif cap <= 0:
        st.error("Cap must be greater than $0.")
    else:
        new_id = (max(b["id"] for b in st.session_state.budgets) + 1) if st.session_state.budgets else 1
        st.session_state.budgets.append({
            "id": new_id, "name": name, "owner": owner or "unknown@neu.edu",
            "start_date": str(start), "end_date": str(end), "cap": float(cap),
            "spent": 0.0, "status": status,
        })
        st.success(f"Created budget '{name}'.")
        st.rerun()
