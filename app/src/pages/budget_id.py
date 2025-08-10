# pages/budget_id.py
from modules.nav import SideBarLinks
import streamlit as st

st.set_page_config(page_title="Budget Details", page_icon="📂")
SideBarLinks()

# --- Get the selected budget id from session or query params ---
budget_id = st.session_state.get("selected_budget_id")

if budget_id is None:
    try:
        bid = st.query_params.get("id")  # Streamlit >= 1.33
    except AttributeError:
        bid = st.experimental_get_query_params().get("id", [None])[0]
    if bid:
        try:
            budget_id = int(bid)
        except ValueError:
            budget_id = None

if budget_id is None:
    st.error("No budget selected.")
    st.stop()

# --- Ensure budgets exist in session ---
if "budgets" not in st.session_state or not st.session_state.budgets:
    st.error("No budgets available in this session.")
    st.stop()

# --- Find the budget record ---
budget = next((b for b in st.session_state.budgets if b["id"] == int(budget_id)), None)
if not budget:
    st.error(f"Budget #{budget_id} not found.")
    st.stop()

# --- Header / summary ---
st.header(f"📂 {budget['name']}")
st.caption(f"Owner: {budget['owner']}  •  Period: {budget['start_date']} → {budget['end_date']}")

cap = float(budget.get("cap", 0.0))
spent = float(budget.get("spent", 0.0))
remaining = cap - spent
utilization = (spent / cap) if cap > 0 else 0.0
utilization = max(0.0, min(1.0, utilization))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Status", budget.get("status", "Unknown"))
c2.metric("Cap", f"${cap:,.2f}")
c3.metric("Spent", f"${spent:,.2f}")
c4.metric("Remaining", f"${remaining:,.2f}")
st.progress(utilization, text=f"{int(utilization*100)}% utilized")

st.divider()
st.subheader("Actions")

# --- Approve budget ---
if budget.get("status") != "Approved":
    if st.button("✅ Approve Budget", use_container_width=True):
        budget["status"] = "Approved"
        st.success("Budget approved.")
        st.rerun()
else:
    st.info("This budget is already Approved.")

# --- Delete budget ---
with st.expander("Danger Zone – Delete Budget"):
    st.warning("Deleting this budget will remove it from this session (no undo).")
    confirm = st.checkbox("I understand and want to delete this budget.")
    if st.button("🗑️ Delete Budget", disabled=not confirm, use_container_width=True):
        st.session_state.budgets = [b for b in st.session_state.budgets if b["id"] != int(budget_id)]
        st.session_state.selected_budget_id = None
        st.success(f"Budget #{budget_id} deleted.")
        st.stop()
