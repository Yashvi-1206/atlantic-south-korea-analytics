import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters, show_kpis

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Atlantic South Korea Music Analytics",
    page_icon="🎵",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #F8F9FA;
}

h1 {
    color: #1DB954;
    text-align: center;
}

[data-testid="metric-container"] {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15);
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# LOAD DATA
# =====================================================

df = load_data()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🎵 Atlantic Dashboard")
st.sidebar.caption("South Korea Music Analytics")

df = apply_filters(df)


# =====================================================
# PAGE TITLE
# =====================================================

st.title("🎵 Atlantic South Korea Music Analytics Dashboard")

st.markdown("""
This dashboard analyzes the **Atlantic South Korea Top 50 playlist**
to understand chart re-entry behavior, comeback momentum,
fandom engagement, and content characteristics.
""")

st.divider()


# =====================================================
# KPI SECTION
# =====================================================

st.subheader("📊 Key Performance Indicators")

show_kpis(df)

st.divider()


# =====================================================
# DATASET SUMMARY
# =====================================================

st.subheader("📂 Dataset Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Records",
        len(df)
    )

with col2:
    st.metric(
        "Songs",
        df["song"].nunique()
    )

with col3:
    st.metric(
        "Artists",
        df["artist"].nunique()
    )

with col4:
    st.metric(
        "Average Daily Entries",
        round(
            df.groupby("date").size().mean(),
            1
        ) if not df.empty else 0
    )

st.divider()

# =====================================================
# DATA VALIDATION — 50 ENTRIES PER DAY
# =====================================================

st.subheader("✅ Data Validation")

valid_days = (
    df.groupby("date")
    .size()
)

valid_days_count = (
    (valid_days == 50).sum()
)

total_days = len(valid_days)

invalid_days_count = (
    (valid_days != 50).sum()
)

average_entries = (
    valid_days.mean()
    if not valid_days.empty
    else 0
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Valid Chart Days",
        valid_days_count
    )

with col2:
    st.metric(
        "Invalid Chart Days",
        invalid_days_count
    )

with col3:
    st.metric(
        "Average Entries / Day",
        round(average_entries, 1)
    )

if invalid_days_count == 0:

    st.success(
        "✅ Data validation passed: every analyzed day contains exactly 50 entries."
    )

else:

    st.warning(
        f"⚠️ {invalid_days_count} day(s) do not contain exactly 50 entries."
    )

st.divider()

# =====================================================
# CHART 1 — TOP SONGS BY MOMENTUM
# =====================================================

st.subheader("🚀 Top Songs by Momentum")

song_momentum = (
    df.groupby(["song", "artist"])
    .agg(
        Momentum=("Momentum_Spike_Score", "mean")
    )
    .reset_index()
    .sort_values(
        "Momentum",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    song_momentum,
    x="Momentum",
    y="song",
    color="artist",
    orientation="h",
    text_auto=".2f",
    title="Top 10 Songs by Momentum Spike Score"
)

fig.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


# =====================================================
# CHART 2 — TOP ARTISTS BY FANDOM INTENSITY
# =====================================================

st.subheader("⭐ Top Artists by Fandom Intensity")

artist_fandom = (
    df.groupby("artist")
    .agg(
        Fandom=("Fandom_Intensity_Proxy_Score", "mean")
    )
    .reset_index()
    .sort_values(
        "Fandom",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    artist_fandom,
    x="Fandom",
    y="artist",
    orientation="h",
    color="Fandom",
    text_auto=".2f",
    title="Top 10 Artists by Fandom Intensity Proxy"
)

fig.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


# =====================================================
# CHART 3 — SINGLE VS ALBUM
# =====================================================

st.subheader("💿 Single vs Album Comeback Strength")

album_comparison = (
    df[df["Re_Entry_Number"] > 0]
    .groupby("Album_Type_Clean")
    .agg(
        Momentum=("Momentum_Spike_Score", "mean")
    )
    .reset_index()
)

fig = px.bar(
    album_comparison,
    x="Album_Type_Clean",
    y="Momentum",
    color="Album_Type_Clean",
    text_auto=".2f",
    title="Average Comeback Momentum: Single vs Album"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


# =====================================================
# CHART 4 — EXPLICIT VS CLEAN
# =====================================================

st.subheader("🔞 Explicit vs Clean Content")

content_comparison = (
    df.groupby("Content_Type")
    .agg(
        Momentum=("Momentum_Spike_Score", "mean")
    )
    .reset_index()
)

fig = px.bar(
    content_comparison,
    x="Content_Type",
    y="Momentum",
    color="Content_Type",
    text_auto=".2f",
    title="Momentum Comparison: Explicit vs Clean"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


# =====================================================
# CHART 5 — SONG DURATION VS MOMENTUM
# =====================================================

st.subheader("⏱️ Song Duration vs Momentum")

duration_data = (
    df[
        [
            "song",
            "Duration_Minutes",
            "Momentum_Spike_Score"
        ]
    ]
    .dropna()
    .drop_duplicates("song")
)

fig = px.scatter(
    duration_data,
    x="Duration_Minutes",
    y="Momentum_Spike_Score",
    hover_name="song",
    title="Song Duration vs Momentum Spike Score",
    labels={
        "Duration_Minutes": "Duration (Minutes)",
        "Momentum_Spike_Score": "Momentum Spike Score"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


# =====================================================
# DATASET PREVIEW
# =====================================================

st.subheader("📄 Dataset Preview")

st.dataframe(
    df.head(10),
    use_container_width=True
)

st.divider()


# =====================================================
# ANALYSIS AREAS
# =====================================================

st.subheader("🔍 Analysis Areas")

col1, col2 = st.columns(2)

with col1:

    st.info("""
    **🔄 Chart Re-Entry Analysis**

    • Exit dates  
    • Re-entry dates  
    • Re-entry frequency  
    • Time gaps between re-entries  
    • Peak rank after re-entry
    """)

    st.info("""
    **🚀 Momentum Analysis**

    • Popularity change rate  
    • Rank jump magnitude  
    • Momentum Spike Score  
    • Post-comeback retention  
    • Rank recovery speed
    """)

with col2:

    st.info("""
    **⭐ Fandom Intensity Analysis**

    • Re-entry frequency  
    • Popularity spike sharpness  
    • Rank recovery speed  
    • Fandom Intensity Proxy Score
    """)

    st.info("""
    **💿 Content Analysis**

    • Single vs Album  
    • Album size  
    • Song duration  
    • Explicit vs Clean  
    • Album Comeback Advantage Index
    """)


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.success(
    "✅ Atlantic South Korea Music Analytics Dashboard Loaded Successfully!"
)