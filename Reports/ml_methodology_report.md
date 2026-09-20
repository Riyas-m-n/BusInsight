# BusInsight — ML Methodology & ML-Ready Dataset Specification (Task 2C)

**Task**: Task 2C — ML-Ready Dataset & Prediction Methodology  
**Execution Date**: 2026-09-20  
**Project Root**: `C:\Project\001\BusInsight`  
**Input Source**: `Data\journey_training_data.csv` (15,277,204 rows, 100% preserved)  
**Primary ML Output**: `Data\journey_ml_ready.csv` (14,477,686 rows, 1641.77 MB)  
**Status**: Validated & Locked  

---

## 1. Prediction Problem

In the passenger scenario:
> *"Given information available before a passenger begins a journey from stop A to stop B, estimate the journey travel time."*

The model serves as an empirical, data-backed journey-time estimator for transit riders planning trips across the Astana bus network. It provides realistic expectations without relying on unvalidated schedules or non-existent live GPS streams.

---

## 2. Target Definition

- **Target Column**: `observed_journey_time_seconds`
- **Unit**: Seconds (convertible to minutes via $\div 60$)
- **Meaning**: Total elapsed time observed between the bus departing the passenger's origin stop (`start_segment`) and arriving at the destination stop (`destination_segment`).
- **Calculation**: Deterministically derived from continuous segment run times and intermediate stop dwell times:
  $$\text{observed\_journey\_time\_seconds} = \sum_{k=i}^{j} \text{run\_time}_k + \sum_{k=i}^{j-1} \text{dwell\_time}_k$$
- **Target Value Properties**: Strictly non-negative ($y \ge 0$). In the eligible dataset, min travel time is positive (minimum single-segment run time), with median **1,437.0 seconds (23.95 mins)**.
- **Integrity Lock**: The observed target values are preserved in their true empirical form and are not arbitrarily transformed, clipped, or modified.

---

## 3. Prediction-Time Scenario & Operational Constraints

At query time, the passenger specifies:
1. **Route**: Route 10, 12, or 46
2. **Direction**: Outbound (Direction 1) or Inbound (Direction 2)
3. **Start Stop**: Boarding stop identifier
4. **Destination Stop**: Alighting stop identifier
5. **Pre-Journey Temporal Context**: Query date and planned travel calendar attributes

### Operational Distinction
- **Pre-Journey Features (Permitted)**: Static network topology, stop sequencing, distance in segments, and calendar context known before the bus arrives.
- **Post-Journey / In-Transit Information (Strictly Prohibited)**: Information that unfolds during or after the trip—such as individual segment run times, dwell times at intermediate stops, downstream telemetry dropouts, vehicle arrival timestamps, or full-trip operational durations—is strictly excluded from model feature matrices.

---

## 4. Feature Inventory & Leakage Audit

Every candidate column from the Task 2B journey dataset has been inspected and audited:

