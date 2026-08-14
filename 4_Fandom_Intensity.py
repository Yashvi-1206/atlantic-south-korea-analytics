import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Fandom Intensity",
    page_icon="⭐",
    layout="wide"
)

# -----------------------------------
# Load Data
# -----------------------------------
df = load_data()
df = apply_filters(df)

st.title("⭐ Fandom Intensity Analysis")

st.markdown("""
Estimate fandom engagement using:

- Re-Entry Frequency
- Momentum Spike Score
- Rank Recovery Speed
- Fandom Intensity Proxy Score
""")

st.divider()

# ===================================
# Top Artists by Fandom Intensity
# ===================================

st.subheader("🏆 Top 15 Artists by Fandom Intensity")

artist = (
    df.groupby("artist")
    .agg(
        Fandom=("Fandom_Intensity", "mean")
    )
    .reset_index()
    .sort_values("Fandom", ascending=False)
    .head(15)
)

fig = px.bar(
    artist,
    x="Fandom",
    y="artist",
    orientation="h",
    color="Fandom",
    text_auto=".2f",
    title="Top Artists by Fandom Intensity"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Top Songs by Fandom Intensity
# ===================================

st.subheader("🎵 Top Songs by Fandom Intensity")

songs = (
    df.groupby("song")
    .agg(
        Fandom=("Fandom_Intensity", "mean")
    )
    .reset_index()
    .sort_values("Fandom", ascending=False)
    .head(15)
)

fig = px.bar(
    songs,
    x="Fandom",
    y="song",
    orientation="h",
    color="Fandom",
    text_auto=".2f",
    title="Top Songs by Fandom Intensity"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Re-Entry vs Fandom Intensity
# ===================================

st.subheader("🎯 Re-Entry vs Fandom Intensity")

bubble = (
    df.groupby("artist")
    .agg(
        ReEntry=("Re_Entry_Frequency", "mean"),
        Fandom=("Fandom_Intensity", "mean"),
        Momentum=("Momentum_Score", "mean")
    )
    .reset_index()
)

# Momentum can contain negative values.
# Plotly does not allow negative bubble sizes.
# Create a separate positive column only for bubble size.

bubble["Bubble_Size"] = bubble["Momentum"].abs() + 1

fig = px.scatter(
    bubble,
    x="ReEntry",
    y="Fandom",
    size="Bubble_Size",
    color="Momentum",
    hover_name="artist",
    title="Re-Entry Frequency vs Fandom Intensity"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Rank Recovery Speed
# ===================================

st.subheader("⚡ Rank Recovery Speed by Artist")

recovery = (
    df.groupby("artist")
    .agg(
        Recovery=("Rank_Recovery_Speed", "mean")
    )
    .reset_index()
    .sort_values("Recovery", ascending=False)
    .head(15)
)

fig = px.bar(
    recovery,
    x="Recovery",
    y="artist",
    orientation="h",
    color="Recovery",
    text_auto=".2f",
    title="Artists with Fastest Rank Recovery"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Momentum Distribution
# ===================================

st.subheader("📈 Momentum Distribution")

fig = px.histogram(
    df,
    x="Momentum_Score",
    nbins=30,
    title="Distribution of Momentum Scores"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Fandom Intensity Timeline
# ===================================

st.subheader("📊 Fandom Intensity Timeline")

song_list = sorted(
    df["song"].dropna().unique()
)

selected_song = st.selectbox(
    "Select Song",
    song_list
)

timeline = (
    df[df["song"] == selected_song]
    .sort_values("date")
)

fig = px.line(
    timeline,
    x="date",
    y="Fandom_Intensity",
    markers=True,
    title=f"Fandom Intensity - {selected_song}"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Artist Summary
# ===================================

st.subheader("📄 Artist Summary")

summary = (
    df.groupby("artist")
    .agg(
        Songs=("song", "nunique"),
        Avg_Fandom=("Fandom_Intensity", "mean"),
        Avg_Momentum=("Momentum_Score", "mean"),
        Avg_Recovery=("Rank_Recovery_Speed", "mean"),
        Avg_ReEntry=("Re_Entry_Frequency", "mean")
    )
    .reset_index()
)

summary["Avg_Fandom"] = summary["Avg_Fandom"].round(2)
summary["Avg_Momentum"] = summary["Avg_Momentum"].round(2)
summary["Avg_Recovery"] = summary["Avg_Recovery"].round(2)
summary["Avg_ReEntry"] = summary["Avg_ReEntry"].round(2)

st.dataframe(
    summary,
    use_container_width=True
)