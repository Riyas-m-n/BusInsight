# BusInsight — Data Cleaning & Quality Stratification Report

**Task**: Task 2A — Clean Analytical Dataset Generation & Data-Quality Validation  
**Execution Date**: 2026-09-20  
**Source Directory**: `C:\Project\001\BusInsight\Original Data` (Immutable/Read-Only)  
**Target Dataset**: `C:\Project\001\BusInsight\Data\segment_level_clean.csv`  

---

## 1. Executive Summary
The derived analytical dataset `segment_level_clean.csv` was generated from the protected raw Astana dataset. 
In strict adherence to the project specification, **0 rows were physically deleted** (785,976 source rows $\to$ 785,976 clean rows). 
Data hygiene is achieved through transparent, deterministic quality flags that separate normal on-road passenger travel observations 
from terminal dispatch holds, zero-duration errors, and extreme breakdown outliers.

---

## 2. Before vs. After Dataset Profile

| Metric / Dimension | Before (`segment_level_data.csv`) | After (`segment_level_clean.csv`) | Change / Action |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 785,976 | 785,976 | **0 rows deleted (100% retained)** |
| **Total Columns** | 15 | 33 | +18 derived & metadata columns |
| **Unique Trips** | 19,769 | 19,769 | Exact match (100% coverage) |
| **Unique Routes** | 3 (unmapped in CSV) | 3 (`10`, `12`, `46` enriched) | Enriched from `trips.txt` & `routes.txt` |
| **Unique Dates** | 55 | 55 | 55 consecutive calendar days |
| **Missing Values** | 0 nulls | 0 nulls | Maintained 100% completeness |
| **Duplicate Rows** | 0 | 0 | 0 duplicates verified |
| **Ordering** | Unsorted | Sorted | Explicitly ordered by `(trip_id, segment, start_time)` |
| **Consecutive Connectivity** | 100% stop continuity | 100% stop continuity | 0 stop mismatches across 762,912 transitions |

---

## 3. Analytical & Quality Flags Summary

| Flag Name | Record Count | Percentage | Operational Rationale |
| :--- | :--- | :--- | :--- |
| `terminal_dispatch_flag` | 19,062 | 2.425% | Identifies initial origin stop (`segment == 1`) terminal layover |
| `zero_run_time_flag` | 925 | 0.118% | Observations with `run_time_in_seconds == 0` |
| `zero_total_time_flag` | 475 | 0.060% | Observations with both run and dwell equal to 0 |
| `run_time_over_10m_flag` | 8,763 | 1.115% | Urban segment travel time exceeding 10 minutes (severe congestion) |
| `run_time_over_30m_flag` | 3,158 | 0.402% | Urban segment travel time exceeding 30 minutes (extreme delay/incident) |
| `run_time_over_1h_flag` | 105 | 0.013% | Segment duration > 1 hour (vehicle breakdown / depot detention) |
| `extreme_travel_time_flag` | 3,158 | 0.402% | Neutral flag for run times > 30 minutes |
| `segment_gap_after_flag` | 3,295 | 0.419% | Identifies missing intermediate segment sequence in GPS feed |
| `standard_travel_time_eligible` | **765,944** | **97.45%** | **Eligible for passenger travel estimation & standard baseline ML** |

---

## 4. Important Distinction: Data Retained vs. Analytically Eligible

> [!IMPORTANT]
> **Data Retained (100.0%)**: All 785,976 records remain intact in `segment_level_clean.csv`. No rows were deleted. 
> This ensures that operator analysis, delay forensics, and fleet dispatch investigations have complete access to the raw evidence.

> 
> **Data Eligible for Standard Travel-Time Analysis (97.45%)**: 765,944 records are tagged with `standard_travel_time_eligible = 1`. 
> Exactly **20,032 records (2.55%)** are marked as ineligible for standard passenger ETA models under the initial rule:
> - **Origin Terminal Layovers (`terminal_dispatch_flag == 1`)**: 19,062 records. (In 100% of these, run time equals dwell time, reflecting pre-departure terminal wait rather than on-road transit).
> - **Zero-Duration Errors (`zero_run_time_flag == 1`)**: 521 records on segments > 1.
> - **Extreme Outliers (`run_time > 1800s`)**: 449 records on segments > 1 (excluding those already captured by segment 1).
> 
> Marking records as ineligible is **NOT** an assertion that they are invalid or corrupted; it isolates non-representative transit phenomena (terminal dispatch waits and vehicle breakdowns) from customer-facing travel-time estimation.

---

## 5. Route Breakdown in Clean Dataset

| Route Short Name | Total Records | Standard Eligible Records | Ineligible Records | Share of Eligible Data |
| :--- | :--- | :--- | :--- | :--- |
| **Route 46** | 335,078 | 327,117 (97.62%) | 7,961 (2.38%) | 42.71% |
| **Route 10** | 243,243 | 236,468 (97.21%) | 6,775 (2.79%) | 30.87% |
| **Route 12** | 207,655 | 202,359 (97.45%) | 5,296 (2.55%) | 26.42% |

---

## 6. Verification Checklist

- [x] Source row count: 785,976
- [x] Clean dataset row count: 785,976 (0 rows deleted)
- [x] 0 unmapped trips or routes
- [x] 0 missing values across all 33 columns
- [x] 0 duplicate `(trip_id, segment)` pairs
- [x] Deterministic sorting by `(trip_id, segment, start_time)`
- [x] 100% topological continuity on consecutive segment transitions
- [x] Original Data SHA-256 cryptographic hashes verified unchanged
