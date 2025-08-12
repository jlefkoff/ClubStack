# pages/budget_id_report.py
import streamlit as st
import requests
import pandas as pd
from datetime import date

st.set_page_config(page_title="Spending Report", page_icon="📊")
st.header("Spending Report")

API_BASE = "http://api:4000/budget"

# Nav
st.page_link("pages/budget_overview.py", label="← Back to Overview", icon="↩️")

# Resolve budget id (session first, then query param)
budget_id = st.session_state.get("budget_id")
if not budget_id:
    if hasattr(st, "query_params"):
        budget_id = st.query_params.get("id")
    else:
        q = st.experimental_get_query_params().get("id")
        budget_id = q[0] if isinstance(q, list) else q

if not budget_id:
    st.error("No budget selected. Open a budget from the overview to generate a report.")
    st.stop()

budget_id = str(budget_id)
st.caption(f"Budget ID: {budget_id}")

# --- (Optional) UI controls you might use in the future ---
# Keeping the form so your UI has a 'Create Spending Report' action.
# Backend currently ignores these; you can wire them up later if the API accepts filters.
st.subheader("Create Spending Report")
default_start = date(date.today().year, 1, 1)
default_end = date.today()
with st.form("report_form"):
    _ = st.date_input("Date Range (not used by API yet)", value=(default_start, default_end))
    _ = st.selectbox("Group By (not used by API yet)", ["none", "category", "month", "vendor", "account"], index=0)
    _ = st.checkbox("Include transaction details (not used by API yet)", value=False)
    run = st.form_submit_button("Create Spending Report")

if run:
    try:
        with st.spinner("Generating report..."):
            # ✅ Correct endpoint per your backend: GET /budget/<id>/report
            resp = requests.get(f"{API_BASE}/{budget_id}/report", timeout=20)
            resp.raise_for_status()
            data = resp.json()
    except requests.RequestException as e:
        st.error(f"Error creating report: {e}")
        st.stop()

    st.subheader("Report Results")

    # Try to support both the current stub and a future richer payload
    # Current stub example: {"budget_id": 1, "report": "Budget + active member analysis (stub)"}
    # Future spec example might include: BudgetInfo, SpendingBreakdown, ActiveMemberMetrics
    if isinstance(data, dict):
        # If we have a SpendingBreakdown list, render as a table with CSV download
        breakdown = data.get("SpendingBreakdown")
        if isinstance(breakdown, list):
            if len(breakdown) == 0:
                st.info("No spending breakdown available.")
            else:
                df = pd.DataFrame(breakdown)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download Spending Breakdown (CSV)",
                    df.to_csv(index=False).encode("utf-8"),
                    file_name=f"budget_{budget_id}_spending_breakdown.csv",
                    mime="text/csv",
                )

        # Show BudgetInfo if present
        if "BudgetInfo" in data and isinstance(data["BudgetInfo"], dict):
            st.markdown("**Budget Info**")
            st.json(data["BudgetInfo"])

        # Show ActiveMemberMetrics if present
        if "ActiveMemberMetrics" in data and isinstance(data["ActiveMemberMetrics"], dict):
            st.markdown("**Active Member Metrics**")
            st.json(data["ActiveMemberMetrics"])

        # Fallback: show whatever else the stub returns
        other_keys = set(data.keys()) - {"SpendingBreakdown", "BudgetInfo", "ActiveMemberMetrics"}
        if other_keys:
            st.markdown("**Raw Report Data**")
            st.json({k: data[k] for k in other_keys})
    else:
        # If API ever returns a list/root object, just display it
        if isinstance(data, list) and data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name=f"budget_{budget_id}_report.csv",
                mime="text/csv",
            )
        else:
            st.write(data)
