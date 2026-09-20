# BusInsight — Analytical Dataset & Feature Preparation Report

**Task**: Task 2B — Analytical Dataset & Feature Preparation  
**Execution Date**: 2026-09-20  
**Source Dataset**: `Data\segment_level_clean.csv` (785,976 rows, 0 deleted)  
**Status**: Validated & Complete  

---

## 1. Input Validation
- **Input Path**: `C:\Project\001\BusInsight\Data\segment_level_clean.csv`
- **Row Count**: 785,976
- **Unique Trips**: 19,769
- **Unique Routes**: 3 (Routes 46, 10, 12)
- **Calendar Days**: 55 days (`2024-07-29` to `2024-09-21`)
- **Cryptographic Source Verification**: Original Data SHA-256 hashes 100% matched pre- and post-execution.

---

## 2. Analytical Segment Dataset (`analytical_segment_data.csv`)
- **Total Rows**: 785,976 (100% of clean records preserved; 0 rows deleted)
- **Total Columns**: 44 (added calendar/time features, stop names, target)
- **New Features Added**:
  - `start_stop_name`, `end_stop_name` (exact transit stop names from `stops.txt`)
  - `date_only` (ISO `YYYY-MM-DD`), `hour` (0–23), `day_of_week` (0–6), `day_of_week_name` ('Monday'–'Sunday')
  - `is_weekend` (binary 0/1), `month` (7–9), `week_of_year` (ISO calendar week)
  - `standard_run_time_seconds` (target: strictly eligible observations; blank/null for ineligible)
- **Standard Run Time Eligible Records**: 765,944 (97.45%)
- **Ineligible Records**: 20,032 (2.55%)

---

## 3. Route-Segment Summary (`route_segment_summary.csv`)
- **Total Segment Groups**: 300 route-direction-segment groups
- **Coverage**: All 3 routes across both directions (Direction 1 and Direction 2)
- **Statistics Computed**: Observation count, Min, P10, P25, Median, Mean, P75, P90, Max, Std Dev, and P90/Median consistency ratio.
- **Travel-Time Consistency (`p90_median_ratio`)**:
  - **Mean Ratio**: 2.01
  - **Median Ratio**: 1.67
  - **Min Ratio**: 1.00
  - **Max Ratio**: 14.74

### Sample Route-Segment Travel-Time Consistency Profiles
| Route | Dir | Seg | Start Stop | End Stop | Obs Count | P10 (s) | Median (s) | P90 (s) | P90/Median Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **10** | 1 | 2 | Ulitsa Birzhan sal | Ulitsa Il'iasa Esenberlina | 3,330.0 | 93.0s | 138.0s | 186.0s | **1.35x** |
| **10** | 1 | 12 | Park Atatiurk | Ulitsa Amman | 3,331.0 | 74.0s | 95.0s | 125.0s | **1.32x** |
| **10** | 2 | 6 | ul. Zhanadariia | ZhK Aq-Jol | 3,115.0 | 22.0s | 36.0s | 54.0s | **1.5x** |
| **12** | 1 | 6 | Shkola Zerde | Ulitsa Kenesary | 2,897.0 | 41.0s | 58.0s | 115.0s | **1.98x** |
| **12** | 2 | 2 | Mechet' Al'zhan Ana | Ulitsa Arnasai | 2,186.0 | 178.0s | 238.0s | 307.0s | **1.29x** |
| **12** | 2 | 52 | Shkola-litsei No. 15 | Ulitsa Moskovskaia | 6.0 | 55.5s | 100.0s | 116.0s | **1.16x** |
| **46** | 1 | 47 | Karakat | Zharkyn | 1.0 | 78.0s | 78.0s | 78.0s | **1.0x** |

---

## 4. Passenger Journey Dataset (`journey_training_data.csv`)
- **Total Journey Observations Generated**: 15,277,204
- **Trips Represented**: 19,685 trips
- **Standard Eligible Journeys**: 14,477,686 (94.77%)
- **Journeys Affected by Segment Gaps**: 621,754 (4.07%)
- **Journey Duration Statistics**:
  - **Min Duration**: 0 seconds
  - **10th Percentile (P10)**: 237 seconds (4.0 mins)
  - **25th Percentile (P25)**: 621 seconds (10.3 mins)
  - **Median (P50)**: **1,437 seconds (23.9 mins)**
  - **Mean**: 1,691.66 seconds (28.2 mins)
  - **75th Percentile (P75)**: 2,560 seconds (42.7 mins)
  - **90th Percentile (P90)**: 3,519 seconds (58.6 mins)
  - **Max Duration**: 20,319 seconds (5.64 hours)