| Column | Candidate Status | Classification | ML Role | Leakage Check Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `trip_id` | Metadata | **B. POST-JOURNEY / IDENTIFIER** | Excluded from Features | Historical trip instance identifier. Causes extreme cardinality and overfits to specific past runs. Retained in CSV for trip isolation and clustering. |
| `route_id` | Network Topology | **A. SAFE FOR PREDICTION** | Excluded (Redundant) | GTFS route UUID; 1-to-1 redundant with `route_short_name`. |
| `route_short_name` | Query Input | **A. SAFE FOR PREDICTION** | **Feature (Categorical)** | Known before journey starts (passenger selects Route 10, 12, or 46). |
| `direction_id` | Query Input | **A. SAFE FOR PREDICTION** | **Feature (Categorical)** | Known before journey starts (inbound/outbound determined by stop pair). |
| `date` | Query Input | **A. SAFE FOR PREDICTION** | **Split & Calendar Base** | Known before journey starts; used to assign chronological splits and calendar features. |
| `day_of_week` | Derived Calendar | **A. SAFE FOR PREDICTION** | **Feature (Integer 0–6)** | Deterministically extracted from date (0=Mon, ..., 6=Sun). Safe. |
| `is_weekend` | Derived Calendar | **A. SAFE FOR PREDICTION** | **Feature (Binary 0/1)** | Deterministically extracted from date. Safe. |
| `month` | Derived Calendar | **A. SAFE FOR PREDICTION** | **Feature (Integer 7–9)** | Deterministically extracted from date. Safe. |
| `start_stop_id` | Query Input | **A. SAFE FOR PREDICTION** | **Feature (Categorical)** | Boarding stop GUID chosen by passenger. |
| `destination_stop_id` | Query Input | **A. SAFE FOR PREDICTION** | **Feature (Categorical)** | Alighting stop GUID chosen by passenger. |
| `start_segment` | Network Topology | **A. SAFE FOR PREDICTION** | **Feature (Integer 2–62)** | Sequence index of origin stop along the route line. |
| `destination_segment` | Network Topology | **A. SAFE FOR PREDICTION** | **Feature (Integer 2–62)** | Sequence index of destination stop along the route line. |
| `segments_traversed` | Network Topology | **A. SAFE FOR PREDICTION** | **Feature (Integer 1–55)** | Topological hop distance ($j - i + 1$). Pure static network geometry. |
| `observed_journey_time_seconds` | Target | **B. TARGET** | **PREDICTION TARGET** | Ground-truth observed duration. NEVER included in $X$. |
| `has_segment_gap` | Telemetry Quality | **B. POST-JOURNEY** | Excluded from Features | Dropouts occur during vehicle operation. Cannot be known prior to journey. Strictly used as filter (`== 0`). |
| `standard_journey_eligible` | Pipeline Quality | **B. POST-JOURNEY / FILTER** | Excluded from Features | Downstream segment eligibility flag. Strictly used as filter (`== 1`). |

### Leakage Audit Findings
- **Zero Segment Run Times / Dwell Times**: None included in feature set.
- **Zero Arrival / Departure Times**: None included.
- **Zero Full-Trip Aggregates**: No trip-level average speeds or total trip times used.
- **Zero Target Statistics**: No target encoding or target statistics computed using the prediction observation.

---

## 5. Pre-Journey Time-of-Day Investigation & Historical Features Methodology

### Focused Pre-Journey Time-of-Day Investigation
A dedicated audit was conducted across `Original Data/stop_times.txt`, `Original Data/trips.txt`, `Original Data/calendar_dates.txt`, and `Original Data/segment_level_data/segment_level_data.csv` to determine whether a valid pre-journey time-of-day feature could be derived:
1. **GTFS Relational Audit**: `Original Data/stop_times.txt` contains exactly 785,976 records, matching `segment_level_data.csv` row-for-row (1:1). Analysis of arrival and departure timestamps reveals that `stop_times.txt` is an ex-post GTFS export of observed vehicle GPS runs, not an independent planned schedule or static timetable. Stop dwell times ($departure\_time - arrival\_time$) and inter-stop elapsed times in `stop_times.txt` match `dwell_time_in_seconds` and `run_time_in_seconds` down to the exact second.
2. **Trips Structure**: In `trips.txt`, `service_id` is defined per calendar date (`service_YYYY-MM-DD`, 55 unique service IDs), and each trip corresponds to a specific physical vehicle run (`vehicle_id`) with retrospective start and end timestamps. There is no static timetable with planned departure frequencies or scheduled departure slots.
3. **Observed `start_time` Leakage & Usability**: In the passenger prediction scenario, a traveler querying the system before starting a journey does not have access to live vehicle GPS coordinates or future departure timestamps down to the second. For intermediate stops, the observed `start_time` inherently reflects accumulated delays or speeds across all preceding segments of that specific bus run. Using observed `start_time` would constitute post-journey telemetry leakage and assume non-existent real-time tracking at query time.
4. **Formal Decision (Rule 2 Applied)**: In accordance with project instructions, no synthetic departure times were invented, observed `start_time` was not substituted, and the ML-ready dataset (`Data/journey_ml_ready.csv`) was preserved unchanged without unnecessary data regeneration. Time-of-day prediction is formally documented as a future enhancement requiring an independent planned timetable schedule.

