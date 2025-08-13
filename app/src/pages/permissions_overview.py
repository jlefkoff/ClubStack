# pages/permissions_overview.py
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(page_title="Permissions Overview", page_icon="🔐")
st.header("Permissions Overview")

API_BASE = "http://api:4000/permissions"

SideBarLinks()

st.divider()

# -------- List all permissions (GET /permissions) --------
st.subheader("All Permissions")

permissions = []
try:
    r = requests.get(f"{API_BASE}/", timeout=15)
    r.raise_for_status()
    data = r.json()
    permissions = data if isinstance(data, list) else []
except requests.RequestException as e:
    st.error(f"Error fetching permissions: {e}")

if permissions:
    # If backend returns dict objects, show a table; otherwise show bullets
    if permissions and isinstance(permissions[0], dict):
        df = pd.DataFrame(permissions)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        for p in permissions:
            st.write("•", p)
else:
    st.info("No permissions found (backend may currently return an empty list).")

# --- Button to go to permissions_member_id page ---
if st.button("Go to Member Permissions Page"):
    st.switch_page("pages/permissions_member_id.py")

st.divider()

# -------- Create a new permission (POST /permissions) --------
st.subheader("Create New Permission")

with st.form("create_permission_form"):
    name = st.text_input("Permission Name", placeholder="e.g., VIEW_REPORTS")
    description = st.text_input(
        "Description (optional)", placeholder="e.g., Can view spending reports"
    )
    submit = st.form_submit_button("Create")

if submit:
    if not name.strip():
        st.warning("Permission Name is required.")
    else:
        payload = {"name": name.strip()}
        if description.strip():
            payload["description"] = description.strip()

        try:
            resp = requests.post(f"{API_BASE}/", json=payload, timeout=15)
            # Show the backend’s response (note: your backend is stubbed right now)
            try:
                body = resp.json()
            except Exception:
                body = {"raw": resp.text[:1000]}

            if 200 <= resp.status_code < 300:
                st.success(
                    "Create request sent. (Backend is a stub and may not persist yet.)"
                )
                st.json(body)
                st.rerun()
            else:
                st.error(f"Create failed: {resp.status_code}")
                st.json(body)
        except requests.RequestException as e:
            st.error(f"Error creating permission: {e}")
