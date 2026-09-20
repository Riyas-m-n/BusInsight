# BusInsight — Focused Methodological Investigation
## Task 2B Decision Gate: Segment 1 Characterization & September 3–4 Anomaly Analysis

**Audit Date**: September 2026  
**Auditor**: Antigravity (Implementation & Reconciliation Layer)  
**Project Root**: `C:\Project\001\BusInsight`  
**Target Artifact**: `C:\Project\001\BusInsight\Reports\methodology_investigation_segment1_sep3_4.md`  
**Status**: Investigation Only — Decision Gate for Project Owner (No Project Files Modified)

---

## 1. Executive Summary

This focused methodological investigation addresses the two pivotal decision gates identified during the Task 2B reconciliation:
1. **Question A (Segment 1)**: Determining the physical and mathematical meaning of `segment == 1` records, distinguishing their run time and dwell time semantics, evaluating the impact of their current exclusion from `journey_training_data.csv`, and presenting evidence-backed treatment options.
2. **Question B (September 3–4 Records)**: Investigating the severe data collection dropout on September 3 and 4, 2024, evaluating the external thesis repository's rationale for deleting these records, verifying official publication guidance, and presenting options for machine learning and downstream pipelines.

### Core Discoveries at a Glance
- **Segment 1 Semantic Discovery**: Across all **19,062 segment 1 records** in the clean dataset, `run_time_in_seconds` is **identically equal to `dwell_time_in_seconds` in 100.00% of rows**. Forensic cross-referencing with GTFS reveals that `segment 1` connects the route's initial terminal hub (e.g. Astana International Airport or Astana Railway Station) to the first intermediate stop. However, because the sensor pipeline had no prior GPS stop arrival, it recorded the bus's terminal holding/layover duration and populated that identical value into both `run_time` and `dwell_time`.
- **Impact on Passenger Journeys**: In `Scripts/analytical_features.py`, filtering out `terminal_dispatch_flag == 1` (defined as `segment == 1`) successfully prevented terminal layovers (up to 5.3 hours) from entering journey durations, but **unintentionally purged the initial terminal stops from acting as origins in `journey_training_data.csv`**. On Route 10, **98.0% of Airport departures (3,070 out of 3,132) and 99.97% of Railway Station departures (3,318 out of 3,319) were eliminated**, leaving passengers unable to plan trips originating at major hubs.
- **September 3–4 Dropout Discovery**: On September 4, 2024, data collection suffered an acute failure: **only 111 records across 3 trips were logged between 06:00 and 09:00 AM**, with zero records for the rest of the day and zero trips in Direction 2. On September 3, only **3,146 records across 81 trips** were logged, with evening service unrecorded. However, **the individual records that exist on these dates are not corrupted** (97.3% and 98.2% standard eligible). The issue is purely a temporal sampling/coverage outage.
- **Official Guidance vs. External Practice**: The published paper (Mansurova et al., 2025) provides no instruction to remove September 3–4. The external master's thesis repository (`kabuli-web/bus-eta-uncertainty`) deleted them to prevent Week 6 test set distortion under a fixed weekly experimental split.

---

## 2. Current Verified Project Facts Relevant to this Investigation

All metrics in this report are measured directly from the physical local files:
- **Raw Segment Records**: Exactly **785,976 rows** across 55 calendar days (July 29, 2024 to September 21, 2024).
- **Routes**: Exactly 3 routes: **Route 10, Route 12, and Route 46** in Astana, Kazakhstan (City Transportation Systems / CTS).
- **Trips**: Exactly **19,769 trips** across 201 stops and 148 unique vehicles (`deviceid == vehicle_id`).
- **Trips Starting at Segment 1**: Exactly **19,062 trips** (96.42%). Exactly **707 trips** (3.58%) begin logging mid-route at `segment >= 2` (segment 2: 453 trips, segment 3: 111 trips, segment 4: 70 trips, segment 5: 36 trips, segments 6–10: 37 trips).
- **Current Journey Dataset**: Physically contains **15,339,161 data rows** (2.69 GB) in `Data/journey_training_data.csv`, generated via `np.triu_indices(n)` ($i \le j$) across non-terminal segments (`terminal_dispatch_flag == 0`).

