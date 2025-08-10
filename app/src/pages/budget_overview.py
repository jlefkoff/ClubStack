# pages/budget_overview.py
from modules.nav import SideBarLinks
import streamlit as st
import pandas as pd

SideBarLinks()
st.header("Budgets")

with st.spinner("Loading budgets…"):
    budgets, err = api.get("/budgets")
if err:
    st.error(f"Could not load budgets: {err}")
    st.stop()

df = pd.DataFrame(budgets)  # id, name, owner, start_date, end_date, cap, spent
df["remaining"] = df["cap"] - df["spent"]
df["utilization"] = (df["spent"] / df["cap"]).fillna(0.0).clip(0,1)

c1, c2, c3 = st.columns([2,2,1])
with c1:
    owner = st.selectbox("Owner", ["All"] + sorted(df["owner"].unique().tolist()))
with c2:
    status = st.selectbox("Status", ["All","Active","Closed"])
with c3:
    st.link_button("➕ Create Budget", "budget_create")

if owner != "All":
    df = df[df["owner"] == owner]
if status != "All":
    df = df[df["status"] == status]

st.dataframe(
    df[["name","owner","start_date","end_date","cap","spent","remaining"]],
    use_container_width=True
)

for _, row in df.iterrows():
    st.progress(row["utilization"], text=f"{row['name']}: ${row['spent']:.2f} / ${row['cap']:.2f}")
    st.link_button("Open", f"budget/{row['id']}")
    st.divider()

