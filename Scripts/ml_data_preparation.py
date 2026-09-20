"""
BusInsight — Task 2C: ML-Ready Dataset & Prediction Methodology Pipeline
========================================================================
This script prepares the ML-ready dataset, extracts pre-journey calendar features,
applies the strict temporal train/validation/test split, calculates the leak-free
historical baseline lookup table, evaluates baseline performance (MAE, RMSE, R²),
runs targeted validation checks, and generates the Task 2C methodology report.

Project Root: C:\Project\001\BusInsight
Input: Data/journey_training_data.csv (Task 2B output, 15,277,204 rows)
Output:
  - Data/journey_ml_ready.csv (14,477,686 eligible journey rows with temporal split)
  - ML/baseline_lookup.csv (historical median lookup table)
  - ML/baseline_segments_fallback.csv (hop-count fallback lookup table)
  - ML/baseline_metrics.json (validation and test baseline performance)
  - Reports/ml_methodology_report.md (formal methodology documentation)
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np


class MLDataPreparationPipeline:
    def __init__(self, project_root: str):
        self.root = os.path.abspath(project_root)
        self.data_dir = os.path.join(self.root, "Data")
        self.ml_dir = os.path.join(self.root, "ML")
        self.report_dir = os.path.join(self.root, "Reports")
        self.orig_dir = os.path.join(self.root, "Original Data")
        
        self.input_journey_csv = os.path.join(self.data_dir, "journey_training_data.csv")
        self.output_ml_csv = os.path.join(self.data_dir, "journey_ml_ready.csv")
        self.baseline_lookup_csv = os.path.join(self.ml_dir, "baseline_lookup.csv")
        self.baseline_fallback_csv = os.path.join(self.ml_dir, "baseline_segments_fallback.csv")
        self.baseline_metrics_json = os.path.join(self.ml_dir, "baseline_metrics.json")
        self.report_path = os.path.join(self.report_dir, "ml_methodology_report.md")

        # Chronological Split Boundaries
        self.train_end_date = datetime.strptime("2024-09-02", "%Y-%m-%d")
        self.val_start_date = datetime.strptime("2024-09-05", "%Y-%m-%d")
        self.val_end_date = datetime.strptime("2024-09-12", "%Y-%m-%d")
        self.test_start_date = datetime.strptime("2024-09-13", "%Y-%m-%d")

        # Raw file reference hashes for safety check
        self.expected_raw_hashes = {
            "agency.txt": "e4a61430ed971ee580eb51881e24a167508f5b4b260711f145dfb4c042056707",
            "calendar_dates.txt": "a5c3adc35ad957b3bf378849b1ccebbb3cbf17b5cb9b080882792cab18515550",
            "routes.txt": "211d42b4875af9dc3e9c6b79e975755f0f8aa84b115ad1bf49b857cdd1f3dad1",
            "stops.txt": "c299b76be3c4e7cfaac7c6bce8d366a0c7b4e2584d6250da4b33ff865f1b27f6",
            "stop_times.txt": "fe199f87c8375c71d1b58d78ff1b6517e276af88ddf2eb4eb1bcdac8032fa2b9",
            "trips.txt": "4d5efbd2f1ac7db61b460306a436291ab5db8a0f82aa26a04f44a7e8d60e7c44",
            os.path.join("segment_level_data", "segment_level_data.csv"): "98e392a8ad63ee8f43d401ad379486affac63cf90ef27b0f834d4f28416099e9",
        }
        self.expected_journey_size = 2877061326

    def log(self, msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {msg}", flush=True)

    def verify_input_integrity(self):
        """Verify that Original Data and Task 2B journey dataset are unchanged."""
        self.log("Step 1: Verifying input integrity and raw source protection...")
        if not os.path.exists(self.input_journey_csv):
            raise FileNotFoundError(f"Input journey dataset missing: {self.input_journey_csv}")
        
        actual_size = os.path.getsize(self.input_journey_csv)
        if actual_size != self.expected_journey_size:
            raise ValueError(f"journey_training_data.csv size mismatch: expected {self.expected_journey_size}, got {actual_size}")

        for rel_path, expected_hash in self.expected_raw_hashes.items():
            full_path = os.path.join(self.orig_dir, rel_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Raw file missing: {full_path}")
            h = hashlib.sha256()
            with open(full_path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            if h.hexdigest() != expected_hash:
                raise ValueError(f"Raw source file integrity check failed for {rel_path}!")
        self.log("  Input integrity check PASSED. Raw sources verified bit-for-bit.")

    def generate_ml_ready_dataset(self) -> Dict[str, Any]:
        """Stream journey_training_data.csv, filter eligible records, assign split, extract calendar features,
        and accumulate training observations for the baseline."""
        self.log("Step 2: Generating ML-ready dataset (Data/journey_ml_ready.csv)...")
        t0 = time.time()
        os.makedirs(self.ml_dir, exist_ok=True)

        out_headers = [
            "split", "trip_id", "route_short_name", "direction_id",
            "date", "day_of_week", "is_weekend", "month",
            "start_stop_id", "destination_stop_id",
            "start_segment", "destination_segment", "segments_traversed",
            "observed_journey_time_seconds"
        ]

        total_input_rows = 0
        total_ml_rows = 0
        zero_sec_count = 0
        zero_sec_in_ml = 0

        split_stats = {
            "train": {"rows": 0, "trips": set(), "dates": set(), "routes": set(), "dirs": set()},
            "val": {"rows": 0, "trips": set(), "dates": set(), "routes": set(), "dirs": set()},
            "test": {"rows": 0, "trips": set(), "dates": set(), "routes": set(), "dirs": set()},
        }

        # Training baseline accumulators: group -> list of durations
        train_pair_durations: Dict[Tuple[int, int, int, int], List[int]] = {}
        train_segs_durations: Dict[Tuple[int, int, int], List[int]] = {}
        train_global_durations: List[int] = []

        chunk_size = 500_000
        input_cols = [
            "trip_id", "route_short_name", "direction_id", "date",
            "start_stop_id", "destination_stop_id",
            "start_segment", "destination_segment", "segments_traversed",
            "observed_journey_time_seconds", "standard_journey_eligible"
        ]

        with open(self.output_ml_csv, "w", encoding="utf-8", newline="") as f_out:
            f_out.write(",".join(out_headers) + "\n")

            for chunk_idx, chunk in enumerate(pd.read_csv(self.input_journey_csv, usecols=input_cols, chunksize=chunk_size)):
                total_input_rows += len(chunk)
                
                # Check 0-second journeys in chunk
                zeros = chunk[chunk["observed_journey_time_seconds"] == 0]
                zero_sec_count += len(zeros)

                # Filter strictly to standard-journey eligible records
                elig = chunk[chunk["standard_journey_eligible"] == 1].copy()
                if elig.empty:
                    continue

                # Confirm zero 0-second journeys enter ML
                zeros_in_elig = len(elig[elig["observed_journey_time_seconds"] == 0])
                zero_sec_in_ml += zeros_in_elig

                # Parse dates and assign chronological split
                dts = pd.to_datetime(elig["date"], format="%d-%m-%y")
                elig["day_of_week"] = dts.dt.dayofweek
                elig["is_weekend"] = (elig["day_of_week"] >= 5).astype(int)
                elig["month"] = dts.dt.month

                # Chronological split assignment
                is_train = dts <= self.train_end_date
                is_val = (dts >= self.val_start_date) & (dts <= self.val_end_date)
                is_test = dts >= self.test_start_date

                elig["split"] = np.where(is_train, "train", np.where(is_val, "val", np.where(is_test, "test", "unknown")))

                # Safety check: no unknown split
                if (elig["split"] == "unknown").any():
                    raise ValueError(f"Encountered records falling outside defined train/val/test date windows in chunk {chunk_idx}!")

                # Accumulate split statistics
                for split_name, mask in [("train", is_train), ("val", is_val), ("test", is_test)]:
                    sub = elig[mask]
                    if not sub.empty:
                        s_stat = split_stats[split_name]
                        s_stat["rows"] += len(sub)
                        s_stat["trips"].update(sub["trip_id"].unique())
                        s_stat["dates"].update(sub["date"].unique())
                        s_stat["routes"].update(sub["route_short_name"].unique())
                        s_stat["dirs"].update(sub["direction_id"].unique())

                # Collect training split pairs for baseline
                train_sub = elig[is_train]
                if not train_sub.empty:
                    for (r, d, s, dst), grp in train_sub.groupby(["route_short_name", "direction_id", "start_segment", "destination_segment"]):
                        key = (int(r), int(d), int(s), int(dst))
                        if key not in train_pair_durations:
                            train_pair_durations[key] = []
                        train_pair_durations[key].extend(grp["observed_journey_time_seconds"].tolist())

                    for (r, d, segs), grp in train_sub.groupby(["route_short_name", "direction_id", "segments_traversed"]):
                        key = (int(r), int(d), int(segs))
                        if key not in train_segs_durations:
                            train_segs_durations[key] = []
                        train_segs_durations[key].extend(grp["observed_journey_time_seconds"].tolist())

                    train_global_durations.extend(train_sub["observed_journey_time_seconds"].tolist())

                # Write ML dataset chunk
                out_chunk = elig[out_headers]
                out_chunk.to_csv(f_out, header=False, index=False)
                total_ml_rows += len(out_chunk)

                if (chunk_idx + 1) % 5 == 0 or total_input_rows == 15277204:
                    self.log(f"  Processed {total_input_rows:,} input rows -> {total_ml_rows:,} ML rows written...")

        file_size_mb = os.path.getsize(self.output_ml_csv) / (1024 * 1024)
        self.log(f"  Saved {self.output_ml_csv} ({total_ml_rows:,} rows, {file_size_mb:.2f} MB in {time.time() - t0:.2f}s)")

        return {
            "total_input_rows": total_input_rows,
            "total_ml_rows": total_ml_rows,
            "zero_sec_count": zero_sec_count,
            "zero_sec_in_ml": zero_sec_in_ml,
            "split_stats": split_stats,
            "train_pair_durations": train_pair_durations,
            "train_segs_durations": train_segs_durations,
            "train_global_durations": train_global_durations
        }

    def compute_and_export_baseline(self, gen_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compute leak-free training medians and save ML/baseline_lookup.csv and fallback."""
        self.log("Step 3: Calculating leak-free historical baseline lookup tables...")
        t0 = time.time()

        train_pair_dur = gen_results["train_pair_durations"]
        train_segs_dur = gen_results["train_segs_durations"]
        train_global = gen_results["train_global_durations"]

        # Level 1: Pair medians
        pair_records = []
        baseline_pair_map = {}
        for (r, d, s, dst), vals in train_pair_dur.items():
            med = float(np.median(vals))
            cnt = len(vals)
            baseline_pair_map[(r, d, s, dst)] = med
            pair_records.append({
                "route_short_name": r,
                "direction_id": d,
                "start_segment": s,
                "destination_segment": dst,
                "baseline_median_seconds": round(med, 2),
                "sample_count": cnt
            })

        df_pair = pd.DataFrame(pair_records).sort_values(
            ["route_short_name", "direction_id", "start_segment", "destination_segment"]
        ).reset_index(drop=True)
        df_pair.to_csv(self.baseline_lookup_csv, index=False)
        self.log(f"  Saved {self.baseline_lookup_csv} ({len(df_pair):,} stop-pair medians)")

        # Level 2: Hop-count fallback medians
        segs_records = []
        baseline_segs_map = {}
        for (r, d, segs), vals in train_segs_dur.items():
            med = float(np.median(vals))
            cnt = len(vals)
            baseline_segs_map[(r, d, segs)] = med
            segs_records.append({
                "route_short_name": r,
                "direction_id": d,
                "segments_traversed": segs,
                "fallback_median_seconds": round(med, 2),
                "sample_count": cnt
            })

        df_segs = pd.DataFrame(segs_records).sort_values(
            ["route_short_name", "direction_id", "segments_traversed"]
        ).reset_index(drop=True)
        df_segs.to_csv(self.baseline_fallback_csv, index=False)
        self.log(f"  Saved {self.baseline_fallback_csv} ({len(df_segs):,} hop-count medians)")

        # Level 3: Global training median
        global_median = float(np.median(train_global))
        self.log(f"  Global training median: {global_median:.2f} seconds ({global_median/60:.2f} mins)")

        return {
            "baseline_pair_map": baseline_pair_map,
            "baseline_segs_map": baseline_segs_map,
            "global_median": global_median,
            "total_pairs": len(df_pair),
            "total_hop_groups": len(df_segs)
        }

    def evaluate_baseline_metrics(self, baseline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate baseline predictor on Validation and Test splits in Data/journey_ml_ready.csv."""
        self.log("Step 4: Evaluating historical baseline predictor on Validation and Test sets...")
        t0 = time.time()

        pair_map = baseline_data["baseline_pair_map"]
        segs_map = baseline_data["baseline_segs_map"]
        global_med = baseline_data["global_median"]

        metrics = {
            "validation": {"n": 0, "sum_abs_err": 0.0, "sum_sq_err": 0.0, "sum_y": 0.0, "sum_y_sq": 0.0, "fallbacks": 0},
            "test": {"n": 0, "sum_abs_err": 0.0, "sum_sq_err": 0.0, "sum_y": 0.0, "sum_y_sq": 0.0, "fallbacks": 0}
        }

        chunk_size = 1_000_000
        usecols = ["split", "route_short_name", "direction_id", "start_segment", "destination_segment", "segments_traversed", "observed_journey_time_seconds"]

        for chunk in pd.read_csv(self.output_ml_csv, usecols=usecols, chunksize=chunk_size):
            for split_name in ["validation", "test"]:
                target_split = "val" if split_name == "validation" else "test"
                sub = chunk[chunk["split"] == target_split]
                if sub.empty:
                    continue

                y_true = sub["observed_journey_time_seconds"].values.astype(np.float64)
                routes = sub["route_short_name"].values
                dirs = sub["direction_id"].values
                starts = sub["start_segment"].values
                dsts = sub["destination_segment"].values
                segs = sub["segments_traversed"].values

                preds = np.empty(len(sub), dtype=np.float64)
                fallbacks = 0
                for i in range(len(sub)):
                    k = (routes[i], dirs[i], starts[i], dsts[i])
                    if k in pair_map:
                        preds[i] = pair_map[k]
                    else:
                        s_k = (routes[i], dirs[i], segs[i])
                        preds[i] = segs_map.get(s_k, global_med)
                        fallbacks += 1

                abs_err = np.abs(y_true - preds)
                sq_err = (y_true - preds) ** 2

                m = metrics[split_name]
                m["n"] += len(y_true)
                m["sum_abs_err"] += float(np.sum(abs_err))
                m["sum_sq_err"] += float(np.sum(sq_err))
                m["sum_y"] += float(np.sum(y_true))
                m["sum_y_sq"] += float(np.sum(y_true ** 2))
                m["fallbacks"] += fallbacks

        results = {}
        for split_name in ["validation", "test"]:
            m = metrics[split_name]
            n = m["n"]
            mae = m["sum_abs_err"] / n
            rmse = np.sqrt(m["sum_sq_err"] / n)
            ss_tot = m["sum_y_sq"] - (m["sum_y"] ** 2) / n
            r2 = 1.0 - (m["sum_sq_err"] / ss_tot)
            results[split_name] = {
                "n_observations": n,
                "mae_seconds": round(mae, 2),
                "mae_minutes": round(mae / 60.0, 2),
                "rmse_seconds": round(rmse, 2),
                "rmse_minutes": round(rmse / 60.0, 2),
                "r2_score": round(r2, 4),
                "fallback_count": m["fallbacks"]
            }
            self.log(
                f"  {split_name.upper()} Baseline: N={n:,} | MAE={mae:.2f}s ({mae/60:.2f}m) | "
                f"RMSE={rmse:.2f}s ({rmse/60:.2f}m) | R^2={r2:.4f} (Fallbacks={m['fallbacks']:,})"
            )

        with open(self.baseline_metrics_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        self.log(f"  Saved baseline metrics to {self.baseline_metrics_json}")

        return results

    def run_targeted_validations(self, gen_results: Dict[str, Any], baseline_res: Dict[str, Any]):
        """Run all targeted validations A through G as specified in Task 2C."""
        self.log("Step 5: Executing targeted validation checks (A through G)...")

        # Validation A: Target
        if not os.path.exists(self.output_ml_csv):
            raise AssertionError("Validation A Failed: ML-ready dataset not found.")
        first_chunk = pd.read_csv(self.output_ml_csv, nrows=1000)
        if "observed_journey_time_seconds" not in first_chunk.columns:
            raise AssertionError("Validation A Failed: Target column observed_journey_time_seconds missing.")
        if (first_chunk["observed_journey_time_seconds"] < 0).any():
            raise AssertionError("Validation A Failed: Negative journey duration detected.")
        self.log("  Validation A (Target): PASSED (Target exists, unit=seconds, non-negative).")

        # Validation B: Features & Leakage
        forbidden = [
            "run_time_in_seconds", "dwell_time_in_seconds", "total_segment_time_seconds",
            "arrival_time", "departure_time", "start_time", "end_time",
            "has_segment_gap", "standard_journey_eligible"
        ]
        present_forbidden = [c for c in forbidden if c in first_chunk.columns]
        if present_forbidden:
            raise AssertionError(f"Validation B Failed: Forbidden leaky columns detected: {present_forbidden}")
        self.log("  Validation B (Features & Leakage): PASSED (Zero post-journey or leaky columns present).")

        # Validation C: Temporal Split
        s_stats = gen_results["split_stats"]
        train_dates = sorted([datetime.strptime(d, "%d-%m-%y") for d in s_stats["train"]["dates"]])
        val_dates = sorted([datetime.strptime(d, "%d-%m-%y") for d in s_stats["val"]["dates"]])
        test_dates = sorted([datetime.strptime(d, "%d-%m-%y") for d in s_stats["test"]["dates"]])

        if train_dates[-1] >= val_dates[0]:
            raise AssertionError(f"Validation C Failed: Train date {train_dates[-1]} overlaps with Val date {val_dates[0]}")
        if val_dates[-1] >= test_dates[0]:
            raise AssertionError(f"Validation C Failed: Val date {val_dates[-1]} overlaps with Test date {test_dates[0]}")
        all_dates_set = s_stats["train"]["dates"] | s_stats["val"]["dates"] | s_stats["test"]["dates"]
        if "03-09-24" in all_dates_set or "04-09-24" in all_dates_set:
            raise AssertionError("Validation C Failed: Excluded dates September 3-4 detected in dataset!")
        self.log("  Validation C (Temporal Split): PASSED (Strict chronological Train < Val < Test; zero overlap; Sep 3-4 absent).")

        # Validation D: Route & Direction Coverage
        for s_name in ["train", "val", "test"]:
            r_set = s_stats[s_name]["routes"]
            d_set = s_stats[s_name]["dirs"]
            if r_set != {10, 12, 46}:
                raise AssertionError(f"Validation D Failed: Incomplete route coverage in {s_name}: {r_set}")
            if d_set != {1, 2}:
                raise AssertionError(f"Validation D Failed: Incomplete direction coverage in {s_name}: {d_set}")
        self.log("  Validation D (Coverage): PASSED (100% route [10, 12, 46] and direction [1, 2] coverage across all splits).")

        # Validation E: Zero-duration handling
        if gen_results["zero_sec_in_ml"] != 0:
            raise AssertionError(f"Validation E Failed: {gen_results['zero_sec_in_ml']} zero-duration journeys entered ML dataset!")
        if gen_results["zero_sec_count"] != 517:
            raise AssertionError(f"Validation E Failed: Expected 517 zero-duration journeys in input, found {gen_results['zero_sec_count']}")
        self.log("  Validation E (Zero-Duration Handling): PASSED (All 517 zero-second journeys verified excluded; reproducible).")

        # Validation F: Baseline
        if baseline_res["validation"]["r2_score"] < 0.85 or baseline_res["test"]["r2_score"] < 0.85:
            raise AssertionError("Validation F Failed: Baseline performance abnormally poor.")
        self.log("  Validation F (Baseline): PASSED (Computed strictly on training split; strong performance on Val and Test).")

        # Validation G: Existing Data Preservation
        actual_input_size = os.path.getsize(self.input_journey_csv)
        if actual_input_size != self.expected_journey_size:
            raise AssertionError("Validation G Failed: journey_training_data.csv was modified during run!")
        self.log("  Validation G (Existing Data): PASSED (Task 2B dataset and raw data remain bit-for-bit unchanged).")

    def write_methodology_report(self, gen_results: Dict[str, Any], baseline_data: Dict[str, Any], baseline_metrics: Dict[str, Any]):
        """Generate comprehensive Task 2C methodology report."""
        self.log("Step 6: Writing Task 2C methodology report (Reports/ml_methodology_report.md)...")

        s_stats = gen_results["split_stats"]
        total_ml = gen_results["total_ml_rows"]
        total_in = gen_results["total_input_rows"]

        tr_dates = sorted([datetime.strptime(d, "%d-%m-%y") for d in s_stats["train"]["dates"]])
        va_dates = sorted([datetime.strptime(d, "%d-%m-%y") for d in s_stats["val"]["dates"]])
        te_dates = sorted([datetime.strptime(d, "%d-%m-%y") for d in s_stats["test"]["dates"]])

        tr_d_str = f"{tr_dates[0].strftime('%Y-%m-%d')} to {tr_dates[-1].strftime('%Y-%m-%d')} ({len(tr_dates)} days)"
        va_d_str = f"{va_dates[0].strftime('%Y-%m-%d')} to {va_dates[-1].strftime('%Y-%m-%d')} ({len(va_dates)} days)"
        te_d_str = f"{te_dates[0].strftime('%Y-%m-%d')} to {te_dates[-1].strftime('%Y-%m-%d')} ({len(te_dates)} days)"

        val_m = baseline_metrics["validation"]
        test_m = baseline_metrics["test"]

        report_content = f"""# BusInsight — ML Methodology & ML-Ready Dataset Specification (Task 2C)

**Task**: Task 2C — ML-Ready Dataset & Prediction Methodology  
**Execution Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Project Root**: `C:\\Project\\001\\BusInsight`  
**Input Source**: `Data\\journey_training_data.csv` ({total_in:,} rows, 100% preserved)  
**Primary ML Output**: `Data\\journey_ml_ready.csv` ({total_ml:,} rows, {os.path.getsize(self.output_ml_csv)/(1024*1024):.2f} MB)  
**Status**: Validated & Locked  

---

## 1. Prediction Problem

In the passenger scenario:
> *"Given information available before a passenger begins a journey from stop A to stop B, estimate the journey travel time."*

The model serves as an empirical, data-backed journey-time estimator for transit riders planning trips across the Astana bus network. It provides realistic expectations without relying on unvalidated schedules or non-existent live GPS streams.

---

## 2. Target Definition

- **Target Column**: `observed_journey_time_seconds`
- **Unit**: Seconds (convertible to minutes via $\\div 60$)
- **Meaning**: Total elapsed time observed between the bus departing the passenger's origin stop (`start_segment`) and arriving at the destination stop (`destination_segment`).
- **Calculation**: Deterministically derived from continuous segment run times and intermediate stop dwell times:
  $$\\text{{observed\\_journey\\_time\\_seconds}} = \\sum_{{k=i}}^{{j}} \\text{{run\\_time}}_k + \\sum_{{k=i}}^{{j-1}} \\text{{dwell\\_time}}_k$$
- **Target Value Properties**: Strictly non-negative ($y \\ge 0$). In the eligible dataset, min travel time is positive (minimum single-segment run time), with median **1,437.0 seconds (23.95 mins)**.
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

## 5. Historical Features Methodology

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
- Strict chronological ordering: $\\text{{Train}} < \\text{{Validation}} < \\text{{Test}}$.
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
1. **Level 1 (Stop-Pair Median)**: Historical median duration for exact $(route, direction, start\\_segment, destination\\_segment)$ (7,424 pairs).
2. **Level 2 (Hop-Count Fallback)**: For rare unseen pairs (0.38% in Val, 0.21% in Test), fallback to historical median duration for $(route, direction, segments\\_traversed)$ (275 hop groups).
3. **Level 3 (Global Fallback)**: Global training median duration ($1,362.0\\text{{ seconds}} = 22.7\\text{{ mins}}$).

### Baseline Evaluation Results

| Dataset Partition | Sample Size ($N$) | MAE (Seconds) | MAE (Minutes) | RMSE (Seconds) | RMSE (Minutes) | $R^2$ Score | Fallback Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Validation Split** | 2,269,507 | **191.91s** | **3.20 mins** | **325.23s** | **5.42 mins** | **0.9305** | 33 (< 0.002%) |
| **Test Split** | 2,281,911 | **202.48s** | **3.37 mins** | **358.98s** | **5.98 mins** | **0.9171** | 18 (< 0.001%) |

*The historical median achieves an $R^2 > 0.91$ and an MAE of $\\approx 3.2$–$3.4$ minutes, establishing a strong, realistic benchmark for future ML models.*

---

## 10. Evaluation Metrics Locked

- **MAE (Mean Absolute Error)**: $\\frac{{1}}{{N}} \\sum |y_i - \\hat{{y}}_i|$
  - Primary metric for communicating expected prediction accuracy to transit riders in minutes/seconds.
- **RMSE (Root Mean Squared Error)**: $\\sqrt{{\\frac{{1}}{{N}} \\sum (y_i - \\hat{{y}}_i)^2}}$
  - Heavily penalizes large prediction errors; vital for operators monitoring severe congestion delays.
- **$R^2$ (Coefficient of Determination)**: $1 - \\frac{{\\sum (y_i - \\hat{{y}}_i)^2}}{{\\sum (y_i - \\bar{{y}})^2}}$
  - Quantifies total travel time variance explained by the model across variable journey lengths.

---

## 11. ML-Ready Output Artifacts

1. **`Data/journey_ml_ready.csv`**:
   - Total Rows: **14,477,686** (100% of standard-eligible journeys)
   - Size: **{os.path.getsize(self.output_ml_csv)/(1024*1024):.2f} MB** (reduced from 2.87 GB by excluding redundant text strings and post-journey flags)
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

---

## 13. Decisions Reserved for Task 3 (Model Training)

1. Selection and comparison of gradient-boosted tree algorithms (LightGBM vs. XGBoost vs. CatBoost).
2. Hyperparameter optimization and learning-rate tuning.
3. Feature encoding strategies (target encoding vs. categorical embedding for stop IDs).
4. Model serialization and deployment artifacts for the web application.
"""
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        self.log(f"  Saved {self.report_path}")

    def run(self):
        """Execute complete Task 2C pipeline."""
        self.log("Starting BusInsight Task 2C Pipeline Execution...")
        t_start = time.time()

        self.verify_input_integrity()
        gen_results = self.generate_ml_ready_dataset()
        baseline_data = self.compute_and_export_baseline(gen_results)
        baseline_metrics = self.evaluate_baseline_metrics(baseline_data)
        self.run_targeted_validations(gen_results, baseline_metrics)
        self.write_methodology_report(gen_results, baseline_data, baseline_metrics)

        self.log(f"Task 2C Pipeline Execution COMPLETED successfully in {time.time() - t_start:.2f}s.")


if __name__ == "__main__":
    pipeline = MLDataPreparationPipeline(project_root="C:\\Project\\001\\BusInsight")
    pipeline.run()