### Historical Baseline Methodology
- In this Task 2C stage, historical central tendencies are implemented as an external, leak-free **Baseline Lookup Model** (`ML/baseline_lookup.csv`).
- The lookup table is computed **strictly on the Training split** ($N = 9,926,268$ observations), recording historical median journey times for each $(route, direction, start, destination)$ pair.
- Zero future observations or validation/test target values were included.
- Dynamic expanding-window historical features are documented as a future modeling enhancement for Task 3, ensuring zero future-data leakage.

---

## 6. Zero-Second Journeys Analysis & Handling

- **Total In Input Dataset**: Exactly **517** rows out of 15,277,204 (0.0034%).
- **Route Breakdown**: Route 10: 280 (Dir 1: 134, Dir 2: 146); Route 12: 81 (Dir 1: 29, Dir 2: 52); Route 46: 156 (Dir 1: 109, Dir 2: 47).
- **Direction Breakdown**: Direction 1: 272 (52.61%), Direction 2: 245 (47.39%).
- **Journey Length**: **100% (517 out of 517)** are 1-segment journeys (`segments_traversed == 1`).
- **Originating Data Condition**: These records originate from segment pings where raw GPS timestamps registered zero elapsed seconds (`run_time_in_seconds == 0`). In Task 2A/2B, these were tagged with `zero_run_time_flag = 1` and excluded from standard run times (`standard_travel_time_eligible = 0`).
- **Eligibility Status**: Because a journey is standard-eligible only if all traversed segments are eligible, **0 out of 517 zero-second journeys are standard eligible** (`standard_journey_eligible == 0`).
- **Handling Decision**: **Excluded from ML Training**. By filtering the ML-ready dataset to `standard_journey_eligible == 1`, all 517 zero-second anomalies are excluded based on established project data-quality rules. Exactly 0 zero-second records enter `Data/journey_ml_ready.csv`.

---

## 7. Temporal Train / Validation / Test Split

A strict chronological split was established across the 53 available historical dates:

```text
Historical Dates (53 days):
[2024-07-29 ---------- 2024-09-02]  | [2024-09-03 to 2024-09-04] | [2024-09-05 --- 2024-09-12] | [2024-09-13 --- 2024-09-21]
           TRAIN (36 days)          |   EXCLUDED (Sep 3-4 gap)   |     VALIDATION (8 days)     |        TEST (9 days)
         9,926,268 rows (68.56%)    |   61,957 journeys excluded |   2,269,507 rows (15.68%)   |   2,281,911 rows (15.76%)
```

- **TRAIN SPLIT**:
  - **Date Range**: `2024-07-29` to `2024-09-02` (36 calendar days, 5 full weeks)
  - **Total Eligible Rows**: **9,926,268** (68.56% of eligible dataset)
  - **Unique Trips**: 13,466
- **UPSTREAM EXCLUSION**: `2024-09-03` to `2024-09-04` (Reduced GPS coverage dates; excluded upstream in Task 2B).
- **VALIDATION SPLIT**:
  - **Date Range**: `2024-09-05` to `2024-09-12` (8 calendar days, covers all 7 weekdays)
  - **Total Eligible Rows**: **2,269,507** (15.68% of eligible dataset)
  - **Unique Trips**: 3,126
- **TEST SPLIT**:
  - **Date Range**: `2024-09-13` to `2024-09-21` (9 calendar days, covers all 7 weekdays)
  - **Total Eligible Rows**: **2,281,911** (15.76% of eligible dataset)
  - **Unique Trips**: 3,093

### Temporal Integrity
- Strict chronological ordering: $\text{Train} < \text{Validation} < \text{Test}$.
- Zero date overlap between partitions.
- September 3–4 strictly absent.

---

## 8. Route, Direction, and Trip Isolation

- **Route Isolation**: Routes 10, 12, and 46 operate along distinct corridors. Features preserve route isolation; no cross-route leakage occurs.
- **Direction Isolation**: Outbound (Dir 1) and Inbound (Dir 2) trips are independent; features preserve directional boundaries.
- **Trip Isolation**: Journeys are constructed strictly within individual bus trips. No features borrow data across trips or across future observations of the same trip.
- **Coverage**: All 3 routes (10, 12, 46) and both directions (1, 2) have 100% representation in Train, Validation, and Test partitions.