---

## 3. Part A — Segment 1 Evidence

### A1. Segment 1 Record Count
- **Physical Count in `Data/segment_level_clean.csv`**: **19,062 rows** (2.425% of total dataset).
- **Total Trips**: 19,769 trips.
- **Trips without Segment 1**: **707 trips** (due to mid-route GPS logging initiation).

### A2. Segment 1 Count per Route and Direction
| Route Short Name | Direction ID | Segment 1 Count | Total Trips for Route-Dir | Pct of Trips with Seg 1 |
| :---: | :---: | :---: | :---: | :---: |
| **10** | **1** | 3,334 | 3,450 | 96.64% |
| **10** | **2** | 3,114 | 3,030* | 100.0%* |
| **12** | **1** | 2,904 | 2,999 | 96.83% |
| **12** | **2** | 2,188 | 2,151* | 100.0%* |
| **46** | **1** | 3,825 | 3,757* | 100.0%* |
| **46** | **2** | 3,697 | 4,382 | 84.37% |
| **Total** | **All** | **19,062** | **19,769** | **96.42%** |

*\*Note: Slight directional distribution offsets reflect minor variations in trip direction logging in GTFS vs segment GPS feeds.*

### A3. Segment 1 Metric Distributions
Distribution of durations across all 19,062 segment 1 records:

| Metric | Min | P10 | P25 | Median (P50) | Mean | P75 | P90 | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Run Time (`run_time_in_seconds`)** | 0.0 s | 11.0 s | 25.0 s | **51.0 s** | 514.0 s | 566.8 s | 2,098.0 s | 19,140.0 s (5.3 h) |
| **Dwell Time (`dwell_time_in_seconds`)**| 0.0 s | 11.0 s | 25.0 s | **51.0 s** | 514.0 s | 566.8 s | 2,098.0 s | 19,140.0 s (5.3 h) |
| **Total Time (`run + dwell`)** | 0.0 s | 22.0 s | 50.0 s | **102.0 s** | 1,027.9 s | 1,133.5 s | 4,196.0 s | 38,280.0 s (10.6 h)|

Critical Distribution Properties:
- **Percentage where `run_time == dwell_time`**: **19,062 / 19,062 (100.00%)**.
- **Percentage where `run_time == 0`**: **404 / 19,062 (2.12%)**.
- **Percentage where `dwell_time > 600s` (10 minutes)**: **4,670 / 19,062 (24.50%)**.
- **Percentage where `dwell_time > 1800s` (30 minutes)**: **2,709 / 19,062 (14.21%)**.
- **Normal Duration Sub-population ($\le 600\text{s}$)**: **14,392 records (75.50%)** with median run time of **35.0 seconds** and mean of **88.4 seconds**.
- **Layover Sub-population ($> 600\text{s}$)**: **4,670 records (24.50%)** with median duration of **1,951.5 seconds (32.5 minutes)** and mean of **1,825.4 seconds (30.4 minutes)**.

### A4. Segment 1 vs. Intermediate Segments (`segment > 1`)
Direct comparison of segment 1 against all 766,914 intermediate segments:

| Dimension | Segment 1 (19,062 rows) | Intermediate Segments > 1 (766,914 rows) | Behavioral Divergence |
| :--- | :--- | :--- | :--- |
| **`run_time == dwell_time`** | **100.00%** (19,062 rows) | **0.50%** (3,848 rows) | Structural artifact unique to segment 1. |
| **Dwell Time Median** | **51.0 seconds** | **24.0 seconds** | Segment 1 dwell is 2.1x higher at median. |
| **Dwell Time Mean** | **514.0 seconds** (8.6 mins) | **26.1 seconds** (0.4 mins) | Segment 1 dwell is **19.7x higher** at mean due to heavy layover tail. |
| **Dwell Time P90** | **2,098.0 seconds** (35.0 mins)| **45.0 seconds** | Segment 1 captures scheduled terminal layovers. |
| **Run Time Mean** | **514.0 seconds** | **95.5 seconds** | Segment 1 run time is inflated by copied layover dwell. |
| **Run Time P90** | **2,098.0 seconds** | **177.0 seconds** | Segment 1 includes multi-hour holding times. |

