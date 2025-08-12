# pages/permissions.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd
import requests
import logging

st.set_page_config(page_title="Permissions", page_icon="🔐")

# Sidebar nav
SideBarLinks()

st.header("Permissions")

logger = logging.getLogger(__name__)
API_BASE = "http://api:4000/permissions"

# -------------------- Helpers --------------------
def friendly(val):
    return "—" if val in (None, "", []) else val

@st.cache_data(show_spinner=False, ttl=30)
def fetch_permissions():
    try:
        r = requests.get(f"{API_BASE}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return pd.DataFrame(data if isinstance(data, list) else [])
    except Exception as e:
        logger.exception("Failed to fetch permissions")
        st.error(f"Could not load permissions: {e}")
        return pd.DataFrame()

def create_permission(title: str, page_access: str | None):
    payload = {"Title": title, "PageAccess": page_access or None}
    r = requests.post(f"{API_BASE}/permissions", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

@st.cache_data(show_spinner=False, ttl=30)
def fetch_member_permissions(member_id: int):
    # Try a couple of likely endpoints; keep whichever your API actually uses.
    # 1) /members/{id}/permissions
    try:
        r = requests.get(f"{API_BASE}/members/{member_id}/permissions", timeout=10)
        if r.status_code == 200:
            return pd.DataFrame(r.json() if isinstance(r.json(), list) else [])
    except Exception:
        pass
    # 2) /permissions?memberId={id}
    try:
        r = requests.get(f"{API_BASE}/permissions", params={"memberId": member_id}, timeout=10)
        if r.status_code == 200:
            return pd.DataFrame(r.json() if isinstance(r.json(), list) else [])
    except Exception:
        pass
    return pd.DataFrame()

# -------------------- Section: List all permissions --------------------
st.subheader("All Permissions")

perm_df = fetch_permissions()

if perm_df.empty:
    st.info("No permissions found.")
else:
    # tidy labels
    label_map = {
        "ID": "ID",
        "Title": "Title",
        "PageAccess": "Page Access",
    }
    display_df = perm_df.rename(columns=label_map).copy()
    # friendly display for nulls
    if "Page Access" in display_df.columns:
        display_df["Page Access"] = display_df["Page Access"].apply(friendly)

    st.dataframe(
        display_df[["ID", "Title", "Page Access"]],
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# -------------------- Section: Create a new permission --------------------
st.subheader("Create New Permission")

with st.form("create_permission_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 2])
    with col1:
        new_title = st.text_input("Title", placeholder="e.g., Trip Leader")
    with col2:
        page_access = st.text_input("Page Access (optional)", placeholder="e.g., /admin, /gear")
    submit_new = st.form_submit_button("Create")

if submit_new:
    if not new_title.strip():
        st.error("Please enter a title for the permission.")
    else:
        try:
            _ = create_permission(new_title.strip(), page_access.strip())
            st.success("Permission created.")
            # refresh the cached table
            fetch_permissions.clear()
            perm_df = fetch_permissions()
        except requests.HTTPError as e:
            st.error(f"Failed to create permission: {e.response.text or e}")
        except Exception as e:
            st.error(f"Failed to create permission: {e}")

st.divider()

# -------------------- Section: List a member's permissions --------------------
st.subheader("Member's Permissions")

member_id_input = st.text_input("Member ID", placeholder="Enter a numeric member ID")
if st.button("Lookup"):
    try:
        mid = int(member_id_input)
    except (TypeError, ValueError):
        st.error("Please enter a valid numeric Member ID.")
    else:
        mdf = fetch_member_permissions(mid)
        if mdf.empty:
            st.info("No permissions found for that member.")
        else:
            # Normalize common shapes. Expect either permission objects or a wrapper with Title/PageAccess.
            col_map = {
                "ID": "ID",
                "Title": "Title",
                "PageAccess": "Page Access",
                "PermissionID": "ID",  # in case API returns PermissionID
            }
            mdf = mdf.rename(columns={k: v for k, v in col_map.items() if k in mdf.columns}).copy()
            if "Page Access" in mdf.columns:
                mdf["Page Access"] = mdf["Page Access"].apply(friendly)
            show = [c for c in ["ID", "Title", "Page Access"] if c in mdf.columns]
            st.dataframe(mdf[show], use_container_width=True, hide_index=True)
