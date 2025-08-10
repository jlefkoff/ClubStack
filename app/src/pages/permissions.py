# pages/permissions.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd

SideBarLinks()
st.header("Permissions")

if st.session_state.get("role") not in {"Admin", "Officer"}:
    st.error("You don’t have access to manage permissions.")
    st.stop()

with st.spinner("Loading users…"):
    users, err = api.get("/permissions")
if err:
    st.error(f"Failed to load: {err}")
    st.stop()

df = pd.DataFrame(users)  # columns: user_id, name, email, role
q = st.text_input("Search by name or email")
if q:
    m = df["name"].str.contains(q, case=False) | df["email"].str.contains(q, case=False)
    df = df[m]

st.dataframe(df[["name", "email", "role"]], use_container_width=True)

st.subheader("Edit role")
col1, col2 = st.columns([2,1])
with col1:
    who = st.selectbox("User", users, format_func=lambda u: f"{u['name']} ({u['email']})")
with col2:
    new_role = st.selectbox("Role", ["Admin", "Officer", "Member"], index=["Admin","Officer","Member"].index(who["role"]))

if st.button("Update role"):
    _, err = api.put(f"/permissions/{who['user_id']}", json={"role": new_role})
    if err:
        st.error(f"Update failed: {err}")
    else:
        st.success("Role updated. Reloading…")
        st.rerun()
