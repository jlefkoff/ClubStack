# pages/permissions_member_id.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Member Permissions", page_icon="🧾")
st.header("Member Permissions")

API_BASE = "http://api:4000/permissions"

st.divider()

# If you navigated here via another page and stored an ID:
prefill = st.session_state.get("member_id", 1)

member_id = st.number_input("Enter Member ID", min_value=1, step=1, format="%d", value=int(prefill))

if st.button("View Member's Permissions", type="primary"):
    try:
        with st.spinner(f"Loading permissions for member #{member_id}..."):
            resp = requests.get(f"{API_BASE}/{int(member_id)}", timeout=15)
            resp.raise_for_status()
            data = resp.json()
    except requests.RequestException as e:
        st.error(f"Error fetching member permissions: {e}")
    else:
        st.subheader(f"Permissions for Member #{st.session_state.get('first_name', 'Unknown')} (ID: {member_id})")

        if not data:
            st.info("This member has no permissions.")
        else:
            # If backend returns objects, show a table; if strings, list them
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                for p in data:
                    st.write("•", p)
