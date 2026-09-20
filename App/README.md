# BusInsight Web Application

The **BusInsight Web Application** is an interactive, browser-based transit intelligence platform for Astana's urban bus network. Built with [Streamlit](https://streamlit.io/), the application operationalizes the completed data-cleaning, journey reconstruction, machine-learning models, SQL analytics, and exploratory data analysis (EDA) from Tasks 1–4 into a dual-purpose portfolio system:

1. **Passenger-Facing Journey Estimator:** Pre-journey travel-time estimation powered by gradient-boosted regression.
2. **Operator & Analyst Dashboard:** Corridor performance intelligence, directional asymmetry quantification, corridor segment variability, dwell dynamics, and hop-length travel-time analysis.

---

## 1. Quickstart & Launch Instructions

### Prerequisites
Ensure your Python environment has the project dependencies installed:
```bash
pip install streamlit scikit-learn pandas numpy joblib
```

### Launch the Application
From the project root (`C:\Project\001\BusInsight`):
```bash
streamlit run App/app.py
```
The application will automatically start and open in your default browser at `http://localhost:8501`.

---

## 2. Architecture & File Organization

The application follows a clean service-oriented, modular architecture:

```
App/
├── app.py                      # Application entry point, layout, and page routing
├── README.md                   # Application guide and architecture documentation
├── styles/
│   └── main.css                # Custom transit-themed CSS stylesheets
├── services/                   # Business logic and cached data access
│   ├── __init__.py
│   ├── metadata_service.py     # Network topology, stop sequences, and stop ID mapping
│   ├── model_service.py        # ML artifact loader and pre-journey feature inference
│   ├── baseline_service.py     # Historical segment-pair median lookup and fallback
│   └── analytics_service.py    # Cached loaders for Task 4 EDA summaries and Task 3 metrics
└── components/                 # Presentation views
    ├── __init__.py
    ├── passenger_view.py       # Passenger journey estimator UI
    ├── operator_view.py        # Operations & corridor analytics dashboard
    ├── model_view.py           # Model architecture, benchmark, and feature importance
    └── methodology_view.py     # Methodology governance, audit decisions, and limitations
```

---

## 3. Core Application Views

### 🧭 Passenger Journey Estimator (`passenger_view.py`)
- **Dependent Selectors:** Cascading dropdowns (Route $\to$ Direction $\to$ Boarding Stop $\to$ Downstream Destination Stop $\to$ Travel Date).
- **Segment 1 Exclusion:** Boarding stop selector enforces $\text{Segment} \ge 2$, strictly honoring the approved Task 2B terminal dispatch governance lock.
- **Downstream Constraint:** Destination selector only displays stops physically downstream of the chosen origin ($\text{destination\_segment} \ge \text{start\_segment}$).
- **Interactive Inference:** Calls the serialized `HistGradientBoostingRegressor` model artifact (`ML/best_model.joblib`) with 10 strictly pre-journey features (providing fast, lightweight local inference).
- **Empirical Baseline Comparison:** Displays the historical median travel time (`ML/baseline_lookup.csv`) and sample size for the exact OD segment pair.
- **Historical Error Context:** Displays test set Mean Absolute Error (MAE: 3.2 min / 189.5s) as aggregate historical model error rather than an individual prediction interval.
- **Honesty & Transparency Callout:** Prominently clarifies that predictions reflect historical models under normal operating conditions, without live GPS or real-time traffic inputs.

### 📊 Transit Operations Dashboard (`operator_view.py`)
- **Route Overview:** High-level network KPIs and comparative metrics across Routes 10, 12, and 46.
- **Directional Asymmetry:** Highlights structural imbalances between Outbound (Direction 1) and Inbound (Direction 2) corridors, notably Route 12's 3.5 min (20.0%) directional difference.
- **Segment Variability:** Direct filterable inventory of the **62 high-variability corridor segments** ($N \ge 500$, $\text{IQR} \ge 68\text{s}$) identified during Task 4.
- **Dwell Dynamics:** Empirical contrast between Terminal Dispatch (Segment 1: substantial layover buffering with median dwell 506–546s on outbound routes) and Standard Passenger Stops (Segments $\ge 2$: routine boarding/alighting with median dwell 22–27s).
- **Hop-Tier Trends & Day-of-Week:** Shows that journey duration increases with hop length in the observed data, along with operational stability across Monday–Sunday schedules.

### 🤖 ML Architecture & Evaluation (`model_view.py`)
- **Model Architecture:** Detailed specification of `HistGradientBoostingRegressor` trained with squared error loss (L2).
- **Validation Benchmark Table:** Chronological split comparison against Historical Median Baseline, Ridge Regression, and HistGradientBoosting (Absolute Error).
- **Out-of-Time Test Set Evaluation:** Out-of-sample performance on 2,281,911 observations:
  - Model MAE: **189.54s (3.16 min)** vs Baseline **202.48s (3.37 min)** (6.39% improvement).
  - Model RMSE: **332.22s (5.54 min)** vs Baseline **358.98s (5.98 min)** (7.45% improvement).
  - Model $R^2$: **0.9290** vs Baseline **0.9171**.
- **Permutation Feature Importance:** Interactive chart detailing feature impact (`segments_traversed` 81.59%, stop indices 14.16%, segment positions 2.64%, day-of-week 0.49%).

### 📖 Methodology & Governance (`methodology_view.py`)
- Comprehensive overview of project milestones (Tasks 1 through 5).
- Detailed documentation of the six foundational data governance principles.

---

## 4. Methodological Guardrails & Truth in Data

BusInsight enforces strict scientific guardrails throughout the user interface:
1. **Historical Predictive Scope:** The platform does **not** claim live GPS feeds, real-time bus tracking, or live congestion updates.
2. **Zero-Leakage Pre-Journey Inputs:** No post-journey telemetry, segment run times, actual dwell durations, or arrival timestamps are used in prediction.
3. **Observation Terminology:** Volume numbers ($N = 15.28\text{M}$) are explicitly identified as **journey observations** or **corridor observations**, never as individual passenger counts.
4. **Empirical Reporting:** Corridor variance is reported strictly as measured statistics without unsubstantiated causal claims regarding external traffic or driver behavior.
5. **Terminal Dispatch Isolation:** Layover buffering is treated as an operational dispatch mechanism and kept separate from passenger trip boarding.

---

## 5. Dataset & Attribution

BusInsight utilizes the open Astana bus operations dataset described in:

> Mansurova, A.; Mussina, A.; Aubakirov, S.; Nugumanova, A.; Yedilkhan, D. (2025).  
> *"From Raw GPS to GTFS: A Real-World Open Dataset for Bus Travel Time Prediction."*  
> *Data*, 10(8), 119.  
> - **Paper:** [https://doi.org/10.3390/data10080119](https://doi.org/10.3390/data10080119)  
> - **Dataset:** [https://doi.org/10.5281/zenodo.15769359](https://doi.org/10.5281/zenodo.15769359)  
> - **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)  
> - **Original GPS Data Provider:** INNOFORCE SOLUTIONS LLP (published with permission from the rights holder)  
> - **Independent Implementation Notice:** BusInsight is an independent portfolio and educational data engineering implementation. Neither the dataset authors, publication authors, nor INNOFORCE SOLUTIONS LLP are affiliated with, endorsed, or reviewed this project.

