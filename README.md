# 🎵 Atlantic South Korea Music Analytics

An interactive **Streamlit dashboard** for analyzing Atlantic South Korea Top 50 playlist data.

The project focuses on understanding **chart re-entry behavior, comeback momentum, momentum sustainability, content characteristics, and fandom engagement proxies** using playlist snapshot data.

---

## 📌 Project Overview

When songs leave a music chart and later return, their comeback can provide useful insights into audience engagement and market behavior.

This project analyzes transaction-level playlist snapshot data to identify:

* Songs that re-enter the chart
* Frequency of chart re-entries
* Momentum generated during comebacks
* Sustainability after a comeback
* Relationship between content attributes and comeback strength
* Fandom engagement intensity using behavioral proxies

---

## 🎯 Objectives

The main objectives of the project are:

1. Identify song exits and re-entries.
2. Measure the frequency and timing of chart re-entries.
3. Measure momentum spikes during comebacks.
4. Analyze how long songs remain after returning to the chart.
5. Study rank recovery and post-peak rank decay.
6. Compare comeback strength between singles and album tracks.
7. Analyze album size, song duration, and explicit content in relation to momentum.
8. Estimate fandom engagement intensity using chart behavior.

---

## 📂 Dataset

The dataset contains playlist snapshot information for the Atlantic South Korea Top 50.

### Dataset Fields

| Column            | Description                   |
| ----------------- | ----------------------------- |
| `date`            | Date of playlist snapshot     |
| `position`        | Playlist rank (1–50)          |
| `song`            | Song title                    |
| `artist`          | Artist(s)                     |
| `popularity`      | Popularity score              |
| `duration_ms`     | Song duration in milliseconds |
| `album_type`      | Single / Album                |
| `total_tracks`    | Number of tracks in album     |
| `is_explicit`     | Explicit content flag         |
| `album_cover_url` | Album artwork URL             |

---

## 🔬 Analytical Methodology

### 1. Data Validation & Preparation

The dataset is prepared by:

* Validating daily chart entries
* Ensuring valid 50-entry chart snapshots
* Normalizing song–artist identifiers
* Converting duration from milliseconds to minutes
* Validating popularity scores

### 2. Chart Re-Entry Detection

For each song:

* Identify chart exit dates
* Identify re-entry dates
* Count re-entries
* Measure gaps between chart appearances

### 3. Momentum Spike Measurement

For each entry or re-entry:

* Calculate popularity change rate
* Measure rank jump magnitude
* Identify peak rank after re-entry
* Calculate Momentum Spike Score

### 4. Momentum Sustainability Analysis

For comeback episodes:

* Measure post-comeback retention
* Measure rank decay after the peak
* Analyze stability and volatility

### 5. Content Attribute vs Momentum Analysis

The project compares:

* Single vs Album comeback strength
* Album size vs resurgence intensity
* Song duration vs momentum
* Explicit vs Clean content momentum

### 6. Fandom Engagement Proxy

Fandom engagement intensity is estimated using:

* Re-entry frequency
* Popularity spike behavior
* Rank recovery speed

The resulting metric is a **proxy score**, not direct fandom-engagement data.

---

## 📊 Key Performance Indicators

The dashboard includes the following KPIs:

| KPI                                | Description                                        |
| ---------------------------------- | -------------------------------------------------- |
| **Re-Entry Frequency**             | Indicator of repeated chart reactivation           |
| **Momentum Spike Score**           | Measures comeback intensity                        |
| **Post-Comeback Retention Days**   | Measures how long a comeback is sustained          |
| **Rank Recovery Speed**            | Measures the efficiency of rank recovery           |
| **Album Comeback Advantage Index** | Compares album and single comeback strength        |
| **Fandom Intensity Proxy Score**   | Estimates engagement intensity from chart behavior |

---

## 📊 Dashboard Pages

### 🏠 Dashboard

The main dashboard provides:

* KPI cards
* Dataset summary
* Data validation
* Top songs by momentum
* Top artists by fandom intensity
* Single vs Album comparison
* Explicit vs Clean comparison
* Song duration vs momentum
* Dataset preview

### 🔄 Chart Re-Entry

Analyzes:

* Chart exits
* Chart re-entries
* Re-entry frequency
* Time gaps
* Rank recovery
* Comeback behavior

### 🚀 Momentum Analysis

Analyzes:

* Popularity changes
* Rank jumps
* Momentum Spike Score
* Peak rank
* Comeback sustainability
* Rank decay

### ⭐ Fandom Intensity

Analyzes:

* Re-entry frequency
* Popularity spike behavior
* Rank recovery
* Fandom Intensity Proxy Score

### 💿 Content Analysis

Analyzes:

* Single vs Album
* Album size
* Song duration
* Explicit vs Clean content
* Content characteristics and momentum

---

## 🛠️ Technologies Used

* **Python**
* **Pandas**
* **NumPy**
* **Plotly**
* **Streamlit**

---

## 📁 Project Structure

```text
atlantic-south-korea-analytics/
│
├── home.py
├── utils.py
├── requirements.txt
│
├── data/
│   └── Atlantic_South_Korea.csv
│
└── pages/
    ├── 2_Chart_ReEntry.py
    ├── 3_Momentum_Analysis.py
    ├── 4_Fandom_Intensity.py
    └── 5_Content_Analysis.py
```

---

## ▶️ Run the Project Locally

Clone the repository and open the project folder.

Install the required libraries:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run home.py
```

The dashboard will open in your browser.

---

## 📈 Expected Outcome

The project provides a consolidated analytical view of Atlantic South Korea chart behavior and helps identify:

* Songs with repeated chart comebacks
* Strong comeback momentum
* Sustainable vs volatile comebacks
* Rank recovery patterns
* Content characteristics associated with resurgence
* Behavioral signals that can be used as a fandom engagement proxy

---

## 👩‍💻 Project

**Atlantic South Korea Music Analytics**

Built using Python, Pandas, Plotly and Streamlit.
