# BusInsight — Astana Urban Transit Analytics & Predictive Prototype

**BusInsight** is an end-to-end data analytics and machine-learning prototype built on GPS-derived automated vehicle location (AVL) transit telemetry from the urban bus network in **Astana, Kazakhstan**. 

The platform translates **15.2 million stop-to-stop journey observations** across 3 trunk routes into actionable intelligence, serving two distinct personas:
1. **Riders (Passenger Journey Estimator):** Pre-journey travel-time estimation powered by gradient-boosted decision trees using strictly pre-journey features.
2. **Transit Planners (Operations Dashboard):** Empirical corridor intelligence covering directional travel-time asymmetry, segment variability, dwell dynamics, and hop-length scaling.

> [!NOTE]
> **Prototype Scope Notice:** BusInsight is a historical analytical and predictive prototype based on observed transit data (July 29 – September 21, 2024). It is **not** a live bus-tracking system and does not claim real-time GPS feeds, live vehicle positions, or traffic-aware dynamic ETAs.

---

## 1. Problem Statement & Product Concept

### The Problem
Public transit riders face journey-time uncertainty without knowing realistic travel-time distributions before boarding. Concurrently, municipal transit planners and dispatchers often lack granular, segment-by-segment empirical metrics to pinpoint where travel time fluctuates across corridors.

### The Product Concept
BusInsight bridges this gap through a dual-perspective architecture:
- **Passenger Persona:** Needs a reliable, pre-journey travel-time estimate before boarding, using only known trip parameters (route, direction, origin, destination, calendar date) without post-journey leakage.
- **Operator / Analyst Persona:** Needs empirical corridor intelligence (identifying high-variability segments, quantifying directional imbalances, separating terminal layovers from routine stop dwells).

---

## 2. Dataset & Data Engineering

The system analyzes automated vehicle location (AVL) tracking records combined with static GTFS specifications:
- **Corridors:** 3 high-volume Astana trunk routes:
  - **Route 10:** Express trunk (*Astana Railway Station – International Airport* via Mangilik El Ave).
  - **Route 12:** City trunk (*Astana Railway Station – International Airport* via Kabanbay Batyr Ave).
  - **Route 46:** Cross-city residential trunk (*Karasu – Comfort Town*).
- **Network Scope:** 2 directions, 201 unique physical stops, 300 physical corridor segments.
- **Volume:** 785,976 segment records across 19,769 trips and 55 operating dates, generating **15,277,204 stop-to-stop journey observations**.
- **Data Governance Guardrails:**
  - **Terminal Dispatch Isolation:** Segment 1 (initial dispatch from terminal) exhibits heavy layovers and buffer holding (median dwell: 506–546s on outbound routes). It is preserved for fleet analysis but strictly excluded as a passenger journey origin.
  - **Telemetry Anomaly Isolation:** September 3–4 experienced a severe cellular collection drop; retained in analytical logs but excluded from ML training partitions.
  - **Zero Data Leakage:** Target is `observed_journey_time_seconds`. Models use only 10 strictly pre-journey features.

---

## 3. SQL Analytics & Key Operational Findings

SQL queries run against a lightweight, view-backed DuckDB catalog (`SQL/businsight.duckdb`):
- **Directional Asymmetry:** Direction 2 (Inbound) exhibits longer median journey durations across all three routes (longer by 1.34 to 2.36 min). Specifically on Route 12, Direction 2 median journey duration is **21.97 minutes** versus **20.63 minutes** for Direction 1 (Outbound) — an approximately **1.34 min (80.0s) differential**.
- **Corridor Segment Variability:** Identified **62 High-Variability Segments** ($N \ge 500, \text{IQR} \ge 68\text{s}$) across the 300 corridor segments where travel times fluctuate significantly.
- **Dwell Dynamics:** Standard passenger stops exhibit median dwell times of **22.0 to 27.0 seconds** (accounting for 20% to 23% of segment run time), whereas terminal dispatch (Segment 1) reflects layover holding.
- **Hop Scaling:** Journey duration increases monotonically with hop length, establishing hop count as the primary predictive baseline.

---

## 4. Machine Learning & Model Evaluation

### Benchmark: Historical Median Baseline
Before training machine learning models, an empirical baseline was established using training-set segment-pair historical medians with hop-count fallbacks. The baseline achieved strong performance ($R^2 = 0.9171$, MAE = 3.37 min).

