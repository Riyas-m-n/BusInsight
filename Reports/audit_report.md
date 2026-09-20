# BusInsight — Comprehensive Data Audit & Relational Integrity Report

**Task**: Task 1 — Data Audit, Integrity Validation & Relational Ingestion Pipeline  
**Execution Date**: 2026-09-20  
**Dataset**: Astana Public Transit GPS & GTFS Records  

---

## 1. Executive Summary

An end-to-end data audit was conducted across all 7 raw Astana transit files in `C:\Project\001\Data`. 
The audit verified 100% referential integrity across the GTFS relational schema and revealed critical domain-specific insights 
regarding origin terminal dwell times, zero-duration anomalies, and heavy-tailed travel-time distributions.

### Key Audit Highlights
- **Total Segment Records**: 785,976
- **Unique Trips**: 19,769 across **3 routes** (46, 10, 12)
- **Unique Calendar Dates**: 55 days (2024-07-29 to 2024-09-21)
- **Referential Match Rate**: **100.0%** (0 orphan segments, 0 orphan trips, 0 orphan stops)
- **Missing Values / Exact Duplicates**: **0** (0 null cells, 0 duplicate rows)
- **Topological Continuity**: **100.0%** match on all 762,912 consecutive segment transitions (`end_guid` of segment $k$ = `start_guid` of segment $k+1$)
- **Domain Discovery (Terminal Layover)**: In 100% of segment 1 records (19,062), `run_time_in_seconds` equals `dwell_time_in_seconds`. 98.05% of extreme dwell times (>10 min) occur at the trip origin terminal.

---

## 2. Raw File Inventory & Relational Validation

| File Name | Record Count | Encoding | Integrity Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `agency.txt` | 1 | UTF-8 | Validated | CTS (City Transportation Systems), Asia/Almaty |
| `calendar_dates.txt` | 55 | UTF-8 | Validated | 55 consecutive calendar days |
| `routes.txt` | 3 | Windows-1252 | Validated | Contains 0x96 en-dash; routes 46, 10, 12 |
| `stops.txt` | 201 | UTF-8 | Validated | 201 unique transit stops |
| `trips.txt` | 19,769 | UTF-8 | Validated | 19,769 scheduled trips, 148 unique vehicles |
| `stop_times.txt` | 785,976 | UTF-8 | Validated | 785,976 scheduled stop arrival/departures |
| `segment_level_data.csv` | 785,976 | UTF-8 | Audited | 785,976 segment travel observations |

### Relational Integrity Breakdown
- **Segment → Trip**: 19,769 unique trips in segments; 100% exist in `trips.txt` (0 orphan records).
- **Trip → Route**: All 19,769 trips map to valid routes in `routes.txt` (0 orphans).
- **Segment → Stop**: All 200 `start_guid`s and 201 `end_guid`s map directly to `stops.txt` `stop_id`.
- **Stop Times vs Segment Row Match**: Exactly 0 trips have mismatched counts between `stop_times.txt` and `segment_level_data.csv` (perfect 1:1 match per trip).

### Distribution by Route
| Route Short Name | Trips Count | Share of Trips | Segment Records | Share of Segments |
| :--- | :--- | :--- | :--- | :--- |
| **Route 46** | 8,139 | 41.17% | 335,078 | 42.63% |
| **Route 10** | 6,480 | 32.78% | 243,243 | 30.95% |
| **Route 12** | 5,150 | 26.05% | 207,655 | 26.42% |

---

## 3. Segment Dataset Quality & Connectivity Audit

### Data Hygiene & Timestamps
- **Missing Values**: 0 across all 15 columns.
- **Exact Duplicate Rows**: 0.
- **Duplicate `(trip_id, segment)` Combinations**: 0.
- **Timestamp Validity**: 100% of timestamps (`start_time`, `arrival_time`, `departure_time`) parse without errors.
- **Temporal Consistency**: 0 records have `arrival_time < start_time` or `departure_time < arrival_time`.
- **Direction Integrity**: Direction is strictly bounded to values `1` (390,564) and `2` (395,412).
- **Self-loops**: 0 records where `start_point == end_point`.

### Network Sequence & Connectivity
- **Consecutive Transitions**: 762,912 transitions checked between segment $k$ and segment $k+1$.
- **Topological Continuity**: **0 mismatches** — whenever segment numbers increment by 1, the `start_guid` of segment $k+1$ exactly equals `end_guid` of segment $k$ in 100.0% of cases.
- **Trips Not Starting at Segment 1**: 707 trips (3.58%) start at segment 2 or later (delayed GPS ping initialization).
- **Trips with Internal Gaps**: 2,640 trips (13.35%) omit intermediate segments (total 3,295 gap events).

### Origin Terminal Layover Discovery
> [!IMPORTANT]
> In all **19,062 records where `segment == 1`**, `run_time_in_seconds` is identical to `dwell_time_in_seconds`. 
> Furthermore, **98.05% of all dwell times exceeding 10 minutes** occur on segment 1. 
> This proves that segment 1 reflects the initial vehicle dispatch layover at the origin terminal rather than an en-route transit travel time.

---

## 4. Distribution Analysis & Outlier Profiling