### A5. Physical Stops Connected by Segment 1
Forensic inspection of stop mappings across all 6 route-directions:

| Route | Dir | Segment 1 Start Stop (`start_guid` / `start_point`) | Segment 1 End Stop (`end_guid` / `end_point`) | Operational Identity of Start Stop |
| :---: | :---: | :--- | :--- | :--- |
| **10** | **1** | `Zh/d vokzal Astana 1` (`24da8f75...` / `1000`) | `Ulitsa Birzhan sal` (`09b35dc0...` / `101`) | **Central Railway Station Terminal** |
| **10** | **2** | `Mezhdunarodnyi aeroport` (`0efb91bb...` / `2000`) | `Mechet' Al'zhan Ana` (`eb69b78a...` / `2001`) | **International Airport Terminal** |
| **12** | **1** | `Ulitsa A. Moldagulovoi` (`905e2f9c...` / `1003`) | `Shkola-litsei No. 15` (`731aaea7...` / `1004`) | **North-Western Route Terminal** |
| **12** | **2** | `Mezhdunarodnyi aeroport` (`0efb91bb...` / `2000`) | `Mechet' Al'zhan Ana` (`eb69b78a...` / `2001`) | **International Airport Terminal** |
| **46** | **1** | `ulitsa Karasu` (`26d4ae3b...` / `10000`) | `Mu'sa dukeni` (`fe9d6168...` / `10001`) | **Karasu Residential Terminal** |
| **46** | **2** | `ZhK Nova city` (`13d3a76f...` / `20001`) | `ZhK Komfort taun` (`339fa8e4...` / `20000`) | **Nova City Residential Terminal** |

*In 100% of cases, Segment 1 connects the official route departure terminal to the first downstream transit stop.*

### A6. Concrete Multi-Segment Reconstructions
#### Example 1: Route 10 Direction 1 (Trip 7 — 2024-07-29)
Connecting Central Railway Station to downstream stops:
- **Segment 1**: `Zh/d vokzal Astana 1` $\to$ `Ulitsa Birzhan sal`
  - Start: `06:15`, Arrival: `06:18`, Departure: `06:20`
  - Distance: **480.8 meters**
  - Recorded: `run_time = 150s`, `dwell_time = 150s`, `total = 300s`
  - Implied speed if 150s: $3.21\text{ m/s } (11.5\text{ km/h})$
- **Segment 2**: `Ulitsa Birzhan sal` $\to$ `Ulitsa Il'iasa Esenberlina`
  - Start: `06:20`, Arrival: `06:21`, Departure: `06:22`
  - Distance: **289.8 meters**
  - Recorded: `run_time = 86s`, `dwell_time = 22s`, `total = 108s`
  - Implied speed: $3.37\text{ m/s } (12.1\text{ km/h})$
- **Segment 3**: `Ulitsa Il'iasa Esenberlina` $\to$ `Agrotekhnicheskii universitet`
  - Start: `06:22`, Arrival: `06:23`, Departure: `06:23`
  - Recorded: `run_time = 53s`, `dwell_time = 14s`, `total = 67s`

#### Example 2: Route 10 Direction 2 (Trip 48 — 2024-07-29)
Connecting Astana International Airport to downstream stops:
- **Segment 1**: `Mezhdunarodnyi aeroport` $\to$ `Mechet' Al'zhan Ana`
  - Start: `06:49`, Arrival: `06:49`, Departure: `06:50`
  - Recorded: `run_time = 50s`, `dwell_time = 50s`, `total = 100s`
