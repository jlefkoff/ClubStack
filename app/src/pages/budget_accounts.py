# pages/budget_accounts.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Budget Accounts", page_icon="🏦")
SideBarLinks()
st.header("Budget Accounts")

# ---- fetch accounts (your API uses /budget) ----
def fetch_accounts():
    try:
        r = requests.get("http://api:4000/budget", timeout=10)
        r.raise_for_status()
        data = r.json()
        return pd.DataFrame(data if isinstance(data, list) else [])
    except Exception as e:
        st.error(f"Failed to load accounts: {e}")
        return pd.DataFrame()

df = fetch_accounts()

def friendly(v): return "—" if v in (None, "", [], {}) else v

label_map = {
    "BudgetID": "Budget ID",
    "AuthorFirstName": "Author First Name",
    "AuthorLastName": "Author Last Name",
    "ApprovedByFirstName": "Approver First Name",
    "ApprovedByLastName": "Approver Last Name",
    "FiscalYear": "Fiscal Year",
    "Status": "Status",
}

# ---- table ----
if df.empty:
    st.info("No accounts found.")
else:
    display = df.rename(columns={k: v for k, v in label_map.items() if k in df.columns}).copy()
    for c in display.columns:
        display[c] = display[c].apply(friendly)

    order = [c for c in ["Budget ID", "Author First Name", "Author Last Name",
                         "Approver First Name", "Approver Last Name",
                         "Fiscal Year", "Status"] if c in display.columns]
    cols = order or list(display.columns)

    st.subheader("All Accounts")
    st.dataframe(display[cols], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Open an Account")

    can_switch = hasattr(st, "switch_page")
    # per-row open button
    for _, row in df.sort_values(["FiscalYear", "BudgetID"], ascending=[False, True]).iterrows():
        bid = int(row["BudgetID"])
        left, right = st.columns([6, 1.5])
        with left:
            st.write(f"**Account #{bid}** — FY {int(row['FiscalYear'])} • Status: {row.get('Status','—')}")
        with right:
            if st.button("Open", key=f"acct_open_{bid}", use_container_width=True):
                st.session_state["selected_account_id"] = bid
                if can_switch:
                    st.switch_page("pages/budget_accounts_id.py")
                else:
                    st.session_state["_acct_link_ready"] = True
        st.divider()

    if not can_switch and st.session_state.get("_acct_link_ready"):
        st.link_button("Go to Account Details", "budget_accounts_id")

# ---- create account ----
st.subheader("Create New Account")
with st.form("create_account_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        fiscal_year = st.number_input("Fiscal Year", min_value=2000, max_value=2100, step=1)
    with c2:
        author_first = st.text_input("Author First Name")
    with c3:
        author_last  = st.text_input("Author Last Name")
    status = st.selectbox("Status", ["DRAFT", "SUBMITTED", "PAST"])
    submitted = st.form_submit_button("Create")

if submitted:
    if not (fiscal_year and author_first.strip() and author_last.strip()):
        st.error("Please fill in all required fields.")
    else:
        try:
            payload = {
                "FiscalYear": int(fiscal_year),
                "AuthorFirstName": author_first.strip(),
                "AuthorLastName":  author_last.strip(),
                "Status": status,
            }
            r = requests.post("http://api:4000/budget", json=payload, timeout=10)
            r.raise_for_status()
            st.success("Account created.")
            st.experimental_rerun()
        except requests.HTTPError as e:
            msg = getattr(e.response, "text", "") or str(e)
            st.error(f"Failed to create account: {msg}")
        except Exception as e:
            st.error(f"Failed to create account: {e}")