### Selected Model: HistGradientBoostingRegressor (L2 Loss)
Evaluated across 2,281,911 out-of-time test observations (chronological split):

| Metric | Historical Baseline | HistGradientBoosting (L2) | Performance Delta |
| :--- | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | 202.48 s (3.37 min) | **189.54 s (3.16 min)** | **-12.94 s (-6.39%)** |
| **Root Mean Squared Error (RMSE)** | 358.98 s (5.98 min) | **332.22 s (5.54 min)** | **-26.76 s (-7.45%)** |
| **R² Score** | 0.9171 | **0.9290** | **+0.0119** |

### Product & Analytical Takeaway
The historical-median baseline was already very strong ($R^2 > 0.91$). The ML model produced a measurable but modest improvement ($6.39\%$ MAE reduction) by capturing non-linear spatial interactions and calendar patterns. A key product consideration is whether this modest accuracy gain justifies the operational overhead of managing an ML model lifecycle over a simple lookup table.

---

## 5. Web Application Overview

The browser-based application is built with **Streamlit** (`App/`):
- **🧭 Passenger Estimator:** Cascading selectors for Route $\to$ Direction $\to$ Boarding Stop $\to$ Downstream Destination Stop $\to$ Travel Date. Displays estimated duration, historical test set MAE (3.2 min), historical median comparison, and transparency notices.
- **📊 Operations Dashboard:** Route overview KPIs, directional asymmetry charts, 62 high-variability segment inventory, dwell comparisons, and hop trends.
- **🤖 ML Performance:** Model architecture specs, validation benchmark table, test evaluation metrics, and permutation feature importance.
- **📖 Methodology & Governance:** Full documentation of project milestones and data governance rules.

---

## 6. How to Launch

### Prerequisites
```bash
pip install streamlit scikit-learn pandas numpy joblib duckdb
```

### Run the Application
From the project root directory:
```bash
streamlit run App/app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 7. Project Structure

```text
BusInsight/
├── Original Data/    # Permanent reference GTFS static files and raw segment telemetry
├── Data/             # Cleaned analytical tables, ML-ready datasets, and EDA summaries
├── Scripts/          # Automated pipeline scripts (audit, cleaning, ML prep, training, EDA)
├── SQL/              # DuckDB database catalog and analytical SQL queries
├── ML/               # Serialized model artifact, baseline lookup tables, and evaluation metrics
├── Reports/          # Analytical Markdown reports, audit logs, and generated figures
├── App/              # Streamlit web application (app.py, components, services, styles)
└── README.md         # Project overview and portfolio documentation
```

---

## 8. Limitations & Scope

1. **Historical Telemetry:** Telemetry reflects July–September 2024 operating patterns and does not incorporate real-time GPS feeds or dynamic traffic conditions.
2. **No Ridership Counters:** Observation counts ($N = 15.28\text{M}$) represent mathematically generated stop-to-stop vehicle trajectory observations, not ticketed passenger counts.
3. **No Unmeasured Causal Claims:** High travel-time variability is reported empirically without asserting unmeasured causes such as traffic congestion or driver behavior.

---

## 9. Dataset & Attribution

BusInsight utilizes the open Astana bus operations dataset described in the scientific publication:

> Mansurova, A.; Mussina, A.; Aubakirov, S.; Nugumanova, A.; Yedilkhan, D. (2025).  
> *"From Raw GPS to GTFS: A Real-World Open Dataset for Bus Travel Time Prediction."*  
> *Data*, 10(8), 119.  
> - **Paper:** [https://doi.org/10.3390/data10080119](https://doi.org/10.3390/data10080119)  
> - **Dataset:** [https://doi.org/10.5281/zenodo.15769359](https://doi.org/10.5281/zenodo.15769359)  
> - **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

### Data Provider & Independent Implementation Notice
- **Original Data Provider:** The original raw GPS telemetry records were provided by **INNOFORCE SOLUTIONS LLP** and published with permission from the rights holder, as described in the source dataset publication.
- **Independent Project Notice:** BusInsight is an independent portfolio, data engineering, and machine learning implementation created for educational and demonstration purposes using this publicly released open dataset. Neither the dataset authors, the publication authors, nor INNOFORCE SOLUTIONS LLP created, reviewed, endorsed, or are affiliated with this project.