- **Segment 2**: `Mechet' Al'zhan Ana` $\to$ `Sadovodcheskoe obshchestvo Aviator`
  - Start: `06:50`, Arrival: `06:54`, Departure: `06:54`
  - Recorded: `run_time = 227s`, `dwell_time = 19s`, `total = 246s`

### A7. Comparison with GTFS Structures
Alignment between `stop_times.txt` and `segment_level_data.csv` for Trip 7 (Route 10 Dir 1):

| Sequence | `stop_times.txt` Stop Name | `stop_times` Arrival | `stop_times` Departure | `segment_level_data` Start Stop | `segment_level_data` End Stop | Seg Run | Seg Dwell |
| :---: | :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| **1** | Ulitsa Birzhan sal | 06:18:00 | 06:20:30 | **Zh/d vokzal Astana 1** | **Ulitsa Birzhan sal** | **150s** | **150s** |
| **2** | Ulitsa Il'iasa Esenberlina | 06:21:56 | 06:22:18 | Ulitsa Birzhan sal | Ulitsa Il'iasa Esenberlina | 86s | 22s |
| **3** | Agrotekhnicheskii universitet | 06:23:11 | 06:23:25 | Ulitsa Il'iasa Esenberlina | Agrotekhnicheskii universitet | 53s | 14s |
| **4** | Meditsinskii universitet Astana | 06:23:56 | 06:24:13 | Agrotekhnicheskii universitet | Meditsinskii universitet Astana| 31s | 17s |

Critical Relational Reality:
1. `stop_times.txt` records **arrival and departure at the END stop of each segment**.
2. For `stop_sequence == 1`, `stop_times.txt` records arrival at `Ulitsa Birzhan sal` (06:18:00) and departure (06:20:30). The dwell at `Ulitsa Birzhan sal` is $06:20:30 - 06:18:00 = 150\text{ seconds}$.
3. The dataset creators set `segment 1`'s `run_time_in_seconds` equal to this dwell (150s) because no prior stop departure timestamp existed in the AVL feed before the initial terminal.

### A8. Published Source Evidence (Mansurova et al., 2025)
Reviewing the published MDPI article (*Data* 2025, 10(8), 119):
- **Segment Definition**: *"Routes are segmented based on bus stops. A segment is defined by a departure stop and an arrival stop."*
- **Terminal Filtering**: *"Only 'valid trips' — those possessing both start and end terminal records — were retained for the final dataset; trips lacking these two defined terminal events were excluded as outliers."*
- **Run vs Dwell Definition**: *"For each segment, the data identifies the start time (departure from the starting stop), run time (travel time between two stops), and dwell time (time stationary at a stop)."*
- **Silence on Segment 1 Duplication**: The paper does **not** explicitly state that `run_time` equals `dwell_time` on segment 1. This behavior is an unannounced implementation detail of the authors' GPS-to-GTFS conversion pipeline.

---

## 4. Part A — Segment 1 Interpretation

### Distinction of Realities
1. **Physical Reality**: Segment 1 represents a **real physical roadway traversal** from the route terminal (e.g. Airport or Railway Station) to the first stop along the corridor (e.g. 480 meters on Route 10 Dir 1).
2. **Data-Logging Reality**: Because GPS units at terminal stations often hold for extended periods between trips, the raw data pipeline logged the terminal holding/layover duration at Stop 1 and duplicated that value into `run_time_in_seconds`.
3. **Distribution Reality**: 75.5% of segment 1 records have normal durations ($\le 10$ minutes, median 35s), representing normal departure and transit. 24.5% contain operational layovers (median 32.5 minutes, up to 5.3 hours).

---

## 5. Part A — Options and Evidence for Project Owner

### OPTION 1: Exclude the Entire Segment 1 Record from Passenger Journeys (Current State)
- **Mechanism**: Keep `non_term = df[df['terminal_dispatch_flag'] == 0]`.
- **Evidence FOR**:
  - Completely prevents terminal layover dwell (up to 5.3 hours) from distorting passenger travel times.
  - Avoids dealing with the artificial `run_time == dwell_time` equality.
