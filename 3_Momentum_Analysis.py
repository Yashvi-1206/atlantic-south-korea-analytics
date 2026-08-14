
import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters

# ----------------------------------
# Page Configuration
# ----------------------------------
st.set_page_config(
    page_title="Momentum Analysis",
    page_icon="🚀",
    layout="wide"
)

# ----------------------------------
# Load Data
# ----------------------------------
df = load_data()
df = apply_filters(df)

st.title("🚀 Momentum Analysis")

st.markdown("""
Analyze comeback momentum using:

- Momentum Spike Score
- Popularity Change
- Rank Jump Magnitude
- Retention Days
- Rank Recovery Speed
""")

st.divider()

# ==================================
# Top Momentum Songs
# ==================================

st.subheader("🏆 Top 15 Momentum Songs")

momentum = (
    df.groupby(["song", "artist"])
    .agg(
        Momentum=("Momentum_Score", "mean")
    )
    .reset_index()
    .sort_values("Momentum", ascending=False)
    .head(15)
)

fig = px.bar(
    momentum,
    x="Momentum",
    y="song",
    color="artist",
    orientation="h",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================
# Popularity Change
# ==================================

st.subheader("⭐ Popularity Change")

pop = (
    df.groupby("song")
    .agg(
        Popularity_Change=("Popularity_Change", "mean")
    )
    .reset_index()
)

fig = px.histogram(
    pop,
    x="Popularity_Change",
    nbins=25
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================
# Rank Change
# ==================================

st.subheader("📈 Rank Change")

rank = (
    df.groupby("song")
    .agg(
        Rank_Change=("Rank_Change", "mean")
    )
    .reset_index()
    .sort_values("Rank_Change", ascending=False)
    .head(15)
)

fig = px.bar(
    rank,
    x="Rank_Change",
    y="song",
    orientation="h",
    color="Rank_Change",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================
# Retention Days
# ==================================

st.subheader("📅 Post-Comeback Retention")

retention = (
    df.groupby("song")
    .agg(
        Retention=("Retention_Days", "max")
    )
    .reset_index()
    .sort_values("Retention", ascending=False)
    .head(15)
)

fig = px.bar(
    retention,
    x="Retention",
    y="song",
    orientation="h",
    color="Retention",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================
# Recovery Speed vs Momentum
# ==================================

st.subheader("⚡ Recovery Speed vs Momentum")

scatter = (
    df.groupby("song")
    .agg(
        Recovery=("Rank_Recovery_Speed", "mean"),
        Momentum=("Momentum_Score", "mean")
    )
    .reset_index()
)

# IMPORTANT:
# Momentum can be negative.
# Plotly does not allow negative values for bubble size.
# Therefore we create a separate positive column.

scatter["Bubble_Size"] = scatter["Momentum"].abs() + 1

fig = px.scatter(
    scatter,
    x="Recovery",
    y="Momentum",
    size="Bubble_Size",
    hover_name="song",
    color="Momentum",
    title="Rank Recovery Speed vs Momentum"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================
# Momentum Timeline
# ==================================

st.subheader("📊 Song Momentum Timeline")

song_list = sorted(df["song"].dropna().unique())

selected_song = st.selectbox(
    "Select Song",
    song_list
)

timeline = df[df["song"] == selected_song].sort_values("date")

fig = px.line(
    timeline,
    x="date",
    y="Momentum_Score",
    markers=True,
    title=f"Momentum Timeline - {selected_song}"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================
# Momentum Details
# ==================================

st.subheader("📄 Momentum Details")

columns = [
    "date",
    "song",
    "artist",
    "position",
    "popularity",
    "Popularity_Change",
    "Rank_Change",
    "Momentum_Score",
    "Rank_Recovery_Speed",
    "Retention_Days"
]

# Only display columns that actually exist
available_columns = [
    col for col in columns
    if col in df.columns
]

st.dataframe(
    df[available_columns],
    use_container_width=True
)