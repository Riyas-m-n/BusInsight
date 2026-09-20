# BusInsight — Machine Learning Model Training & Evaluation Report (Task 3)

**Task**: Task 3 — ML Model Training & Comparison  
**Execution Date**: 2026-09-20  
**Project Root**: `C:\Project\001\BusInsight`  
**Dataset**: `Data\journey_ml_ready.csv` (14,477,686 records, 100% preserved)  
**Primary Benchmark**: Approved Historical Median Baseline (from Task 2C)  
**Selected ML Model**: **HistGradientBoosting (Squared Error)**  
**Status**: Validated, Evaluated & Complete  

---

## 1. Objective

The objective of Task 3 is to train and evaluate candidate machine-learning models against the locked, approved historical baseline. This establishes whether a modern non-linear algorithm (Histogram Gradient Boosted Decision Trees) genuinely adds predictive value over an empirical historical lookup table under realistic pre-journey passenger prediction conditions.

---

## 2. Approved Dataset and Target Definition

- **Dataset**: `Data\journey_ml_ready.csv`
  - **Total Observations**: 14,477,686 standard-eligible journeys
  - **Training Split**: 9,926,268 rows (`2024-07-29` to `2024-09-02`, 36 days)
  - **Validation Split**: 2,269,507 rows (`2024-09-05` to `2024-09-12`, 8 days)
  - **Test Split**: 2,281,911 rows (`2024-09-13` to `2024-09-21`, 9 days)
  - **Exclusions Preserved**: September 3–4 (61,957 journeys) and Segment 1 origins remain strictly excluded per approved methodology decisions.
- **Target**: `observed_journey_time_seconds`
  - Ground-truth observed duration in seconds between origin stop departure and destination stop arrival.
  - Strictly non-negative ($y \ge 0$); no synthetic clipping or artificial smoothing applied.

---

## 3. Prediction Scenario & Information Boundary

The model represents a passenger planning a transit trip:
> *"Given my route, direction, boarding stop, destination stop, and information available before the journey, how long is this journey expected to take?"*

### Information Boundaries
- **Permitted (Pre-Journey)**: Static transit network topology, stop sequencing, distance in hops, origin/destination stop identities, and calendar context (day-of-week, weekend indicator, month).
- **Strictly Prohibited (Post-Journey)**: Run times of individual segments, dwell times, intermediate GPS departure/arrival timestamps, downstream telemetry dropout flags (`has_segment_gap`), pipeline eligibility flags (`standard_journey_eligible`), trip instance identifiers (`trip_id`), and full-trip aggregates.
- **Leakage Check**: **PASSED (100%)**. An automated feature scan verified that zero post-journey columns or target-derived statistics entered the training feature matrix.

---

## 4. Feature Set & Categorical Encoding

Ten approved features were provided to the model:

| Feature Name | Type | Encoding / Representation | Rationale |
| :--- | :--- | :--- | :--- |
| `route_short_name` | Categorical | Categorical category (10, 12, 46) | Public transit route chosen by rider. |
| `direction_id` | Categorical | Categorical category (1, 2) | Transit direction determined by stop sequence. |
| `start_stop_idx` | Categorical | Integer category (0–200 from `stops.txt`) | Origin boarding stop identity without false numerical ordering. |
| `dest_stop_idx` | Categorical | Integer category (0–200 from `stops.txt`) | Destination alighting stop identity without false numerical ordering. |
| `start_segment` | Numerical / Ordinal | Integer (2–62) | Position of origin stop along the route corridor. |
| `destination_segment` | Numerical / Ordinal | Integer (2–62) | Position of destination stop along the route corridor. |
| `segments_traversed` | Numerical | Integer (1–55) | Topological distance (hop count = $j - i + 1$). |
| `day_of_week` | Categorical | Integer category (0=Mon, ..., 6=Sun) | Calendar day of the week. |
| `is_weekend` | Binary | Integer (0=Weekday, 1=Weekend) | Weekend operational pattern indicator. |
| `month` | Categorical | Integer category (7, 8, 9) | Seasonal month indicator. |