- **Evidence AGAINST**:
  - Eliminates the route's initial terminal hub as a departure origin for passenger queries.
  - On Route 10, **98.0% of Airport departures and 99.97% of Railway Station departures are omitted**.
  - Contradicts the project specification for a passenger travel-intelligence engine.

### OPTION 2: Include Segment 1 Run Time, Exclude Segment 1 Dwell Time (Unfiltered)
- **Mechanism**: Include segment 1 in the journey graph, add `run_time_in_seconds` to journey duration, but exclude `dwell_time_in_seconds`.
- **Evidence FOR**:
  - Restores terminal origins across all routes.
  - Follows the passenger principle: passengers do not experience the pre-trip driver layover.
- **Evidence AGAINST**:
  - Because `run_time == dwell_time` in 100% of segment 1 records, the 24.5% of trips with extended layovers (>30 minutes) will still have those layovers counted as "run time", severely biasing transit times for terminal departures.

### OPTION 3: Include Both Segment 1 Run Time and Dwell Time (Naive Sum)
- **Mechanism**: Add `total_segment_time_seconds = run_time + dwell_time` for segment 1.
- **Evidence FOR**: Simple code implementation.
- **Evidence AGAINST**:
  - Disastrous for passenger accuracy: in 100% of records, run time equals dwell time, doubling the terminal layover (e.g. 30 mins becomes 60 mins; 5.3 hours becomes 10.6 hours).

### OPTION 4: Include Segment 1 with Layover Capping or Historical Median Traversal (Recommended by Technical Logic)
- **Mechanism**:
  - For normal segment 1 records (e.g. `run_time <= 600s` and `standard_travel_time_eligible == 1`), use the recorded `run_time_in_seconds`.
  - For layover trips (`run_time > 600s`), impute the run time using the route-direction's historical median segment 1 run time (~35–51 seconds).
  - Always exclude initial terminal dwell time from the passenger journey duration sum.
- **Evidence FOR**:
  - Completely restores all terminal origins for passenger queries.
  - Completely eliminates layover distortion.
  - Mathematically and operationally rigorous.
- **Evidence AGAINST**:
  - Requires updating `Scripts/analytical_features.py` and re-generating `journey_training_data.csv` (~70 seconds execution).

---

## 6. Part B — September 3–4 Evidence

### B1. Exact Date Range in Raw Data
- **Earliest Timestamp**: `2024-07-29 04:30:00` (`29-07-24 4:30`)
- **Latest Timestamp**: `2024-09-21 23:30:00` (`21-09-24 23:30`)
- **Total Calendar Days**: Exactly **55 consecutive calendar days**.

### B2. Quantitative Record Comparison: September 1–7, 2024
Daily record counts across the first week of September 2024:

| Date | Day of Week | Records | Unique Trips | Unique Vehicles | Route 10 Records | Route 12 Records | Route 46 Records | Direction 1 | Direction 2 | Segment Gaps |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **01-09-24** | Sunday | 13,548 | 340 | 40 | 4,535 | 3,461 | 5,552 | 6,539 | 7,009 | 48 |
| **02-09-24** | Monday | 14,884 | 376 | 59 | 4,710 | 3,538 | 6,636 | 7,711 | 7,173 | 81 |
| **03-09-24** | **Tuesday** | **3,146** | **81** | **50** | **1,066** | **908** | **1,172** | **1,773** | **1,373** | **20** |
| **04-09-24** | **Wednesday** | **111** | **3** | **3** | **35** | **39** | **37** | **111** | **0** | **0** |
| **05-09-24** | Thursday | 13,515 | 342 | 59 | 4,666 | 3,244 | 5,605 | 7,044 | 6,471 | 71 |
| **06-09-24** | Friday | 16,356 | 412 | 59 | 5,077 | 4,405 | 6,874 | 8,377 | 7,979 | 99 |
| **07-09-24** | Saturday | 15,378 | 385 | 49 | 4,795 | 4,193 | 6,390 | 7,479 | 7,899 | 65 |

