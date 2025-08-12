# pages/budget_accounts.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Budget Accounts", page_icon="🏦")
st.header("Budget Accounts")

API_BASE = "http://api:4000/budget"

# Back to overview
st.page_link("pages/budget_overview.py", label="← Back to Budgets", icon="↩️")

# --- Load budgets for selection (GET /budget) ---
budgets = []
try:
    r = requests.get(API_BASE, timeout=15)
    r.raise_for_status()
    data = r.json()
    budgets = data if isinstance(data, list) else data.get("results", [])
except requests.RequestException as e:
    st.error(f"Error fetching budgets: {e}")
    st.stop()

if not budgets:
    st.info("No budgets found.")
    st.stop()

# Prefer a pre-selected budget from session_state if you arrived via a button
initial_bid = st.session_state.get("budget_id")

# Build label -> id map
def budget_label(b):
    return f"Budget #{b.get('BudgetID')} • FY {b.get('FiscalYear','—')} • {b.get('Status','—')}"

label_to_id = {budget_label(b): b.get("BudgetID") for b in budgets}

# Pick default label if we have an initial id
default_index = 0
if initial_bid is not None:
    for i, (lbl, bid) in enumerate(label_to_id.items()):
        if str(bid) == str(initial_bid):
            default_index = i
            break

st.subheader("View Accounts by Budget")
selected_label = st.selectbox("Choose a budget", list(label_to_id.keys()), index=default_index)
selected_budget_id = str(label_to_id[selected_label])
st.caption(f"Selected Budget ID: {selected_budget_id}")

# --- Fetch accounts for selected budget (GET /budget/<id>) ---
accounts = []
try:
    with st.spinner(f"Loading accounts for budget #{selected_budget_id}..."):
        bresp = requests.get(f"{API_BASE}/{selected_budget_id}", timeout=15)
        bresp.raise_for_status()
        bdata = bresp.json()
        accounts = bdata.get("Accounts") or []
except requests.RequestException as e:
    st.error(f"Error fetching accounts: {e}")

# Show accounts table
st.markdown("**Accounts for selected budget**")
if accounts:
    df = pd.DataFrame(accounts)
    order = [c for c in ["ID", "AcctCode", "AcctTitle"] if c in df.columns]
    st.dataframe(df[order] if order else df, use_container_width=True, hide_index=True)

    # 👉 Added: per-account Open button
    st.markdown("**Open an Account**")
    for a in accounts:
        aid = a.get("ID")
        left, right = st.columns([6, 1.5])
        with left:
            st.write(f"{a.get('AcctTitle','—')} — `{a.get('AcctCode','—')}` (ID: {aid})")
        with right:
            if st.button("Open", key=f"acct_open_{aid}", use_container_width=True):
                st.session_state["account_id"] = aid
                st.session_state["budget_id"] = selected_budget_id
                st.switch_page("pages/budget_accounts_id.py")
else:
    st.info("No accounts on this budget.")

st.divider()

# --- Create a new account ---
st.subheader("Create a New Account on Selected Budget")

with st.form("create_account_form"):
    acct_code = st.text_input("Account Code", placeholder="e.g., GEAR001")
    acct_title = st.text_input("Account Title", placeholder="e.g., Equipment & Gear")
    create = st.form_submit_button("Create Account")

if create:
    if not acct_code.strip() or not acct_title.strip():
        st.warning("Please provide both Account Code and Account Title.")
    else:
        # Try two common backend patterns and surface results to help align with the API
        attempts = [
            ("POST", f"{API_BASE}/{selected_budget_id}/accounts", {"json": {"AcctCode": acct_code.strip(), "AcctTitle": acct_title.strip()}}),
            ("POST", "http://api:4000/accounts", {"json": {"Budget": int(selected_budget_id), "AcctCode": acct_code.strip(), "AcctTitle": acct_title.strip()}}),
        ]
        success = False
        last_status = None
        last_body = None

        for method, url, kwargs in attempts:
            try:
                with st.spinner(f"Creating account via {method} {url} ..."):
                    resp = requests.request(method, url, timeout=20, **kwargs)
                last_status = resp.status_code
                try:
                    last_body = resp.json()
                except Exception:
                    last_body = {"raw": resp.text[:1000]}

                if 200 <= resp.status_code < 300:
                    st.success("Account created.")
                    st.json(last_body)
                    st.rerun()
                    success = True
                    break
            except requests.RequestException as e:
                last_status = "request_error"
                last_body = str(e)

        if not success:
            st.error("Could not create account — backend route not found or rejected the request.")
            st.write("Last response/status:")
            st.write(last_status)
            st.json(last_body if isinstance(last_body, dict) else {"message": str(last_body)})
