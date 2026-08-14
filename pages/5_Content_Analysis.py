import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Content Analysis",
    page_icon="💿",
    layout="wide"
)

# -----------------------------------
# Load Data
# -----------------------------------
df = load_data()
df = apply_filters(df)

st.title("💿 Content Attribute vs Momentum Analysis")

st.markdown("""
Compare:

- Album vs Single
- Explicit vs Clean Songs
- Album Size
- Song Duration
- Momentum Score
""")

st.divider()

# ===================================
# Album vs Single Momentum
# ===================================

st.subheader("💿 Album vs Single Momentum Score")

album = (
    df.groupby("album_type")
      .agg(
          Avg_Momentum=("Momentum_Score","mean"),
          Avg_Fandom=("Fandom_Intensity","mean")
      )
      .reset_index()
)

fig = px.bar(
    album,
    x="album_type",
    y="Avg_Momentum",
    color="album_type",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Explicit vs Clean
# ===================================

st.subheader("🔞 Explicit vs Clean Songs")

explicit = (
    df.groupby("is_explicit")
      .agg(
          Avg_Momentum=("Momentum_Score","mean"),
          Avg_Popularity=("popularity","mean")
      )
      .reset_index()
)

explicit["is_explicit"] = explicit["is_explicit"].replace({
    True:"Explicit",
    False:"Clean"
})

fig = px.bar(
    explicit,
    x="is_explicit",
    y="Avg_Momentum",
    color="is_explicit",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Album Size
# ===================================

st.subheader("📀 Album Size vs Momentum")

fig = px.scatter(
    df,
    x="total_tracks",
    y="Momentum_Score",
    color="album_type",
    size="popularity",
    hover_data=["song","artist"]
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Song Duration
# ===================================

st.subheader("⏱ Song Duration vs Momentum")

fig = px.scatter(
    df,
    x="Duration_Minutes",
    y="Momentum_Score",
    color="album_type",
    size="popularity",
    hover_data=["song"]
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Album Advantage Index
# ===================================

st.subheader("🏆 Album Comeback Advantage")

advantage = (
    df.groupby("album_type")
      .agg(
          Album_Advantage=("Album_Advantage","mean"),
          Momentum=("Momentum_Score","mean"),
          Recovery=("Rank_Recovery_Speed","mean")
      )
      .reset_index()
)

fig = px.bar(
    advantage,
    x="album_type",
    y="Album_Advantage",
    color="album_type",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Album Type Distribution
# ===================================

st.subheader("📊 Album Type Distribution")

album_count = (
    df["album_type"]
      .value_counts()
      .reset_index()
)

album_count.columns = ["Album Type","Count"]

fig = px.pie(
    album_count,
    names="Album Type",
    values="Count",
    hole=0.45
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Duration Distribution
# ===================================

st.subheader("🎵 Song Duration Distribution")

fig = px.histogram(
    df,
    x="Duration_Minutes",
    color="album_type",
    nbins=25
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===================================
# Final Summary Table
# ===================================

st.subheader("📄 Content Summary")

summary = (
    df.groupby("album_type")
      .agg(
          Songs=("song","count"),
          Avg_Popularity=("popularity","mean"),
          Avg_Momentum=("Momentum_Score","mean"),
          Avg_Fandom=("Fandom_Intensity","mean"),
          Avg_Duration=("Duration_Minutes","mean")
      )
      .reset_index()
)

summary = summary.round(2)

st.dataframe(summary, use_container_width=True)