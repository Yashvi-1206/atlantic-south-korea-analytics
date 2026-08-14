import streamlit as st
import pandas as pd
import numpy as np


# =========================================================
# LOAD + PROCESS DATA
# =========================================================

@st.cache_data
def load_data():

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------
    df = pd.read_csv("data/Atlantic_South_Korea.csv")

    # -----------------------------------------------------
    # Basic column validation
    # -----------------------------------------------------
    required_columns = [
        "date",
        "position",
        "song",
        "artist",
        "popularity",
        "duration_ms",
        "album_type",
        "total_tracks",
        "is_explicit",
        "album_cover_url"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        st.error(
            f"Missing columns in dataset: {missing_columns}"
        )
        st.stop()

    # -----------------------------------------------------
    # Data types
    # -----------------------------------------------------
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["position"] = pd.to_numeric(
        df["position"],
        errors="coerce"
    )

    df["popularity"] = pd.to_numeric(
        df["popularity"],
        errors="coerce"
    )

    df["duration_ms"] = pd.to_numeric(
        df["duration_ms"],
        errors="coerce"
    )

    df["total_tracks"] = pd.to_numeric(
        df["total_tracks"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # Remove rows without essential identifiers
    # -----------------------------------------------------
    df = df.dropna(
        subset=[
            "date",
            "song",
            "artist",
            "position"
        ]
    ).copy()

    # =====================================================
    # 1. NORMALIZE SONG + ARTIST IDENTIFIERS
    # =====================================================

    df["Song_Clean"] = (
        df["song"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )

    df["Artist_Clean"] = (
        df["artist"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Unique song-artist identifier
    df["Song_Artist_ID"] = (
        df["Song_Clean"] + " | " + df["Artist_Clean"]
    )

    # =====================================================
    # 2. DURATION CONVERSION
    # =====================================================

    df["Duration_Minutes"] = (
        df["duration_ms"] / 60000
    ).round(2)

    # =====================================================
    # 3. POPULARITY VALIDATION
    # =====================================================

    # Spotify popularity is expected to be between 0 and 100.
    df["Popularity_Valid"] = df["popularity"].between(
        0,
        100,
        inclusive="both"
    )

    # Invalid popularity values are excluded from
    # popularity-based calculations.
    df.loc[
        ~df["Popularity_Valid"],
        "popularity"
    ] = np.nan

    # =====================================================
    # DAILY CHART VALIDATION
    # =====================================================

    # Count chart entries for each date
    daily_counts = (
    df.groupby("date")
    .size()
    .rename("Daily_Entry_Count")
)

    df = df.merge(
    daily_counts,
    on="date",
    how="left"
)

# -----------------------------------------------------
# Keep exactly 50 chart entries per day
# -----------------------------------------------------
# The dataset should contain positions 1–50 for each
# valid playlist snapshot.

    df = df[
    df["Daily_Entry_Count"] == 50
].copy()

# Recalculate the validation flag after filtering
    df["Exactly_50_Entries"] = True
    # =====================================================
    # SORT DATA
    # =====================================================

    df = df.sort_values(
        ["Song_Artist_ID", "date"]
    ).reset_index(drop=True)

    # =====================================================
    # 5. DETECT ACTUAL CHART EXIT / RE-ENTRY
    # =====================================================

    # Previous chart date for the same song
    df["Previous_Chart_Date"] = (
        df.groupby("Song_Artist_ID")["date"]
        .shift(1)
    )

    # Days since previous appearance
    df["Days_Since_Previous_Entry"] = (
        df["date"] -
        df["Previous_Chart_Date"]
    ).dt.days
    
    # Compatibility name used by Chart Re-Entry page
    df["Days_Between_Entries"] = (
     df["Days_Since_Previous_Entry"]
)

    # A re-entry occurs when the song returns after
    # at least one missing calendar day.
    df["Is_ReEntry"] = (
        df["Days_Since_Previous_Entry"] > 1
    )

    # First appearance is NOT treated as a re-entry.
    df.loc[
        df["Previous_Chart_Date"].isna(),
        "Is_ReEntry"
    ] = False

    # Exit date = last chart date before a gap.
    df["Is_Previous_Entry_Before_Exit"] = (
        df["Days_Since_Previous_Entry"] > 1
    )

    # For each song, calculate its previous exit date.
    df["Exit_Date_Before_ReEntry"] = np.where(
        df["Is_ReEntry"],
        df["Previous_Chart_Date"],
        pd.NaT
    )

    df["Exit_Date_Before_ReEntry"] = pd.to_datetime(
        df["Exit_Date_Before_ReEntry"]
    )

    # =====================================================
    # 6. RE-ENTRY NUMBER
    # =====================================================

    df["Re_Entry_Number"] = (
        df.groupby("Song_Artist_ID")["Is_ReEntry"]
        .cumsum()
    )

    # Actual re-entry frequency for each song
    reentry_counts = (
        df.groupby("Song_Artist_ID")["Is_ReEntry"]
        .sum()
        .rename("Re_Entry_Frequency")
    )

    df = df.merge(
        reentry_counts,
        on="Song_Artist_ID",
        how="left"
    )

    df["Re_Entry_Frequency"] = (
        df["Re_Entry_Frequency"]
        .fillna(0)
        .astype(int)
    )

    # =====================================================
    # 7. POPULARITY CHANGE
    # =====================================================

    df["Previous_Popularity"] = (
        df.groupby("Song_Artist_ID")["popularity"]
        .shift(1)
    )

    df["Popularity_Change"] = (
        df["popularity"] -
        df["Previous_Popularity"]
    )

    # Popularity change rate per day
    days = df["Days_Since_Previous_Entry"]

    df["Popularity_Change_Rate"] = np.where(
        days > 0,
        df["Popularity_Change"] / days,
        np.nan
    )

    # =====================================================
    # 8. RANK JUMP MAGNITUDE
    # =====================================================

    df["Previous_Position"] = (
        df.groupby("Song_Artist_ID")["position"]
        .shift(1)
    )

    # Positive = improved rank
    # Example: 30 -> 10 = +20
    df["Rank_Change"] = (
        df["Previous_Position"] -
        df["position"]
    )

    df["Rank_Jump_Magnitude"] = (
        df["Rank_Change"].abs()
    )

    # =====================================================
    # 9. CREATE CHART EPISODES
    # =====================================================

    # Every re-entry starts a new chart episode.
    # The first appearance also starts episode 0.
    df["Chart_Episode"] = (
        df.groupby("Song_Artist_ID")["Is_ReEntry"]
        .cumsum()
    )

    # Unique episode ID
    df["Episode_ID"] = (
        df["Song_Artist_ID"].astype(str)
        + "_episode_"
        + df["Chart_Episode"].astype(str)
    )

    # =====================================================
    # 10. EPISODE-LEVEL METRICS
    # =====================================================

    episode_summary = (
        df.groupby("Episode_ID")
        .agg(
            Episode_Start=("date", "min"),
            Episode_End=("date", "max"),
            Peak_Rank=("position", "min"),
            Lowest_Rank=("position", "max"),
            Avg_Position=("position", "mean"),
            Rank_Volatility=("position", "std"),
            Avg_Popularity=("popularity", "mean")
        )
        .reset_index()
    )

    # Duration of episode
    episode_summary["Episode_Duration_Days"] = (
        episode_summary["Episode_End"] -
        episode_summary["Episode_Start"]
    ).dt.days + 1

    # Fill volatility for episodes containing one observation
    episode_summary["Rank_Volatility"] = (
        episode_summary["Rank_Volatility"]
        .fillna(0)
    )

    # =====================================================
    # 11. PEAK RANK AFTER RE-ENTRY
    # =====================================================

    df = df.merge(
        episode_summary[
            [
                "Episode_ID",
                "Peak_Rank",
                "Episode_Start",
                "Episode_End",
                "Episode_Duration_Days",
                "Rank_Volatility"
            ]
        ],
        on="Episode_ID",
        how="left"
    )

    # Only comeback episodes need comeback-specific
    # peak rank values.
    df["Peak_Rank_After_ReEntry"] = np.where(
        df["Re_Entry_Number"] > 0,
        df["Peak_Rank"],
        np.nan
    )

    # =====================================================
    # 12. POST-COMEBACK RETENTION DAYS
    # =====================================================

    df["Post_Comeback_Retention_Days"] = np.where(
        df["Re_Entry_Number"] > 0,
        df["Episode_Duration_Days"],
        np.nan
    )

    # Keep old column name used by dashboard pages
    df["Retention_Days"] = df[
        "Post_Comeback_Retention_Days"
    ]

    # =====================================================
    # 13. PEAK DATE
    # =====================================================

    peak_dates = (
        df[df["position"] == df["Peak_Rank"]]
        .groupby("Episode_ID")["date"]
        .min()
        .rename("Peak_Date")
    )

    df = df.merge(
        peak_dates,
        on="Episode_ID",
        how="left"
    )

    # =====================================================
    # 14. RANK DECAY SPEED AFTER PEAK
    # =====================================================

    df["Days_After_Peak"] = (
        df["date"] -
        df["Peak_Date"]
    ).dt.days

    # Rank gets numerically larger when it decays.
    df["Rank_Decay_From_Peak"] = (
        df["position"] -
        df["Peak_Rank"]
    )

    df["Rank_Decay_Speed_Post_Peak"] = np.where(
        df["Days_After_Peak"] > 0,
        df["Rank_Decay_From_Peak"] /
        df["Days_After_Peak"],
        0
    )

    # =====================================================
    # 15. STABILITY VS VOLATILITY
    # =====================================================

    df["Post_Comeback_Rank_Volatility"] = np.where(
        df["Re_Entry_Number"] > 0,
        df["Rank_Volatility"],
        np.nan
    )

    # Lower volatility = more stable comeback.
    # Stability score is bounded between 0 and 1.
    df["Comeback_Stability_Score"] = np.where(
        df["Post_Comeback_Rank_Volatility"].notna(),
        1 / (
            1 +
            df["Post_Comeback_Rank_Volatility"]
        ),
        np.nan
    )

    # =====================================================
    # 16. RANK RECOVERY SPEED
    # =====================================================

    df["Rank_Recovery_Speed"] = np.where(
        df["Days_Since_Previous_Entry"] > 0,
        df["Rank_Change"] /
        df["Days_Since_Previous_Entry"],
        0
    )

    # =====================================================
    # 17. MOMENTUM SPIKE SCORE
    # =====================================================

    # Popularity component
    popularity_component = (
        df["Popularity_Change_Rate"]
        .fillna(0)
    )

    # Rank component
    rank_component = (
        df["Rank_Change"]
        .fillna(0)
    )

    # Stronger comeback = stronger rank improvement
    # and stronger popularity growth.
    df["Momentum_Score"] = (
        popularity_component +
        rank_component
    )

    # More explicit name for methodology
    df["Momentum_Spike_Score"] = (
        df["Momentum_Score"]
    )

    # =====================================================
    # 18. SINGLE VS ALBUM COMEBACK STRENGTH
    # =====================================================

    df["Album_Type_Clean"] = (
        df["album_type"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    df["Is_Album"] = (
        df["Album_Type_Clean"] == "Album"
    )

    df["Is_Single"] = (
        df["Album_Type_Clean"] == "Single"
    )

    # =====================================================
    # 19. ALBUM SIZE VS RESURGENCE
    # =====================================================

    df["Album_Size"] = df["total_tracks"]

    df["Resurgence_Intensity"] = (
        df["Momentum_Spike_Score"]
    )

    # =====================================================
    # 20. EXPLICIT / CLEAN
    # =====================================================

    # Convert different possible representations to bool
    def convert_explicit(value):

        if pd.isna(value):
            return False

        if isinstance(value, bool):
            return value

        value = str(value).strip().lower()

        return value in [
            "true",
            "1",
            "yes",
            "explicit"
        ]

    df["is_explicit"] = (
        df["is_explicit"]
        .apply(convert_explicit)
    )

    df["Content_Type"] = np.where(
        df["is_explicit"],
        "Explicit",
        "Clean"
    )

    # =====================================================
    # 21. ALBUM COMEBACK ADVANTAGE INDEX
    # =====================================================

    # Compare average comeback momentum of Album tracks
    # with Single tracks.
    #
    # The value is created at the dataset level and then
    # attached to each row for dashboard use.

    comeback_rows = df[
        df["Re_Entry_Number"] > 0
    ].copy()

    if not comeback_rows.empty:

        album_momentum = comeback_rows.loc[
            comeback_rows["Is_Album"],
            "Momentum_Spike_Score"
        ].mean()

        single_momentum = comeback_rows.loc[
            comeback_rows["Is_Single"],
            "Momentum_Spike_Score"
        ].mean()

        if pd.notna(album_momentum) and pd.notna(single_momentum):

            df["Album_Comeback_Advantage_Index"] = (
                album_momentum -
                single_momentum
            )

        else:
            df["Album_Comeback_Advantage_Index"] = 0.0

    else:

        df["Album_Comeback_Advantage_Index"] = 0.0

    # Keep compatibility with previous page
    df["Album_Advantage"] = np.where(
        df["Is_Album"],
        df["Album_Comeback_Advantage_Index"],
        0
    )

    # =====================================================
    # 22. FANDOM INTENSITY PROXY SCORE
    # =====================================================

    # The documentation specifies:
    #
    # Re-entry frequency
    # Popularity spike sharpness
    # Rank recovery speed
    #
    # We standardize the three components so one metric
    # doesn't dominate simply because of scale.

    def safe_zscore(series):

        series = series.astype(float)

        mean = series.mean()
        std = series.std()

        if pd.isna(std) or std == 0:
            return pd.Series(
                0,
                index=series.index
            )

        return (series - mean) / std

    reentry_z = safe_zscore(
        df["Re_Entry_Frequency"]
    )

    spike_z = safe_zscore(
        df["Popularity_Change_Rate"].fillna(0)
    )

    recovery_z = safe_zscore(
        df["Rank_Recovery_Speed"].fillna(0)
    )

    df["Fandom_Intensity"] = (
        reentry_z +
        spike_z +
        recovery_z
    ).round(4)

    df["Fandom_Intensity_Proxy_Score"] = (
        df["Fandom_Intensity"]
    )

    # =====================================================
    # 23. FINAL CLEANUP
    # =====================================================

    # Replace infinite values
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # Sort by date/song
    df = df.sort_values(
        ["date", "position"]
    ).reset_index(drop=True)

    return df


# =========================================================
# SIDEBAR FILTERS
# =========================================================

def apply_filters(df):

    st.sidebar.header("🎛️ Filters")

    # -----------------------------------------
    # Artist
    # -----------------------------------------
    artists = sorted(
        df["artist"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_artists = st.sidebar.multiselect(
        "🎤 Artist",
        artists
    )

    if selected_artists:
        df = df[
            df["artist"].isin(selected_artists)
        ]

    # -----------------------------------------
    # Album Type
    # -----------------------------------------
    album_types = sorted(
        df["album_type"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_album_types = st.sidebar.multiselect(
        "💿 Album Type",
        album_types
    )

    if selected_album_types:
        df = df[
            df["album_type"].isin(
                selected_album_types
            )
        ]

    # -----------------------------------------
    # Explicit Content
    # -----------------------------------------
    explicit_choice = st.sidebar.selectbox(
        "🔞 Explicit Content",
        [
            "All",
            "Explicit",
            "Clean"
        ]
    )

    if explicit_choice == "Explicit":

        df = df[
            df["is_explicit"] == True
        ]

    elif explicit_choice == "Clean":

        df = df[
            df["is_explicit"] == False
        ]

    # -----------------------------------------
    # Date Range
    # -----------------------------------------
    min_date = df["date"].min()
    max_date = df["date"].max()

    if pd.notna(min_date) and pd.notna(max_date):

        selected_dates = st.sidebar.date_input(
            "📅 Date Range",
            value=(
                min_date.date(),
                max_date.date()
            ),
            min_value=min_date.date(),
            max_value=max_date.date()
        )

        if len(selected_dates) == 2:

            start_date = pd.Timestamp(
                selected_dates[0]
            )

            end_date = pd.Timestamp(
                selected_dates[1]
            )

            df = df[
                (df["date"] >= start_date) &
                (df["date"] <= end_date)
            ]

    return df


# =========================================================
# KPI DISPLAY
# =========================================================

def show_kpis(df):

    # -----------------------------------------
    # Re-entry frequency
    # -----------------------------------------
    total_reentries = int(
        df["Is_ReEntry"].sum()
    )

    # -----------------------------------------
    # Momentum
    # -----------------------------------------
    momentum = df[
        "Momentum_Spike_Score"
    ].dropna()

    avg_momentum = (
        round(momentum.mean(), 2)
        if not momentum.empty
        else 0
    )

    # -----------------------------------------
    # Retention
    # -----------------------------------------
    retention = df[
        "Post_Comeback_Retention_Days"
    ].dropna()

    avg_retention = (
        round(retention.mean(), 1)
        if not retention.empty
        else 0
    )

    # -----------------------------------------
    # Recovery speed
    # -----------------------------------------
    recovery = df[
        "Rank_Recovery_Speed"
    ].dropna()

    avg_recovery = (
        round(recovery.mean(), 2)
        if not recovery.empty
        else 0
    )

    # -----------------------------------------
    # Album advantage
    # -----------------------------------------
    album_advantage = df[
        "Album_Comeback_Advantage_Index"
    ].dropna()

    album_advantage_value = (
        round(
            album_advantage.mean(),
            2
        )
        if not album_advantage.empty
        else 0
    )

    # -----------------------------------------
    # Fandom intensity
    # -----------------------------------------
    fandom = df[
        "Fandom_Intensity_Proxy_Score"
    ].dropna()

    fandom_value = (
        round(
            fandom.mean(),
            2
        )
        if not fandom.empty
        else 0
    )

    # =====================================================
    # DISPLAY
    # =====================================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🔄 Re-Entry Frequency",
        total_reentries
    )

    c2.metric(
        "🚀 Momentum Spike Score",
        avg_momentum
    )

    c3.metric(
        "📅 Post-Comeback Retention Days",
        avg_retention
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "⚡ Rank Recovery Speed",
        avg_recovery
    )

    c5.metric(
        "💿 Album Comeback Advantage",
        album_advantage_value
    )

    c6.metric(
        "⭐ Fandom Intensity Proxy",
        fandom_value
    )
    