import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Chart Re-Entry Analysis",
    page_icon="🔄",
    layout="wide"
)

# -----------------------------------
# Load Data
# -----------------------------------
df = load_data()
df = apply_filters(df)

st.title("🔄 Chart Re-Entry Analysis")
st.markdown("""
This page analyzes:

- Re-entry Frequency
- Days Between Entries
- Rank Recovery
- Timeline of Songs
""")

st.divider()

# ===================================
# Top Re-Entry Songs
# ===================================

st.subheader("🏆 Top Songs by Re-Entry Frequency")

reentry = (
    df.groupby(["song", "artist"])
    .agg(Re_Entry=("Re_Entry_Frequency", "max"))
    .reset_index()
    .sort_values("Re_Entry", ascending=False)
    .head(15)
)

fig = px.bar(
    reentry,
    x="Re_Entry",
    y="song",
    color="artist",
    orientation="h",
    text="Re_Entry"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Days Between Entries
# ===================================

st.subheader("📅 Days Between Chart Entries")

gap = (
    df.groupby("song")
    .agg(
        Avg_Days=("Days_Between_Entries", "mean")
    )
    .reset_index()
    .sort_values("Avg_Days", ascending=False)
    .head(15)
)

fig = px.bar(
    gap,
    x="Avg_Days",
    y="song",
    orientation="h",
    color="Avg_Days",
    text_auto=".1f"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Timeline
# ===================================

st.subheader("📈 Song Timeline")

selected_song = st.selectbox(
    "Select Song",
    sorted(df["song"].unique())
)

timeline = df[df["song"] == selected_song]

fig = px.line(
    timeline,
    x="date",
    y="position",
    markers=True,
    title=f"{selected_song} Chart Position"
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Rank Recovery
# ===================================

st.subheader("⚡ Rank Recovery Speed")

rank = (
    df.groupby("song")
    .agg(
        Recovery=("Rank_Recovery_Speed", "mean")
    )
    .reset_index()
    .sort_values("Recovery", ascending=False)
    .head(15)
)

fig = px.bar(
    rank,
    x="Recovery",
    y="song",
    orientation="h",
    color="Recovery",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Scatter Plot
# ===================================

st.subheader("🎯 Re-Entry vs Momentum")

scatter = (
    df.groupby("song")
    .agg(
        ReEntry=("Re_Entry_Frequency", "max"),
        Momentum=("Momentum_Score", "mean")
    )
    .reset_index()
)

# Create positive bubble sizes
scatter["Bubble_Size"] = scatter["Momentum"].abs() + 1

fig = px.scatter(
    scatter,
    x="ReEntry",
    y="Momentum",
    size="Bubble_Size",
    hover_name="song",
    color="Momentum",
    title="Re-Entry vs Momentum"
)

st.plotly_chart(fig, use_container_width=True)
st.divider()

# ===================================
# Detailed Table
# ===================================

st.subheader("📄 Re-Entry Details")

display = df[
    [
        "date",
        "song",
        "artist",
        "position",
        "Re_Entry_Frequency",
        "Days_Between_Entries",
        "Rank_Recovery_Speed"
    ]
]

st.dataframe(display, use_container_width=True)