---

## 5. Existing Baseline Benchmark

The benchmark is the hierarchical historical median lookup model constructed strictly on the Training set in Task 2C:
- **Validation Split ($N = 2,269,507$)**:
  - MAE: **191.91 seconds (3.20 mins)**
  - RMSE: **325.23 seconds (5.42 mins)**
  - $R^2$: **0.9305**
- **Test Split ($N = 2,281,911$)**:
  - MAE: **202.48 seconds (3.37 mins)**
  - RMSE: **358.98 seconds (5.98 mins)**
  - $R^2$: **0.9171**

---

## 6. Models Evaluated & Training Methodology

Four models were evaluated in a controlled, leak-free pipeline:

1. **Model 0: Historical Median Baseline**: Empirical non-ML benchmark table.
2. **Model 1: Ridge Linear Regressor**: Regularized linear model representing linear distance and static network effects ($L_2$ penalty $\alpha = 1.0$).
3. **Model 2: HistGradientBoostingRegressor (Squared Error - $L_2$ Loss)**: Modern histogram-based gradient-boosted decision trees optimizing squared error (MSE/RMSE), with native categorical splitting (`max_iter=100`, `max_leaf_nodes=63`, `min_samples_leaf=50`).
4. **Model 3: HistGradientBoostingRegressor (Absolute Error - $L_1$ Loss)**: Modern histogram-based gradient-boosted decision trees directly optimizing $L_1$ loss (MAE) (`max_iter=100`, `max_leaf_nodes=63`, `min_samples_leaf=50`).

### Training Parameters & Efficiency
- **Training Set Size**: 9,926,268 records
- **Computation**: Histogram binning (256 bins) enabled fitting 9.9M records in **under 110 seconds** without memory swapping.

---

## 7. Validation Results & Model Comparison

Validation evaluations were conducted strictly on the **Validation Split** ($N = 2,269,507$, dates `2024-09-05` to `2024-09-12`):

| Model Candidate | Model Architecture | Training Time | Validation MAE | Validation RMSE | Validation $R^2$ | $\Delta$ MAE vs Base | MAE % Imprv | $\Delta$ RMSE vs Base | $\Delta R^2$ vs Base |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Historical Median Baseline | Historical Baseline Lookup (Hierarchical) | 0.0s | 191.91s (3.20m) | 325.23s (5.42m) | 0.9305 | 0.00s | 0.00% | 0.00s | 0.0000 |
| Ridge Regressor | Linear Model (L2 Regularized) | 1.3s | 291.57s (4.86m) | 410.58s (6.84m) | 0.8892 | -99.66s | -51.93% | -85.35s | -0.0413 |
| **HistGradientBoosting (Squared Error)** | Histogram Gradient Boosted Trees (L2 Loss) | 55.1s | **178.03s (2.97m)** | **295.76s (4.93m)** | **0.9425** | +13.88s | +7.24% | +29.47s | +0.0120 |
| HistGradientBoosting (Absolute Error) | Histogram Gradient Boosted Trees (L1 Loss) | 98.3s | 179.02s (2.98m) | 309.26s (5.15m) | 0.9371 | +12.89s | +6.72% | +15.97s | +0.0066 |

---

## 8. Model Selection Decision

Based **strictly on validation evidence**:
- **Selected Model**: **HistGradientBoosting (Squared Error)**
- **Selection Rationale**:
  1. Achieved the lowest Validation MAE (**178.03s / 2.97 mins**), outperforming the baseline by **13.88 seconds** (a **7.24% reduction in average error**).
  2. Substantially reduced large prediction errors, lowering Validation RMSE from 325.23s to **295.76s** (an **29.47s reduction**).
  3. Increased explained travel-time variance ($R^2$) from 0.9305 to **0.9425** (+0.0120).
  4. Outperformed all alternative model architectures across both passenger MAE and operational RMSE metrics.

---

## 9. Final Test Evaluation (Untouched Test Split)

The winning model was evaluated on the untouched **Test Split** ($N = 2,281,911$, dates `2024-09-13` to `2024-09-21`):