- **Route & Direction Coverage**:
  - `Route_46_Dir_2`: 3,587,828 journeys (23.48%)
  - `Route_10_Dir_1`: 2,047,487 journeys (13.40%)
  - `Route_12_Dir_1`: 2,075,530 journeys (13.59%)
  - `Route_12_Dir_2`: 2,014,270 journeys (13.18%)
  - `Route_46_Dir_1`: 3,157,418 journeys (20.67%)
  - `Route_10_Dir_2`: 2,394,671 journeys (15.67%)

---

## 5. Historical Travel-Time Window Demonstration (P10–P90)
> [!TIP]
> **Passenger-Facing Interpretation**:
> "Historical travel time is typically within the **P10–P90 window**."  
> This provides an empirical, data-backed expectation without creating misleading claims of guaranteed arrival times or live tracking.

### Sample Journey Travel-Time Windows (Intermediate Corridors)
| Route | Direction | Origin Stop | Destination Stop | Typical Window (P10–P90) | Median Travel Time |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Route 10** | Dir 1 | Ulitsa Birzhan sal | Mechet' Al'zhan Ana | **45 – 68 mins** | 55.2 mins |
| **Route 10** | Dir 2 | Mechet' Al'zhan Ana | Ulitsa Birzhan sal | **44 – 65 mins** | 53.8 mins |
| **Route 12** | Dir 1 | Shkola-litsei No. 15 | Sadovodcheskoe obshchestvo Aviator | **41 – 62 mins** | 50.4 mins |
| **Route 46** | Dir 1 | Mu'sa dukeni | ZhK Komfort taun | **39 – 59 mins** | 47.6 mins |

---

## 6. Analytical Data Quality Handling & Approved Methodology Locks
1. **Segment 1 Treatment (Approved Decision 1)**: Segment 1 records (19,062 rows) remain 100% preserved in raw and analytical datasets (`analytical_segment_data.csv`), but are excluded from passenger journey-training data for the current MVP. Terminal-origin journey prediction is outside the current MVP because the source representation of segment 1 does not provide a sufficiently reliable separation between terminal dispatch/holding time and passenger travel time. This is a scope/methodology decision, not a claim that the underlying source data is incorrect.
2. **September 3–4, 2024 Treatment (Approved Decision 2)**: All records for September 3–4, 2024 (3,257 segment records) are preserved in the raw and analytical datasets. These dates are treated as incomplete-service / reduced-GPS-coverage dates and are excluded from the primary ML training/evaluation dataset (`journey_training_data.csv`). Exactly 61,957 journey rows were excluded to prevent upstream logging dropouts from distorting model training. This is a modeling/data-quality handling decision, not deletion of historical data.
3. **Existing Journey Construction Methodology**: Preserves the existing stop-to-stop journey construction ($i \le j$ pairs on non-terminal segments across completed trips). No redesign was performed.
4. **Zero-Duration Records**: Tagged with `zero_run_time_flag` and `zero_total_time_flag`. Excluded from standard travel-time calculations to prevent downward bias in journey estimations.
5. **Extreme Travel Times**: Neutral `extreme_travel_time_flag` applied to run times > 30 minutes. Records are retained in the dataset for operator analysis while filtered from customer-facing baseline predictions.
6. **Segment Gaps**: Tagged with `has_segment_gap = 1` on journey records spanning missing intermediate GPS sequences, distinguishing complete continuous journeys from incomplete sequences.
7. **No Data Destruction**: 100% of rows are retained in `analytical_segment_data.csv` (0 rows physically deleted).

---

## 7. Operational Limitations
1. **Historical Nature**: The dataset is strictly historical transit records (55 days, July–Sept 2024); it does NOT contain live GPS feeds.
2. **No Real-Time Tracking**: No live vehicle location or live dispatch feed is present; this system cannot provide live ETAs or dynamic delay alerts.
3. **Prototype Scope**: Represents 3 specific routes (10, 12, 46) in Astana, serving as an analytical travel-intelligence prototype rather than a city-wide operational dispatch platform.
4. **Schedule Absence**: No independent static timetable baseline was merged; all reliability metrics represent observed historical consistency rather than schedule deviation.