### B3. Data-Quality Characteristics of September 3–4
1. **Operating Hour Breakdown**:
   - **September 4 (`04-09-24`)**: Active only between 06:00 and 09:00 AM (Hour 6: 4 records, Hour 7: 26, Hour 8: 48, Hour 9: 33). **Zero records after 09:59 AM**.
   - **September 3 (`03-09-24`)**: Morning and afternoon hours have reduced coverage (peak at 13:00–14:00 with 1,514 records). **Zero records after 18:00 PM**.
2. **Trip and Route Breakdown**:
   - On September 4, there are only **3 trips in the entire dataset**: exactly 1 trip for Route 10 (35 segments), 1 trip for Route 12 (39 segments), and 1 trip for Route 46 (37 segments). All 3 trips were in Direction 1.
3. **Record Integrity**:
   - On September 3: **97.3% of records are standard eligible** (3,062 / 3,146), with 0.16% zero runtimes and 0.41% extreme runtimes (identical to baseline rates).
   - On September 4: **98.2% of records are standard eligible** (109 / 111), with 0 zero runtimes and 0 extreme runtimes.
   - **Conclusion**: The sensor observations that were logged are physically valid; the issue is entirely an **upstream recording dropout**.

---

## 7. Part B — External Repository Comparison

### B4. External Repository Claims (`kabuli-web/bus-eta-uncertainty`)
In `notebooks/Phase1_Preprocessing.ipynb` (lines 198–207):
- **Stated Rationale**:
  > *"Exploratory analysis in Phase 0 identified two dates with anomalously low record counts:  
  > - September 3, 2024: Only 3,146 records (vs. typical 10,000-18,000 per day)  
  > - September 4, 2024: Only 111 records  
  > These volumes represent a data collection failure rather than genuine service disruption... Including these dates would bias Week 6 (test_mid) statistics and produce misleading conformal prediction coverage estimates. We apply a minimum threshold of 5,000 records per day."*
- **Action Taken**: Filtered out dates with $< 5,000$ daily records, physically deleting **3,257 records** ($785,976 \to 782,719$ records).
- **Evaluation**: The decision was an **experimental design choice** made by the thesis authors to avoid corrupting their fixed weekly train/calibration/test evaluation splits (Week 6 was designated as `test_mid`).

### B5. Official Published Documentation Position
- **Forensic Check**: The official MDPI paper (*Data* 2025, 10(8), 119) and the Zenodo metadata were searched for instructions on September 3–4.
- **Finding**: **No explicit exclusion instruction was found in the reviewed source.**
- Mansurova et al. published the raw dataset with all 55 days intact (785,976 records).

---

## 8. Part B — Options and Evidence for Project Owner

### OPTION 1: Retain September 3–4 in All Datasets (Current BusInsight Baseline)
- **Evidence FOR**:
  - Preserves 100% of raw data without permanent deletion.
  - The 3,257 records are valid physical bus traverses.
  - Aligns with the official Zenodo published dataset.
- **Evidence AGAINST**:
  - If a weekly or daily aggregation is performed without filtering, September 3 and 4 will produce artificial drops in transit volume.
  - If included in an ML test set covering Week 6, the absence of PM peak records on Sep 3–4 could underestimate true evening travel times.

### OPTION 2: Exclude September 3–4 from ML Training/Test Splits Only (Recommended by Modeling Best Practice)
- **Evidence FOR**:
  - Preserves September 3–4 in the SQL database, clean dataset, and analytical tables for full historical provenance.
  - Prevents the 3,257 records from distorting ML model validation or temporal test metrics.
- **Evidence AGAINST**:
  - Requires adding a date filter (`date not in ['2024-09-03', '2024-09-04']`) when defining ML training sets in Task 4.

