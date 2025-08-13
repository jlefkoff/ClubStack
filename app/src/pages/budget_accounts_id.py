# pages/budget_accounts_id.py
import streamlit as st
import requests

st.set_page_config(page_title="Budget Account", page_icon="🧾")
st.header("Budget Account Details")

API_BASE = "http://api:4000/budget"

# Nav
st.page_link("pages/budget_overview.py", label="← Back to Budgets", icon="↩️")
st.page_link("pages/budget_accounts.py", label="← Back to Accounts", icon="↩️")

# --- Resolve budget/account IDs (session first, then query params) ---
budget_id = st.session_state.get("budget_id")
account_id = st.session_state.get("account_id")

if not budget_id or not account_id:
    if hasattr(st, "query_params"):
        q_budget = st.query_params.get("budget")
        q_account = st.query_params.get("account")
    else:
        qp = st.experimental_get_query_params()
        qb = qp.get("budget")
        qa = qp.get("account")
        q_budget = qb[0] if isinstance(qb, list) else qb
        q_account = qa[0] if isinstance(qa, list) else qa
    budget_id = budget_id or q_budget
    account_id = account_id or q_account

if not budget_id or not account_id:
    st.error(
        "Missing budget/account id. Open from the Accounts page or pass ?budget=<bid>&account=<aid>."
    )
    st.stop()

budget_id = str(budget_id)
account_id = str(account_id)

st.caption(f"Budget ID: {budget_id} • Account ID: {account_id}")

# --- GET: load budget and find the account in its Accounts list ---
account = None
try:
    with st.spinner(f"Loading Budget #{budget_id}..."):
        bresp = requests.get(f"{API_BASE}/{budget_id}", timeout=15)
        if bresp.status_code == 404:
            st.error(f"Budget {budget_id} not found.")
            st.stop()
        bresp.raise_for_status()
        bdata = bresp.json()
        for a in bdata.get("Accounts") or []:
            if str(a.get("ID")) == account_id:
                account = a
                break
except requests.RequestException as e:
    st.error(f"Error fetching budget/account: {e}")
    st.stop()

if not account:
    st.error(f"Account {account_id} not found in Budget {budget_id}.")
    st.stop()

# --- SHOW: Account details ---
st.subheader("Account")
st.write("**ID:**", account.get("ID", "—"))
st.write("**AcctCode:**", account.get("AcctCode", "—"))
st.write("**AcctTitle:**", account.get("AcctTitle", "—"))

st.divider()

# --- PUT: Update account details ---
st.subheader("Update Account")
with st.form("update_account_form"):
    new_code = st.text_input("Account Code", value=str(account.get("AcctCode") or ""))
    new_title = st.text_input(
        "Account Title", value=str(account.get("AcctTitle") or "")
    )
    do_update = st.form_submit_button("Save Changes")

if do_update:
    if not new_code.strip() or not new_title.strip():
        st.warning("Both Account Code and Account Title are required.")
    else:
        payload = {"AcctCode": new_code.strip(), "AcctTitle": new_title.strip()}
        attempts = [
            ("PUT", f"{API_BASE}/{budget_id}/accounts/{account_id}", {"json": payload}),
            (
                "PUT",
                "http://api:4000/accounts/" + account_id,
                {"json": {**payload, "Budget": int(budget_id)}},
            ),
        ]
        updated = False
        last_status = None
        last_body = None
        for method, url, kwargs in attempts:
            try:
                with st.spinner(f"Updating via {method} {url} ..."):
                    resp = requests.request(method, url, timeout=20, **kwargs)
                last_status = resp.status_code
                try:
                    last_body = resp.json()
                except Exception:
                    last_body = {"raw": resp.text[:1000]}
                if 200 <= resp.status_code < 300:
                    st.success("Account updated.")
                    st.json(last_body)
                    # Refresh page data
                    try:
                        st.rerun()
                    except Exception:
                        st.experimental_rerun()
                    updated = True
                    break
            except requests.RequestException as e:
                last_status = "request_error"
                last_body = str(e)
        if not updated:
            st.error("Update failed")
            st.write("Last response/status:")
            st.write(last_status)
            st.json(
                last_body
                if isinstance(last_body, dict)
                else {"message": str(last_body)}
            )

st.divider()

# --- DELETE: Delete account ---
st.subheader("Delete Account")
danger = st.checkbox("I understand this will permanently delete this account.")
if st.button("🗑️ Delete Account", disabled=not danger, use_container_width=True):
    attempts = [
        ("DELETE", f"{API_BASE}/{budget_id}/accounts/{account_id}", {}),
        ("DELETE", "http://api:4000/accounts/" + account_id, {}),
    ]
    deleted = False
    last_status = None
    last_body = None
    for method, url, kwargs in attempts:
        try:
            with st.spinner(f"Deleting via {method} {url} ..."):
                resp = requests.request(method, url, timeout=20, **kwargs)
            last_status = resp.status_code
            try:
                last_body = resp.json()
            except Exception:
                last_body = {"raw": resp.text[:1000]}
            if 200 <= resp.status_code < 300:
                st.success("Account deleted.")
                # Clear selected account and go back to accounts list
                if "account_id" in st.session_state:
                    del st.session_state["account_id"]
                try:
                    st.switch_page("pages/budget_accounts.py")
                except Exception:
                    st.page_link(
                        "pages/budget_accounts.py", label="Return to Accounts", icon="↩️"
                    )
                deleted = True
                break
        except requests.RequestException as e:
            last_status = "request_error"
            last_body = str(e)
    if not deleted:
        st.error("Delete failed")
        st.write("Last response/status:")
        st.write(last_status)
        st.json(
            last_body if isinstance(last_body, dict) else {"message": str(last_body)}
        )