| Metric | Run Time (s) | Dwell Time (s) | Total Segment Time (s) |
| :--- | :--- | :--- | :--- |
| **Count** | 785,976 | 785,976 | 785,976 |
| **Mean** | 105.6 | 37.92 | 143.52 |
| **Std Dev** | 188.43 | 156.45 | 326.47 |
| **Min** | 0.0 | 0.0 | 0.0 |
| **25th Percentile (Q1)** | 42.0 | 15.0 | 65.0 |
| **Median (Q2)** | **70.0** | **24.0** | **97.0** |
| **75th Percentile (Q3)** | 113.0 | 34.0 | 143.0 |
| **IQR** | 71.0 | 19.0 | 78.0 |
| **90th Percentile** | 183.0 | 47.0 | 217.0 |
| **95th Percentile** | 267.0 | 61.0 | 304.0 |
| **99th Percentile** | 645.0 | 209.0 | 794.0 |
| **99.9th Percentile** | 2525.03 | 2460.05 | 4932.0 |
| **Max** | 19,140.0 | 19,140.0 | 38,280.0 |
| **Skewness** | 14.15 | 20.86 | 18.32 |
| **Kurtosis** | 560.58 | 1096.77 | 915.57 |

### Outlier & Extreme Threshold Breakdown
| Threshold Category | Threshold | Record Count | Percentage of Dataset | Operational Rationale |
| :--- | :--- | :--- | :--- | :--- |
| Non-positive Run Time | $\le 0$ seconds | 925 | 0.118% | GPS logging error or zero-second ping transition |
| Non-positive Total Time | $\le 0$ seconds | 475 | 0.060% | Both run time and dwell time equal 0 |
| High Run Time | > 300s (5 min) | 30,879 | 3.929% | Heavy congestion, traffic signal delay |
| Severe Run Time | > 600s (10 min) | 8,763 | 1.115% | Gridlock, incident, or delayed segment |
| Extreme Run Time | > 1800s (30 min) | 3,158 | 0.402% | Breakdown, shift change, or sensor dropout |
| Ultra Run Time | > 3600s (1 hour) | 105 | 0.013% | Equipment detachment / depot return |
| High Dwell Time | > 120s (2 min) | 11,618 | 1.478% | Heavy boarding / wheelchair / intersection |
| Terminal Dwell Time | > 600s (10 min) | 4,778 | 0.608% | Origin layover / driver rest period |

---

## 5. Verified Facts vs. Detected Anomalies

### Verified Facts
1. The dataset contains exactly 785,976 segment records spanning 55 unique dates (2024-07-29 to 2024-09-21) and 19,769 trips across routes 46, 10, and 12.
2. Referential integrity across the transit network is 100.0% intact. There are zero orphan segments, trips, or stops.
3. For all consecutive segments within trips, the departure stop of the next segment matches the arrival stop of the prior segment with 100.0% topological fidelity.
4. Standard UTF-8 parsing fails on `routes.txt` due to Windows-1252 byte 0x96 (en-dash); reading with `cp1252` resolves all characters cleanly.
5. All timestamps (`start_time`, `arrival_time`, `departure_time`) conform to `%d-%m-%y %H:%M` and maintain non-negative sequential order.

### Detected Anomalies
1. **Zero-Duration Records**: 925 records exhibit `run_time_in_seconds == 0`, of which 475 also have `dwell_time_in_seconds == 0`.
2. **Origin Dwell Duplication**: All 19,062 records where `segment == 1` duplicate dwell time into `run_time_in_seconds`.
3. **Extreme Outliers**: Runtimes reach 19,140s (5.3 hours) and total segment times reach 38,280s (10.6 hours), resulting in extreme kurtosis (560.58).
4. **Missing Intermediate Segments**: 2,640 trips (13.35%) skip segment sequence numbers due to GPS dropout or geofence misses.
5. **Unordered Storage**: Segment records in the raw CSV are not stored sequentially by trip or time.

---

## 6. Proposed Cleaning Rules & Specification Impact

Based on the empirical evidence gathered during this audit, the following rules are proposed for subsequent analytical and ML pipeline tasks:

### RULE-01: Exclude zero/non-positive total travel time records
- **Evidence**: 475 records have run_time_in_seconds == 0 AND dwell_time_in_seconds == 0 (total_time == 0). A bus physically cannot traverse a segment in 0 seconds.
- **Proposed Action**: Filter out records where total_segment_time <= 0.

### RULE-02: Exclude or separate origin terminal records (segment == 1)
- **Evidence**: All 19,062 segment 1 records have run_time_in_seconds == dwell_time_in_seconds. Furthermore, 98.05% of extreme dwell times (> 600s) occur on the first segment. These reflect terminal dispatch holding/layovers, not on-road travel time.
- **Proposed Action**: Separate segment == 1 dispatch wait times from running segment journey estimations.

### RULE-03: Cap/filter extreme operational outlier runtimes (> 1,800s / 30 mins)
- **Evidence**: 3,158 records (0.40%) exceed 1,800 seconds and 105 exceed 1 hour (max 19,140s / 5.3 hours). Segments are short urban intervals (~1 km). These represent breakdowns, sensor detachments, or GPS tracking suspended mid-route.
- **Proposed Action**: Flag records with run_time > 1800s as abnormal/breakdown outliers for specialized operator analysis; exclude from standard passenger baseline models.

### RULE-04: Chronological sorting and multi-index establishment
- **Evidence**: The raw segment CSV is unsorted, scattering trips and segment sequences across the 154MB file.
- **Proposed Action**: Sort datasets by trip_id, segment, and start_time to guarantee temporal ordering and enable sequential feature engineering.

### RULE-05: Explicit route enrichment
- **Evidence**: segment_level_data.csv does not contain route_id. Trips must be joined with trips.txt to access route_id and routes.txt to access route_short_name (10, 12, 46).
- **Proposed Action**: Denormalize or index route_id and route_short_name into the analytical table/view.

---

## 7. Next Recommended Task

> **Recommended Next Step**: **Task 2 — Clean Analytical Dataset & SQL Schema DDL Generation**  
> Following user approval of the cleaning rules, execute a reproducible data cleaning script that applies the verified filtering criteria, sorts segments sequentially, enriches route keys, and prepares the structured tables for MySQL ingestion.