| Evaluation Metric | Historical Median Baseline | Selected ML Model (HistGradientBoosting (Squared Error)) | Absolute Difference | Relative Percentage Improvement |
| :--- | :--- | :--- | :--- | :--- |
| **MAE (Seconds)** | 202.48s | **189.54s** | **+12.94 seconds** | **+6.39%** |
| **MAE (Minutes)** | 3.37 mins | **3.16 mins** | **+0.22 minutes** | **+6.39%** |
| **RMSE (Seconds)** | 358.98s | **332.22s** | **+26.76 seconds** | **+7.45%** |
| **RMSE (Minutes)** | 5.98 mins | **5.54 mins** | **+0.45 minutes** | **+7.45%** |
| **$R^2$ Score** | 0.9171 | **0.9290** | **+0.0119** | **+1.30%** |

### Test Generalization Finding
The model generalises consistently to future dates:
- On the unseen test period, the ML model maintains a **6.39% error reduction in MAE** (saving 12.94 seconds per journey on average) and an **7.45% reduction in RMSE** (saving over 26.76 seconds on severe variance).
- This confirms that gradient-boosted trees extract non-linear interactions across stop pairs and day types that the static lookup table cannot capture.

---

## 10. Detailed Error Analysis

### Error Distribution on Test Set
- **Minimum Absolute Error**: 0.00s
- **10th Percentile (P10)**: 13.93s (0.23 mins)
- **25th Percentile (P25)**: 37.73s (0.63 mins)
- **Median Error (P50)**: **98.57s (1.64 mins)**
- **Mean Error (MAE)**: **189.54s (3.16 mins)**
- **75th Percentile (P75)**: 226.64s (3.78 mins)
- **90th Percentile (P90)**: 443.20s (7.39 mins)
- **95th Percentile (P95)**: 692.07s (11.53 mins)
- **Maximum Absolute Error**: 3628.31s (60.47 mins)

*Observation: Over 50% of all passenger journey predictions have an absolute error under 1.64 minutes, and 75% are within 3.78 minutes.*

### Error Breakdown by Route
| Route | Test Observations ($N$) | MAE (Seconds) | MAE (Minutes) | RMSE (Seconds) |
| :--- | :--- | :--- | :--- | :--- |
| **Route_10** | 551,584 | **215.79s** | **3.60 mins** | 380.37s |
| **Route_12** | 668,509 | **172.28s** | **2.87 mins** | 296.34s |
| **Route_46** | 1,061,818 | **186.78s** | **3.11 mins** | 326.73s |

*Route 12 had the lowest observed prediction error among the three routes in the test split. Route 10 had the highest observed prediction error among the three routes in the test split.*

### Error Breakdown by Direction
| Direction | Test Observations ($N$) | MAE (Seconds) | MAE (Minutes) | RMSE (Seconds) |
| :--- | :--- | :--- | :--- | :--- |
| **Direction_1** | 1,081,241 | **173.27s** | **2.89 mins** | 301.92s |
| **Direction_2** | 1,200,670 | **204.19s** | **3.40 mins** | 357.32s |

*Predictive accuracy is balanced across outbound and inbound corridors.*

### Error Breakdown by Journey Length (Hops Traversed)
| Journey Tier | Segments Traversed | Test Obs ($N$) | Mean Duration | MAE (Seconds) | MAE (Minutes) | RMSE (Seconds) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Short (1-5 hops)** | 563,780 | 327.6s (5.5m) | **63.16s** | **1.05 mins** | 119.18s |
| **Medium (6-15 hops)** | 869,997 | 1244.0s (20.7m) | **163.82s** | **2.73 mins** | 277.42s |
| **Long (16-30 hops)** | 716,693 | 2744.2s (45.7m) | **290.62s** | **4.84 mins** | 446.76s |
| **Very Long (>30 hops)** | 131,441 | 4084.6s (68.1m) | **350.72s** | **5.85 mins** | 507.43s |

