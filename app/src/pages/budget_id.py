# pages/budget_id.py
import streamlit as st
import requests

# Optional nav (ignore if you don't use it)
try:
    from modules.nav import SideBarLinks
    st.set_page_config(page_title="Budget Details", page_icon="📂")
    SideBarLinks()
except Exception:
    st.set_page_config(page_title="Budget Details", page_icon="📂")

st.header("Budget Details")

API_URL = "http://api:4000/budget"

# --- Back to overview link (static) ---
st.page_link("pages/budget_overview.py", label="← Back to Overview", icon="↩️")

# --- Resolve budget ID (query param first, then session) ---
qid = None
if hasattr(st, "query_params"):
    qid = st.query_params.get("id")
else:
    q = st.experimental_get_query_params().get("id")
    qid = q[0] if isinstance(q, list) else q

budget_id = qid or st.session_state.get("budget_id") or st.session_state.get("selected_account_id")
if not budget_id:
    st.error("No budget selected (missing ?id=... and no session_state id).")
    st.stop()

budget_id = str(budget_id)

# GET: budgets
budgets = []
try:
    r = requests.get(API_URL, timeout=15)
    r.raise_for_status()
    budgets = r.json() if isinstance(r.json(), list) else r.json().get("results", [])
except requests.RequestException as e:
    st.error(f"Error fetching budgets: {e}")

st.subheader("All Budgets")
if budgets:
    for b in budgets:
        bid = b.get("BudgetID")
        label = f"📄 Budget #{bid} • Fiscal Year {b.get('FiscalYear','')} • {b.get('Status','')} • Author First Name: {b.get('AuthorFirstName','')} • Author Last Name: {b.get('AuthorLastName','')}"
        if st.button(label, key=f"open_{bid}"):
            st.session_state["budget_id"] = bid
            st.switch_page("pages/budget_id.py")
else:
    st.info("No budgets found.")
# --- GET: fetch budget details ---
try:
    with st.spinner(f"Loading budget #{budget_id}..."):
        resp = requests.get(f"{API_URL}/{budget_id}", timeout=15)
        resp.raise_for_status()
        budget = resp.json()
except requests.RequestException as e:
    st.error(f"Error fetching budget: {e}")
    st.stop()

# --- Show details ---
st.subheader(f"Budget #{budget_id}")
c1, c2 = st.columns(2)
with c1:
    st.write("**Fiscal Year:**", b.get("FiscalYear", "—"))
    st.write("**Status:**", b.get("Status", "—"))
with c2:
    st.write("**Author First Name:**", b.get("AuthorFirstName"))
    st.write("**Author Last Name:**", b.get("AuthorLastName"))
    st.write("**Approved By:**",
             f"{b.get('ApprovedByFirstName','')} {b.get('ApprovedByLastName','')}")

st.divider()

# --- PUT: approve budget (update status) ---
if st.button("✅ Approve Budget", use_container_width=True):
    try:
        # If your API uses a dedicated approve route, switch to f"{API_URL}/{budget_id}/approve"
        put_resp = requests.put(f"{API_URL}/{budget_id}", json={"Status": "APPROVED"}, timeout=15)
        put_resp.raise_for_status()
        st.success("Budget approved.")
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()
    except requests.RequestException as e:
        st.error(f"Error approving budget: {e}")

st.divider()

# --- DELETE: delete budget ---
with st.expander("Danger Zone"):
    st.warning("This will permanently delete the budget.")
    confirm = st.checkbox("I understand and want to delete this budget.")
    if st.button("🗑️ Delete Budget", disabled=not confirm, use_container_width=True):
        try:
            del_resp = requests.delete(f"{API_URL}/{budget_id}", timeout=15)
            del_resp.raise_for_status()
            st.success("Budget deleted.")
            # Clear any saved id and go back to list
            for k in ("budget_id", "selected_account_id"):
                if k in st.session_state:
                    del st.session_state[k]
            if hasattr(st, "switch_page"):
                st.switch_page("pages/budget_overview.py")
            else:
                st.page_link("pages/budget_overview.py", label="Return to Overview", icon="↩️")
        except requests.RequestException as e:
            st.error(f"Error deleting budget: {e}")