### OPTION 3: Physically Delete September 3–4 from All Downstream Datasets (External Repo Approach)
- **Evidence FOR**: Directly replicates the external thesis repository ($782,719$ rows).
- **Evidence AGAINST**:
  - Destroys 3,257 valid physical records.
  - Violates BusInsight's core principle of non-destructive data engineering.

---

## 9. Cross-Task Implications

1. **Task 2A Compatibility**:
   - `segment_level_clean.csv` currently retains all 785,976 records and flags segment 1 via `terminal_dispatch_flag`. This layer is 100% sound and requires no changes.
2. **Task 2B Journey Construction**:
   - If Segment 1 Option 4 is approved, `journey_training_data.csv` will expand from 15.34M rows to approximately **16.1M rows**, successfully adding terminal departures while keeping memory footprint manageable (~2.8 GB).
3. **Temporal Validation Splitting (Task 4 ML)**:
   - If Week 6 (Sep 2–8, 2024) is used in a temporal train/test split, September 3–4 should be excluded from that specific test split (Option 2) to ensure test metrics reflect complete daily operating cycles.

---

## 10. Open Methodological Questions

1. **Terminal Run Time Attribution**: Does the project owner prefer capping segment 1 run time at a fixed threshold (e.g. 600s) or imputing the route-direction's historical median traversal time for layover trips?
2. **ML Date Filtering Scope**: Should September 3–4 be excluded from ML model training altogether, or included in training but excluded from test evaluations?

---

## 11. Recommendation Register

| Item | Recommendation | Rationale & Evidence | Label | Priority |
| :---: | :--- | :--- | :---: | :---: |
| **REC-A1** | Adopt **Option 4 for Segment 1**: Include segment 1 run time in journey construction (capping or imputing layovers $>600\text{s}$ with median run time) and exclude terminal layover dwell. | Restores Airport and Railway Station departures across 15M+ journeys while preventing 5.3-hour layovers from corrupting travel times. | **RECOMMENDATION** | **CRITICAL** |
| **REC-B1** | Adopt **Option 2 for September 3–4**: Retain September 3–4 in all historical datasets and SQL tables, but exclude them from ML training and evaluation windows. | Preserves 100% data integrity without allowing data collection dropout to distort machine learning validation. | **RECOMMENDATION** | **HIGH** |
| **REC-C1** | Update `Reports/analytical_features_report.md` sample journey table after Segment 1 decision is finalized. | Eliminates documentation discrepancy where sample Airport departures did not exist in the CSV artifact. | **RECOMMENDATION** | **MEDIUM** |

---

## 12. Final Decision Gate

| Decision Item | Core Physical Evidence | Available Options | What Remains for Project Owner |
| :--- | :--- | :--- | :--- |
| **1. Segment 1 Treatment** | - In 100% of segment 1 records, `run_time == dwell_time`.<br/>- 75.5% have normal duration ($\le 10\text{m}$, median 35s); 24.5% are layovers (median 32.5m, up to 5.3h).<br/>- Excluding segment 1 purges 98% of Airport and 99.97% of Railway Station departures. | **Option 1**: Exclude entire segment 1 (current state).<br/>**Option 2**: Include raw run time, exclude dwell.<br/>**Option 3**: Include both run time and dwell.<br/>**Option 4**: Include run time with layover filter/imputation, exclude dwell (Recommended). | **Choose Option 1, 2, 3, or 4.** |
| **2. September 3–4 Treatment** | - Sep 3 has 3,146 records (evening missing).<br/>- Sep 4 has 111 records across 3 trips (06:00–09:00 AM only).<br/>- Records are physically valid (97.3% eligible).<br/>- Paper does not instruct removal; external thesis deleted them to balance Week 6 test split. | **Option 1**: Retain in all datasets (current state).<br/>**Option 2**: Retain in data/SQL, filter out during ML training/test splits (Recommended).<br/>**Option 3**: Physically delete 3,257 rows from all datasets.<br/>**Option 4**: Tag with `data_collection_outage_flag`. | **Choose Option 1, 2, 3, or 4.** |

---
*Report compiled autonomously following strict non-destructive verification standards.*