---

## 9. Baseline Methodology & Performance

### Construction
The non-ML baseline is a hierarchical historical central tendency lookup constructed **strictly from the Training split**:
1. **Level 1 (Stop-Pair Median)**: Historical median duration for exact $(route, direction, start\_segment, destination\_segment)$ (7,424 pairs).
2. **Level 2 (Hop-Count Fallback)**: For rare unseen pairs (0.38% in Val, 0.21% in Test), fallback to historical median duration for $(route, direction, segments\_traversed)$ (275 hop groups).
3. **Level 3 (Global Fallback)**: Global training median duration ($1,362.0\text{ seconds} = 22.7\text{ mins}$).

### Baseline Evaluation Results

| Dataset Partition | Sample Size ($N$) | MAE (Seconds) | MAE (Minutes) | RMSE (Seconds) | RMSE (Minutes) | $R^2$ Score | Fallback Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Validation Split** | 2,269,507 | **191.91s** | **3.20 mins** | **325.23s** | **5.42 mins** | **0.9305** | 33 (< 0.002%) |
| **Test Split** | 2,281,911 | **202.48s** | **3.37 mins** | **358.98s** | **5.98 mins** | **0.9171** | 18 (< 0.001%) |

*The historical median achieves an $R^2 > 0.91$ and an MAE of $\approx 3.2$–$3.4$ minutes, establishing a strong, realistic benchmark for future ML models.*

---

## 10. Evaluation Metrics Locked

- **MAE (Mean Absolute Error)**: $\frac{1}{N} \sum |y_i - \hat{y}_i|$
  - Primary metric for communicating expected prediction accuracy to transit riders in minutes/seconds.
- **RMSE (Root Mean Squared Error)**: $\sqrt{\frac{1}{N} \sum (y_i - \hat{y}_i)^2}$
  - Heavily penalizes large prediction errors; vital for operators monitoring severe congestion delays.
- **$R^2$ (Coefficient of Determination)**: $1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$
  - Quantifies total travel time variance explained by the model across variable journey lengths.

---

## 11. ML-Ready Output Artifacts

1. **`Data/journey_ml_ready.csv`**:
   - Total Rows: **14,477,686** (100% of standard-eligible journeys)
   - Size: **1,641.77 MB** (reduced from 2.87 GB by excluding redundant text strings and post-journey flags)
   - Columns: `split`, `trip_id`, `route_short_name`, `direction_id`, `date`, `day_of_week`, `is_weekend`, `month`, `start_stop_id`, `destination_stop_id`, `start_segment`, `destination_segment`, `segments_traversed`, `observed_journey_time_seconds`
2. **`ML/baseline_lookup.csv`**: 7,424 stop-pair training medians.
3. **`ML/baseline_segments_fallback.csv`**: 275 hop-count fallback training medians.
4. **`ML/baseline_metrics.json`**: Machine-readable baseline evaluation metrics.

---

## 12. Known Limitations & Scope Boundaries

1. **Historical Dataset**: 53 active service days from July to September 2024.
2. **No Real-Time GPS Tracking**: No live bus tracking or live ETA calculation; predictions represent expected historical travel time for the selected trip parameters.
3. **No Schedule Deviation Baseline**: Static timetable schedule times are not merged; performance represents observed journey consistency.
4. **Segment 1 Excluded**: Segment 1 terminal dispatch records remain excluded from passenger journey origins per approved Decision 1.
5. **September 3–4 Excluded**: September 3–4 reduced-coverage dates remain excluded per approved Decision 2.
6. **No Time-of-Day Feature in MVP**: Excluded after focused investigation confirmed that GTFS files represent retrospective GPS runs rather than an independent planned timetable, and observed start time cannot be known prior to travel without live tracking.

---

## 13. Decisions Reserved for Task 3 (Model Training)

1. Selection and comparison of gradient-boosted tree algorithms (LightGBM vs. XGBoost vs. CatBoost).
2. Hyperparameter optimization and learning-rate tuning.
3. Feature encoding strategies (target encoding vs. categorical embedding for stop IDs).
4. Model serialization and deployment artifacts for the web application.