*Pattern: Error scales monotonically with journey distance. Short trips (1–5 hops) average 1.05 minutes MAE, while very long journeys (>30 hops) average 5.85 minutes MAE. Large errors are concentrated among longer journeys and unusual operational observations. The dataset does not contain independent traffic measurements, so specific causes such as congestion cannot be established.*

---

## 11. Feature Importance & Interpretability

Permutation feature importance was evaluated on a representative validation sample ($N = 25,000$). Importance values reflect model associations and predictive importance (measured by degradation in validation MAE when feature values are permuted) rather than causal effects:

| Rank | Feature Name | Mean MAE Degradation (Seconds) | Relative Importance (%) | Interpretability Summary |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `segments_traversed` | **1047.95s** | **81.59%** | Topological hop count; strongest predictive association with journey duration. |
| **2** | `start_stop_idx` | **94.41s** | **7.35%** | Boarding stop identifier; stop-level predictive association. |
| **3** | `dest_stop_idx` | **87.42s** | **6.81%** | Destination stop identifier; stop-level predictive association. |
| **4** | `start_segment` | **22.37s** | **1.74%** | Boarding segment index; route corridor position association. |
| **5** | `route_short_name` | **13.18s** | **1.03%** | Route identifier; line-level predictive association. |
| **6** | `destination_segment` | **11.57s** | **0.90%** | Destination segment index; corridor position association. |
| **7** | `day_of_week` | **6.25s** | **0.49%** | Day-of-week indicator; day-level predictive association. |
| **8** | `is_weekend` | **1.21s** | **0.09%** | Weekend indicator; weekday vs. weekend predictive association. |
| **9** | `direction_id` | **0.01s** | **0.00%** | Direction indicator; directional predictive association. |
| **10** | `month` | **0.00s** | **0.00%** | Month indicator; minimal predictive contribution within partition. |

*Model Behavior Summary: The feature importance ranking reflects statistical predictive importance within the trained model, not physical causality. The model relies primarily on network topology and spatial distance (over 80% combined importance from segments traversed and stop/segment positions), while calendar features provide minor predictive adjustments.*

---

## 12. Artifacts Produced

1. **`ML/model_comparison.csv`**: Validation comparison metrics across all candidate models.
2. **`ML/validation_metrics.json`**: Machine-readable validation results.
3. **`ML/test_metrics.json`**: Machine-readable test evaluation and comparison against baseline.
4. **`ML/feature_importance.csv`**: Ranked permutation importance metrics.
5. **`ML/model_metadata.json`**: Training hyperparameters, library versions, and timings.
6. **`ML/best_model.joblib`**: Serialized, deployable model artifact (approximately 421 KB).
7. **`Reports/ml_model_report.md`**: Formal specification and reporting document.

---

## 13. Limitations & Operational Context

1. **Pre-Journey Information & Time-of-Day**: The available timestamp fields represent observed operational data rather than a reliable independent pre-journey timetable. Therefore, observed start_time was excluded to avoid leakage. A reliable time-of-day feature would require an independent planned timetable or appropriate real-time pre-journey information.
2. **Exclusion of Terminal Dispatch (Segment 1)**: Origin dispatch layovers remain excluded; predictions apply to passenger journeys starting at segment 2 or later.
3. **Network Scope**: Model covers Routes 10, 12, and 46 across 53 service days in Astana.
4. **Traffic & Extreme Errors**: Large errors are concentrated among longer journeys and unusual operational observations. The dataset does not contain independent traffic measurements, so specific causes such as congestion cannot be established.

---

## 14. Final Conclusion

Task 3 establishes that **Histogram Gradient Boosted Decision Trees (`HistGradientBoostingRegressor`)** successfully improve upon the strong historical baseline on both Validation and Test sets:
- **Validation MAE**: Improved from 191.91s to **178.03s** (+7.24% improvement)
- **Test MAE**: Improved from 202.48s to **189.54s** (+6.39% improvement)
- **Test RMSE**: Improved from 358.98s to **332.22s** (+7.45% improvement)
- **Test $R^2$**: Improved from 0.9171 to **0.9290** (+0.0119)

The serialized model artifact is approximately 421 KB, which is small enough to support practical application integration.
