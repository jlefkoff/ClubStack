# pages/budget_id.py
import streamlit as st
import requests

# Optional nav
try:
    from modules.nav import SideBarLinks

    st.set_page_config(page_title="Budget Details", page_icon="📂")
    SideBarLinks()
except Exception:
    st.set_page_config(page_title="Budget Details", page_icon="📂")

st.header("Budget Details")

API_URL = "http://api:4000/budget"

# Back to overview link
st.page_link("pages/Budget_Overview.py", label="← Back to Overview", icon="↩️")

# --- Resolve budget ID (query param first, then session) ---
qid = None
if hasattr(st, "query_params"):
    qid = st.query_params.get("id")
else:
    q = st.experimental_get_query_params().get("id")
    qid = q[0] if isinstance(q, list) else q

budget_id = (
    qid
    or st.session_state.get("budget_id")
    or st.session_state.get("selected_account_id")
)
if not budget_id:
    st.error("No budget selected (missing ?id=... and no session_state id).")
    st.stop()
budget_id = str(budget_id)

# --- GET: fetch budget details (aligned to backend spec) ---
try:
    with st.spinner(f"Loading budget #{budget_id}..."):
        resp = requests.get(f"{API_URL}/{budget_id}", timeout=15)
        resp.raise_for_status()
        budget = resp.json()
except requests.RequestException as e:
    st.error(f"Error fetching budget: {e}")
    st.stop()

# Unpack nested objects safely
author = budget.get("Author") or {}
approver = budget.get("ApprovedBy") or None

# --- Show details ---
st.subheader(f"Budget #{budget_id}")
c1, c2 = st.columns(2)
with c1:
    st.write("**Fiscal Year:**", budget.get("FiscalYear", "—"))
    st.write("**Status:**", budget.get("Status", "—"))
with c2:
    st.write(
        "**Author:**",
        f"{author.get('FirstName','—')} {author.get('LastName','')}".strip(),
    )
    st.write(
        "**Approved By:**",
        (
            f"{approver.get('FirstName','—')} {approver.get('LastName','')}".strip()
            if approver
            else "—"
        ),
    )

# If the endpoint returns Accounts, show them
accounts = budget.get("Accounts") or []
if accounts:
    st.markdown("**Accounts**")
    for a in accounts:
        st.write(
            f"- `{a.get('AcctCode','')}` — {a.get('AcctTitle','')} (ID: {a.get('ID','')})"
        )

st.divider()

# --- PUT: approve budget (correct route + payload) ---
st.subheader("Approve Budget")

if st.button("✅ Approve Budget", use_container_width=True):
    try:
        put_resp = requests.put(
            f"{API_URL}/{budget_id}/approve",
            json={"ApprovedBy": st.session_state['member_id']},
            timeout=15,
        )
        if 200 <= put_resp.status_code < 300:
            st.success("Budget approved.")
            st.rerun()
        else:
            try:
                st.error(put_resp.json())
            except Exception:
                st.error(f"Error {put_resp.status_code}: {put_resp.text[:400]}")
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
            # Clear saved id and go back to list
            for k in ("budget_id", "selected_account_id"):
                if k in st.session_state:
                    del st.session_state[k]
            if hasattr(st, "switch_page"):
                st.switch_page("pages/Budget_Overview.py")
            else:
                st.page_link(
                    "pages/Budget_Overview.py", label="Return to Overview", icon="↩️"
                )
        except requests.RequestException as e:
            st.error(f"Error deleting budget: {e}")
