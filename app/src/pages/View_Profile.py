# ManageMembers.py
import os
import requests
import pandas as pd
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()
st.title("Manage Members")

API_BASE = os.getenv("API_BASE") or "http://web-api:4000"

# The logged-in user's info (actor)
actor_id = st.session_state.get("member_id")
if not actor_id:
    st.error("You must be logged in to access this page.")
    st.stop()

headers = {"X-Actor-ID": str(actor_id)}  # used if you add backend permission checks

# ---- Load all members
with st.spinner("Loading members..."):
    try:
        resp = requests.get(f"{API_BASE}/members", headers=headers, timeout=15)
        if resp.status_code == 403:
            st.error("You do not have permission to manage members.")
            st.stop()
        resp.raise_for_status()
        members = resp.json().get("members", [])
    except Exception as e:
        st.error(f"Failed to fetch members: {e}")
        st.stop()

if not members:
    st.info("No members found.")
    st.stop()

# ---- Filters
with st.expander("Filters", expanded=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        q = st.text_input("Search by name", placeholder="e.g., Ada Lovelace")
    with c2:
        grad_years = sorted(
            {m.get("GraduationYear") for m in members if m.get("GraduationYear")}
        )
        grad_filter = st.multiselect("Graduation Year", grad_years)
    with c3:
        student_type = st.selectbox(
            "Student Type", ["All", "Undergraduate", "Graduate"]
        )


def _matches(m):
    # text search on first/last/preferred
    if q:
        needle = q.lower().strip()
        hay = " ".join(
            [
                str(m.get("FirstName", "")),
                str(m.get("PreferredName", "")),
                str(m.get("LastName", "")),
            ]
        ).lower()
        if needle not in hay:
            return False
    # grad year filter
    if grad_filter:
        if m.get("GraduationYear") not in grad_filter:
            return False
    # student type filter
    if student_type != "All":
        is_grad = bool(m.get("IsGradStudent"))
        if student_type == "Graduate" and not is_grad:
            return False
        if student_type == "Undergraduate" and is_grad:
            return False
    return True


filtered = [m for m in members if _matches(m)]
st.caption(f"Showing {len(filtered)} of {len(members)} members")

# ---- Table
cols = [
    "ID",
    "FirstName",
    "PreferredName",
    "LastName",
    "GraduationYear",
    "IsGradStudent",
    "ActivationDate",
    "CarPlate",
    "CarState",
    "CarPassCount",
    "EmerContactName",
    "EmerContactPhone",
    "Allergies",
]
df = pd.DataFrame(filtered)[[c for c in cols if c in filtered[0].keys()]]
st.dataframe(df, use_container_width=True, hide_index=True)

# ---- Select a member to edit
labels = [
    f"{m['ID']} — {m.get('FirstName','')} {m.get('LastName','')}" for m in filtered
]
label_to_id = {labels[i]: filtered[i]["ID"] for i in range(len(filtered))}
selected_label = st.selectbox("Select a member to edit", labels)
selected_id = label_to_id[selected_label]

# ---- Load fresh single-member view (to avoid stale data)
try:
    one = requests.get(f"{API_BASE}/members/{selected_id}", headers=headers, timeout=10)
    one.raise_for_status()
    profile = one.json()["member"]
except Exception as e:
    st.error(f"Failed to load member {selected_id}: {e}")
    st.stop()

st.write("---")
st.subheader(f"Edit Member #{selected_id}")

with st.form("edit_member_form", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        first_name = st.text_input("First Name", value=profile.get("FirstName", ""))
        last_name = st.text_input("Last Name", value=profile.get("LastName", ""))
        preferred_name = st.text_input(
            "Preferred Name", value=profile.get("PreferredName") or ""
        )
        graduation_year = st.number_input(
            "Graduation Year",
            value=profile.get("GraduationYear") or 2025,
            min_value=1900,
            max_value=2100,
        )
        is_grad_student = st.checkbox(
            "Graduate Student", value=bool(profile.get("IsGradStudent"))
        )
    with c2:
        car_plate = st.text_input("Car Plate", value=profile.get("CarPlate") or "")
        car_state = st.text_input("Car State", value=profile.get("CarState") or "")
        car_pass_count = st.number_input(
            "Car Pass Count",
            value=profile.get("CarPassCount") or 0,
            min_value=0,
            step=1,
        )
        emer_contact_name = st.text_input(
            "Emergency Contact Name", value=profile.get("EmerContactName") or ""
        )
        emer_contact_phone = st.text_input(
            "Emergency Contact Phone", value=profile.get("EmerContactPhone") or ""
        )

    submitted = st.form_submit_button("Save Changes")
    if submitted:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "preferred_name": preferred_name or None,
            "graduation_year": int(graduation_year) if graduation_year else None,
            "is_grad_student": bool(is_grad_student),
            "car_plate": car_plate or None,
            "car_state": car_state or None,
            "car_pass_count": int(car_pass_count) if car_pass_count else None,
            "emer_contact_name": emer_contact_name,
            "emer_contact_phone": emer_contact_phone,
        }
        try:
            up = requests.put(
                f"{API_BASE}/members/{selected_id}",
                json=payload,
                headers=headers,
                timeout=15,
            )
            if up.status_code == 200:
                st.success("Member updated successfully.")
                st.rerun()
            elif up.status_code == 403:
                st.error("You do not have permission to update members.")
            else:
                st.error(f"Failed to update member (status {up.status_code}).")
        except Exception as e:
            st.error(f"Error updating member: {e}")

# Optional quick action
colA, colB = st.columns([1, 4])
with colA:
    if st.button("Renew / Activate"):
        try:
            act = requests.put(
                f"{API_BASE}/members/{selected_id}/activate",
                headers=headers,
                timeout=10,
            )
            if act.status_code == 200:
                st.success("Member activation date updated.")
                st.rerun()
            else:
                st.error(f"Failed to activate member (status {act.status_code}).")
        except Exception as e:
            st.error(f"Error: {e}")
