# pages/budget_account_id.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Account Details", page_icon="📂")
SideBarLinks()
st.header("Account Details")

# ---- get selected account id from session (preferred) or query param ----
account_id = st.session_state.get("selected_account_id")
if account_id is None:
    try:
        q = st.query_params.get("id")  # newer Streamlit
    except AttributeError:
        q = st.experimental_get_query_params().get("id", [None])[0]
    if q:
        try:
            account_id = int(q)
        except ValueError:
            account_id = None

if account_id is None:
    st.error("No account selected.")
    st.stop()

# ---- fetch all accounts, find this one (or swap to GET /budget/{id} if available) ----
try:
    r = requests.get("http://api:4000/budget", timeout=10)
    r.raise_for_status()
    df = pd.DataFrame(r.json() if isinstance(r.json(), list) else [])
except Exception as e:
    st.error(f"Failed to load account data: {e}")
    st.stop()

row = df[df["BudgetID"] == int(account_id)]
if row.empty:
    st.error(f"Account #{account_id} not found.")
    st.stop()

account = row.iloc[0].to_dict()

# ---- friendly labels ----
label_map = {
    "BudgetID": "Account ID",
    "FiscalYear": "Fiscal Year",
    "AuthorFirstName": "Author First Name",
    "AuthorLastName": "Author Last Name",
    "ApprovedByFirstName": "Approver First Name",
    "ApprovedByLastName": "Approver Last Name",
    "Status": "Status",
}
def labelize(k): return label_map.get(k, k.replace("_", " ").title())
def friendly(v): return "—" if v in (None, "", [], {}) else v

# ---- display current info ----
st.subheader(f"Account #{int(account['BudgetID'])}")
for k, v in account.items():
    st.write(f"**{labelize(k)}:** {friendly(v)}")

st.divider()
st.subheader("Edit Account")

# ---- edit form (PUT) ----
with st.form("edit_account_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        fiscal_year = st.number_input("Fiscal Year", value=int(account.get("FiscalYear", 2000)), min_value=2000, max_value=2100, step=1)
    with c2:
        author_first = st.text_input("Author First Name", value=str(account.get("AuthorFirstName") or ""))
    with c3:
        author_last  = st.text_input("Author Last Name",  value=str(account.get("AuthorLastName") or ""))

    status = st.selectbox(
        "Status",
        ["DRAFT", "SUBMITTED", "PAST", "APPROVED"],
        index=["DRAFT","SUBMITTED","PAST","APPROVED"].index(str(account.get("Status","DRAFT")))
        if str(account.get("Status")) in ["DRAFT","SUBMITTED","PAST","APPROVED"] else 0
    )

    save = st.form_submit_button("Save Changes")

if save:
    try:
        payload = {
            **account,
            "FiscalYear": int(fiscal_year),
            "AuthorFirstName": author_first.strip(),
            "AuthorLastName":  author_last.strip(),
            "Status": status,
        }
        u = requests.put(f"http://api:4000/budget/{int(account_id)}", json=payload, timeout=10)
        u.raise_for_status()
        st.success("Account updated.")
        st.experimental_rerun()
    except requests.HTTPError as e:
        msg = getattr(e.response, "text", "") or str(e)
        st.error(f"Failed to update account: {msg}")
    except Exception as e:
        st.error(f"Failed to update account: {e}")

st.divider()
st.subheader("Danger Zone")

# ---- delete (DELETE) ----
with st.expander("Delete this Account"):
    st.warning("This will permanently delete the account.")
    confirm = st.checkbox("I understand and want to delete this account.")
    if st.button("🗑️ Delete Account", disabled=not confirm, use_container_width=True):
        try:
            d = requests.delete(f"http://api:4000/budget/{int(account_id)}", timeout=10)
            d.raise_for_status()
            st.success(f"Account #{account_id} deleted.")
            st.session_state.pop("selected_account_id", None)
        except requests.HTTPError as e:
            msg = getattr(e.response, "text", "") or str(e)
            st.error(f"Failed to delete account: {msg}")
        except Exception as e:
            st.error(f"Failed to delete account: {e}")
