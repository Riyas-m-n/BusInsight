# BusInsight — Final Portfolio & Presentation Package

> **Project Title:** BusInsight: Astana Urban Transit Analytics & Travel-Time Intelligence Prototype  
> **Role / Scope:** End-to-End Data Analytics, SQL Engineering, Machine Learning Evaluation, and Product UI  
> **Target Audience:** Technical Recruiters, Hiring Managers, Portfolio Reviewers, Transit Stakeholders

---

## 1. Final Project Story

```
Problem → Data → Data Quality → SQL / EDA → Feature Engineering → Baseline → ML Model → Evaluation → Product Interface → Key Findings → Limitations → Future Scope
```

- **Problem:** Public transit riders experience travel-time uncertainty when planning journeys across urban bus corridors, while transit authorities often lack granular, segment-level variability metrics to target operational improvements.
- **Data:** Utilized GPS-derived automated vehicle location (AVL) stop events and static GTFS feeds from the public bus network in Astana, Kazakhstan across 3 high-volume trunk routes (Routes 10, 12, 46), covering 201 stops, 300 corridor segments, 19,769 vehicle trips, and 55 active dates (July–September 2024).
- **Data Quality:** Conducted a comprehensive audit resolving zero-duration records, validating stop continuity, isolating an anomalous data collection drop on September 3–4, and uncovering that initial terminal dispatch (Segment 1) incorporates substantial layovers and buffer holding rather than ordinary passenger travel.
- **SQL / EDA:** Deployed a lightweight, view-backed DuckDB analytical catalog to compute route-level distributions, directional asymmetry, dwell behaviors, hop-length scaling, and to identify 62 High-Variability corridor segments ($N \ge 500, \text{IQR} \ge 68\text{s}$).
- **Feature Engineering:** Constructed 15,277,204 stop-to-stop journey observations. Formulated 10 strictly pre-journey features (route, direction, origin/destination stop IDs, segment positions, hop count, day of week, weekend, month) with zero post-journey data leakage.
- **Baseline:** Established a robust empirical baseline using training-set segment-pair historical medians with hop-count fallbacks ($R^2 = 0.9171$, MAE = 3.37 min).
- **ML Model:** Trained and tuned a `HistGradientBoostingRegressor` (squared error / L2 loss) across 9.93M training records.
- **Evaluation:** Evaluated on 2,281,911 out-of-time test observations. The model achieved an MAE of 189.54 seconds (3.16 min) and $R^2$ of 0.9290, yielding a 12.94-second (6.39%) MAE reduction over the baseline.
- **Product Interface:** Built a modular, dual-persona Streamlit web application featuring a Passenger Journey Estimator and an Operator Corridor Intelligence Dashboard.
- **Key Findings:** Discovered consistent directional travel-time differentials across all three routes (Direction 2 longer by 1.34 to 2.36 min; Route 12 differential: 1.34 min / 80.0s between 21.97 min Inbound and 20.63 min Outbound), verified that travel time scales with hop length, and empirically mapped the top high-variability segments.
- **Limitations:** Historical predictive prototype based on observed telematics; does not include live GPS feeds, real-time traffic sensors, or passenger ridership counts.
- **Future Scope:** Potential integration with real-time GTFS-RT feeds, automated passenger counter (APC) data, and signal priority APIs.

---

## 2. Final Project Summary

### Overview
**BusInsight** is an end-to-end transit data analytics and predictive prototype that transforms 15.2 million historical GPS-derived bus journey observations in Astana, Kazakhstan into usable intelligence for transit riders and network operators. The system integrates automated vehicle location (AVL) data with GTFS static specifications to evaluate corridor travel-time distributions and deliver pre-journey travel-time estimates.

### Technical Stack
- **Languages & Frameworks:** Python 3.10, Streamlit, SQL (DuckDB)
- **Data Science & ML:** Scikit-Learn (`HistGradientBoostingRegressor`, `Ridge`), Pandas, NumPy, Matplotlib, Seaborn
- **Data Formats & Infrastructure:** GTFS static text files, DuckDB view-backed catalog, serialized model artifacts (`joblib`)

### Key Results
- **Empirical Baseline:** Historical median lookup achieved $R^2 = 0.9171$ and $\text{MAE} = 202.48\text{s}$ (3.37 min).
- **Machine Learning Model:** Gradient-boosted regression achieved $R^2 = 0.9290$ and $\text{MAE} = 189.54\text{s}$ (3.16 min) on 2.28M out-of-time test samples.
- **Improvement:** 12.94-second (6.39%) MAE improvement and 26.76-second (7.45%) RMSE improvement.
- **Operational Findings:** Quantified Route 12's 1.34 min (80.0s) directional asymmetry (with Direction 2 longer across all corridors) and isolated 62 high-variability corridor segments.

---

## 3. Verified Project Facts Reference Sheet

| Parameter | Verified Project Fact |
| :--- | :--- |
| **Location** | Astana, Kazakhstan public bus network |
| **Observation Period** | July 29, 2024 – September 21, 2024 (55 active operating dates) |
| **Monitored Routes** | 3 trunk routes: Route 10, Route 12, Route 46 |
| **Corridor Dimensions** | 2 directions, 201 unique physical stops, 300 physical corridor segments |
| **Operational Telemetry** | 785,976 segment records across 19,769 vehicle trips |
| **Constructed Journeys** | 15,277,204 stop-to-stop journey observations |
| **Target Variable** | `observed_journey_time_seconds` (total elapsed duration from origin to destination) |
| **Data Quality Results** | 0 missing values, 0 exact duplicates, 0 trip/segment duplicates, stop continuity validated |
| **Segment 1 Governance** | Terminal dispatch layovers isolated (median dwell 506–546s); excluded from passenger starts |
| **Sep 3–4 Governance** | Collection outage retained in analytical logs, excluded from ML training partitions |
| **Data Partitions** | Chronological: Train (9.93M / 68.6%), Validation (2.27M / 15.7%), Test (2.28M / 15.8%) |
| **ML Dataset Size** | 14,477,686 rows across 10 strictly pre-journey features |
| **Baseline Architecture** | Exact segment-pair median lookup with hop-count fallback |
| **Baseline Test Metrics** | MAE: 202.48s (3.37 min) \| RMSE: 358.98s (5.98 min) \| $R^2$: 0.9171 |
| **Selected Model** | `HistGradientBoostingRegressor` (loss: squared error / L2) |
| **Model Test Metrics** | MAE: 189.54s (3.16 min) \| RMSE: 332.22s (5.54 min) \| $R^2$: 0.9290 |
| **Model Performance Delta** | MAE: -12.94s (-6.39%) \| RMSE: -26.76s (-7.45%) \| $R^2$: +0.0119 |
| **Top Predictive Feature** | `segments_traversed` (81.59% of permutation feature importance) |
| **Directional Asymmetry** | Direction 2 longer across all routes by 1.34–2.36 min (Route 12: 21.97 min Dir 2 vs 20.63 min Dir 1 — 1.34 min differential) |
| **High-Variability Segments** | 62 corridor segments identified ($N \ge 500, \text{IQR} \ge 68\text{s}$) |
| **Passenger Dwell Dwell** | Standard stops median dwell: 22.0–27.0s (20–23% of total segment time) |

---

## 4. Product & Analytical Interpretation

### The "Baseline vs. ML Complexity" Trade-Off
A core product takeaway from BusInsight is understanding the cost-benefit trade-off between algorithmic complexity and empirical baselines:

1. **Strong Historical Baseline:** Public bus travel duration is strongly dictated by network topology and physical corridor distance. Because the historical-median lookup already captures segment-pair geometry, it explained over 91.7% of travel-time variance ($R^2 = 0.9171$) with an MAE of 3.37 minutes.
2. **Modest ML Gains:** The machine-learning model delivered a measurable error reduction of 12.94 seconds (6.39%), bringing test MAE down to 3.16 minutes ($R^2 = 0.9290$) by capturing non-linear stop interactions and temporal patterns.
3. **Product Evaluation Question:** In an engineering environment, a critical discussion is whether a ~13-second accuracy improvement justifies deploying and maintaining a machine learning pipeline, or whether an empirical lookup table is sufficient for initial passenger-facing prototypes.

---

## 5. Portfolio Project Highlights

- **Rigorous Data Governance:** Addressed terminal layover distortions (Segment 1) and tracking drops (Sep 3–4) methodologically rather than blindly training models on raw telemetry.
- **Strict Pre-Journey Guardrails:** Engineered 10 features strictly knowable prior to departure, preventing data leakage.
- **Chronological Split Discipline:** Enforced chronological time-series splitting to replicate real-world prospective deployment conditions.
- **Empirical Baseline-First Methodology:** Established a competitive historical median baseline before experimenting with tree-based algorithms.
- **Dual-Persona Product Architecture:** Translated backend analytics into intuitive user interfaces for both passengers and operational planners.
- **Transparent Communication:** Explicitly separated empirical measurements from unsupported causal claims.

---

## 6. Portfolio Project Descriptions

### A. One-Line Project Description
> *An end-to-end transit analytics and machine-learning prototype analyzing 15.2M bus journey observations in Astana to estimate pre-journey travel times and diagnose corridor variability.*

### B. Short 2–3 Sentence Description
> *BusInsight is an urban transit analytics platform built on GPS-derived AVL telemetry and GTFS feeds from Astana, Kazakhstan. The system evaluates 15.2 million journey observations across three trunk routes, delivering a pre-journey travel-time estimator for riders and an operational intelligence dashboard for transit planners. Using a gradient-boosted regression model with strict pre-journey features, it reduces travel-time prediction error by 6.4% over a strong historical median baseline.*

### C. Detailed Portfolio Description
> *BusInsight translates over 785,000 GPS segment records and 15.2 million constructed stop-to-stop journey observations into actionable transit intelligence. Built on Python, DuckDB, Scikit-Learn, and Streamlit, the project addresses travel-time uncertainty across three major bus corridors in Astana, Kazakhstan.*
>
> *The technical pipeline includes a comprehensive data quality audit that resolved terminal dispatch anomalies and tracking outages, an analytical SQL layer quantifying directional travel-time imbalances and identifying 62 high-variability segments, and a machine learning workflow evaluated under strict chronological splits. An out-of-time test evaluation across 2.28 million observations demonstrated that a HistGradientBoosting model achieved an MAE of 3.16 minutes (a 6.39% improvement over an empirical baseline).*
>
> *The resulting web application bridges data science and product design by providing passengers with pre-journey travel-time estimates and giving transit operators granular corridor performance metrics.*

### D. Resume / CV Bullet Points
- **Engineered an end-to-end transit analytics pipeline** analyzing 785K+ GPS segment records and 15.2M journey observations across Astana’s bus network using Python, DuckDB, and Scikit-Learn.
- **Audited and cleansed complex AVL/GTFS telemetry**, designing methodological solutions for terminal dispatch layovers and isolating sensor anomalies under strict data governance standards.
- **Built an analytical SQL/EDA layer** uncovering operational insights, including a 1.34-minute directional travel-time differential on Route 12 and 62 high-variability corridor segments ($\text{IQR} \ge 68\text{s}$).
- **Developed a pre-journey regression model** (`HistGradientBoostingRegressor`) utilizing 10 zero-leakage features, achieving an MAE of 3.16 minutes and reducing prediction error by 6.39% over a strong historical baseline on 2.28M test samples.
- **Designed a dual-persona Streamlit web application** providing riders with pre-journey travel-time estimates and operators with interactive corridor performance dashboards.

---

## 7. Screenshot & Demonstration Plan

| # | Screen / View | What Must Be Visible | Why It Matters | Suggested Caption |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Application Landing / Header** | Navigation sidebar, system metadata badge (3 routes, 15.28M obs), historical notice banner. | Establishes project identity, scope, and prototype framing. | *Figure 1: BusInsight main interface and transit network scope.* |
| **2** | **Passenger Route & Stop Selectors** | Cascading dropdowns (Route 10, Direction 1, Boarding stop Seg #2, Downstream destination). | Demonstrates dependency logic and Segment 1 exclusion. | *Figure 2: Dependent stop selection with Segment 1 terminal dispatch exclusion.* |
| **3** | **Passenger Prediction Results** | Travel-time card (e.g. 18.4 min), Model Test Error (MAE 3.2 min), Historical Median delta, hop count. | Shows model inference, baseline comparison, and clear error metrics. | *Figure 3: Pre-journey travel-time estimation with historical baseline comparison.* |
| **4** | **Operator Route Overview** | Network summary cards and comparison table across Routes 10, 12, and 46. | Provides macro-level transit corridor operational metrics. | *Figure 4: Corridor-level performance overview and summary statistics.* |
| **5** | **Directional Asymmetry Chart** | Bar chart comparing Outbound vs Inbound journey times (highlighting Route 12's 1.34 min spread and Direction 2 longer across all corridors). | Visualizes structural transit imbalance between travel directions. | *Figure 5: Directional travel-time asymmetry across monitored trunk routes.* |
| **6** | **High-Variability Segments Table** | Filterable table showing the 62 segments with IQR $\ge 68\text{s}$, sample sizes, and CV. | Demonstrates actionable insights for transit dispatchers. | *Figure 6: Granular corridor segment variability inventory ($N \ge 500, \text{IQR} \ge 68\text{s}$).* |
| **7** | **ML Benchmark & Feature Importance** | Validation benchmark table, test evaluation metrics, and permutation importance bar chart. | Validates ML methodology, baseline comparison, and model interpretability. | *Figure 7: Out-of-time test set evaluation and permutation feature importance.* |

---

## 8. 15-Slide Presentation Structure

- **Slide 1: Title & Executive Summary**
  - *Title:* BusInsight: Urban Bus Travel-Time Intelligence Prototype
  - *Core Message:* Translating 15.2M GPS-derived journey observations into passenger estimations and transit operational intelligence.
- **Slide 2: Problem Statement & Motivation**
  - *Title:* The Urban Transit Predictability Challenge
  - *Core Message:* Riders experience journey-time uncertainty, while operators lack granular segment-level variability metrics.
- **Slide 3: Product Concept & Personas**
  - *Title:* Dual-Persona Architecture: Riders & Planners
  - *Core Message:* Passenger estimator provides pre-journey expectations; Operator dashboard delivers corridor diagnostics.
- **Slide 4: Network & Data Scope**
  - *Title:* Astana Public Bus Telemetry
  - *Core Message:* 3 trunk routes, 201 stops, 300 segments, 19,769 trips, 785K segment records, July 29 – September 21, 2024.
- **Slide 5: Data Quality & Governance**
  - *Title:* Data Quality: Beyond Clean Data to Operational Understanding
  - *Core Message:* Audited 0 missing/duplicates; isolated terminal dispatch (Segment 1) and September 3–4 collection outage.
- **Slide 6: Journey Construction & Target**
  - *Title:* Constructing 15.2M Journey Observations
  - *Core Message:* Built stop-to-stop journey pairs from vehicle trajectory runs; defined target as `observed_journey_time_seconds`.
- **Slide 7: Directional Asymmetry Analysis**
  - *Title:* Corridor Findings: Directional Asymmetry
  - *Core Message:* Direction 2 is longer across all three routes by 1.34 to 2.36 min (Route 12: 21.97 min Inbound vs 20.63 min Outbound — 1.34 min / 80.0s differential).
- **Slide 8: Segment Variability Hotspots**
  - *Title:* Pinpointing 62 High-Variability Corridor Segments
  - *Core Message:* Empirically identified segments with $\text{IQR} \ge 68\text{s}$ ($N \ge 500$) where segment times fluctuate substantially.
- **Slide 9: Dwell Dynamics & Dispatch**
  - *Title:* Dwell Dynamics: Routine Stops vs. Terminal Dispatch
  - *Core Message:* Standard passenger stops exhibit 22–27s median dwell; Segment 1 incorporates 500s+ layover buffering.
- **Slide 10: Baseline Approach**
  - *Title:* Establishing a Robust Empirical Baseline
  - *Core Message:* Training-set segment-pair median lookup established a competitive benchmark ($R^2 = 0.9171$, MAE = 3.37 min).
- **Slide 11: Machine Learning Architecture**
  - *Title:* Gradient-Boosted Travel-Time Estimation
  - *Core Message:* Trained `HistGradientBoostingRegressor` using 10 strictly pre-journey features under chronological splitting.
- **Slide 12: Model Evaluation & Out-of-Time Testing**
  - *Title:* Model Evaluation on 2.28M Test Observations
  - *Core Message:* Model achieved MAE of 3.16 min ($R^2 = 0.9290$), delivering a 6.39% error reduction over baseline.
- **Slide 13: Feature Importance & Interpretability**
  - *Title:* Model Association: What Drives Travel Time?
  - *Core Message:* Hop count accounts for 81.59% of permutation importance; stop indices provide localized spatial corrections.
- **Slide 14: Application Demonstration**
  - *Title:* BusInsight Interactive Web Application
  - *Core Message:* Built modular Streamlit interface integrating real model inference, baseline comparisons, and corridor analytics.
- **Slide 15: Limitations, Product Trade-Offs & Conclusion**
  - *Title:* Key Takeaways & Scope Boundaries
  - *Core Message:* Historical predictive prototype; discussed whether modest ML gain justifies pipeline overhead vs baseline lookup.

---

## 9. Presentation Speaker Notes (10–15 Minute Script)

### Slide 1: Title & Executive Summary (45s)
> *"Hello everyone. Today I'm presenting BusInsight, an end-to-end urban transit analytics and predictive travel-time prototype. Using automated vehicle location telemetry from Astana, Kazakhstan, BusInsight analyzes over 15.2 million stop-to-stop journey observations. The goal of this project is two-fold: first, to provide riders with pre-journey travel-time estimates, and second, to equip transit planners with empirical corridor performance diagnostics. Across the next ten minutes, I'll walk you through our data governance decisions, our analytical findings, our machine learning evaluation, and the resulting interactive application."*
- **Terms:** Automated Vehicle Location (AVL), GTFS, Pre-Journey Estimation.
- **Avoid:** Do not claim this is a live tracking or real-time production system.

### Slide 2: Problem Statement & Motivation (45s)
> *"In urban public transit, unpredictability creates friction. For riders, timetable schedules often diverge from physical road operations, leaving passengers uncertain about actual journey durations before they board. Meanwhile, transit authorities and dispatchers often lack segment-by-segment empirical variability data, making it difficult to pinpoint where along a corridor travel times fluctuate most. BusInsight addresses both challenges by turning raw operational telematics into transparent, data-driven intelligence."*
- **Terms:** Travel-time variability, schedule adherence vs observed operations.
- **Avoid:** Do not assume ridership complaints; focus on data-driven predictability.

### Slide 3: Product Concept & Personas (45s)
> *"To solve this, we designed BusInsight around two distinct user personas. For the passenger persona, the priority is pre-journey estimation: given a route, boarding stop, destination, and travel date, what is the expected duration? Crucially, this must rely strictly on pre-journey information with zero post-journey data leakage. For the operator persona, the priority is network diagnostics: identifying directional travel-time imbalances, isolating high-variability segments, and analyzing dwell behaviors across the network."*
- **Terms:** User Personas, Pre-Journey Inputs, Data Leakage.
- **Avoid:** Do not introduce live vehicle dispatching or passenger ticketing.

### Slide 4: Network & Data Scope (45s)
> *"Our dataset covers the public bus network in Astana across three major trunk corridors: Route 10, Route 12, and Route 46, observed between July 29 and September 21, 2024. The network consists of 201 physical stops and 300 corridor segments. In total, we analyzed 785,976 segment records across 19,769 completed bus trips over 55 active dates, which we then synthesized into 15.28 million stop-to-stop journey observations. It is important to emphasize that this is a historical dataset of observed timestamps, not a live streaming feed."*
- **Terms:** Trunk routes, corridor segments, observation volume.
- **Avoid:** Do not call journey observations 'passengers'.

### Slide 5: Data Quality & Governance (60s)
> *"A critical priority in this project was data governance—understanding the data rather than blindly training models. Our audit confirmed zero missing values, zero exact duplicates, and validated stop continuity. More importantly, we made two major governance decisions: First, we identified that Segment 1—the initial dispatch from terminal—exhibits massive dwell times exceeding 8 to 9 minutes due to driver layovers and schedule buffering. We preserved Segment 1 for operational fleet analysis, but strictly excluded it as a passenger boarding origin. Second, we detected an anomalous telematics drop on September 3rd and 4th caused by a cellular collection disruption. We preserved these dates in our analytical logs but excluded them from our machine-learning training partitions."*
- **Terms:** Data Governance, Terminal Dispatch Layover, Sensor Outage.
- **Avoid:** Do not claim data was 'corrupt'; explain it was operational behavior.

### Slide 6: Journey Construction & Target (45s)
> *"To model what a rider experiences, we constructed stop-to-stop journey observations from sequential segment runs. For every trip, we computed the total observed elapsed time from boarding stop departure to destination arrival. This defined our target variable: observed_journey_time_seconds. We then restricted our feature set to 10 strictly pre-journey attributes: route, direction, boarding and destination stop indices, segment numbers, hop count, day of week, weekend indicator, and calendar month."*
- **Terms:** Target Variable, Stop-to-Stop Construction, Pre-Journey Constraints.
- **Avoid:** Do not include run times or dwell times as features—that would be data leakage.

### Slide 7: Directional Asymmetry Analysis (60s)
> *"Using our SQL and EDA layer, one of our most striking operational findings was directional travel-time asymmetry. Across all three monitored routes, Direction 2 exhibits longer median journey durations than Direction 1, ranging from 1.34 to 2.36 minutes longer. Specifically on Route 12, Direction 2 (Inbound) has a median journey duration of 21.97 minutes compared to 20.63 minutes for Direction 1 (Outbound)—a 1.34-minute (80.0-second) differential. On Route 10, Direction 2 is 23.68 minutes versus 21.32 minutes (+2.36 minutes), and on Route 46, Direction 2 is 25.15 minutes versus 23.12 minutes (+2.03 minutes). This demonstrates that transit reliability is corridor- and direction-specific, influenced by physical road geometry and stop spacing."*
- **Terms:** Directional Asymmetry, Median Journey Duration.
- **Avoid:** Do not speculate that traffic congestion caused this; report the measured difference.

### Slide 8: Segment Variability Analysis (60s)
> *"Next, we evaluated travel-time dispersion across all 300 corridor segments. We established an empirical threshold to identify High-Variability Segments, defined as segments with at least 500 observations and an interquartile range of at least 68 seconds. Exactly 62 segments met this criteria. Rather than labeling these as 'bottlenecks'—which would imply unmeasured traffic congestion—we classify them as high-variability segments where dispatchers can target schedule buffers, signal priority, or stop-bay enforcement."*
- **Terms:** Interquartile Range (IQR), High-Variability Segments.
- **Avoid:** Do not use the word 'bottleneck' as an established fact.

### Slide 9: Dwell Dynamics & Dispatch (45s)
> *"Our dwell time analysis provided empirical validation for our Segment 1 decision. At standard passenger stops (Segments 2 and above), dwell times reflect routine boarding and alighting, with median dwells ranging between 22.0 and 27.0 seconds, representing about 20% to 23% of total segment time. In contrast, Terminal Dispatch (Segment 1) exhibits median dwells of 506 to 546 seconds on outbound routes, with 90th percentiles exceeding 39 minutes. This confirmed that Segment 1 reflects terminal holding and driver layover, rather than passenger transit."*
- **Terms:** Dwell Time, Terminal Holding, Layover Buffering.
- **Avoid:** Do not claim passenger dwell is zero; use the verified 22–27s median.

### Slide 10: Baseline Approach (45s)
> *"Before evaluating complex machine learning models, we established a rigorous historical median baseline. Using our training split, we calculated median journey times for every exact origin-destination segment pair, with a fallback to route-direction hop counts for unseen pairs. On our out-of-time test partition, this empirical baseline achieved an R-squared of 0.9171 and an MAE of 202.48 seconds (3.37 minutes). This showed that physical network topology and hop distance already explain the vast majority of journey duration."*
- **Terms:** Empirical Baseline, Segment-Pair Median, Hop Fallback.
- **Avoid:** Do not downplay the baseline; highlight that it is strong.

### Slide 11: Machine Learning Architecture (60s)
> *"To explore whether machine learning could improve upon this strong baseline, we enforced a strict chronological split: training on July through late August (9.93M records), validating on early September (2.27M records), and testing on out-of-time late September data (2.28M records). We evaluated linear regression, Ridge regression, and tree-based gradient boosting. Ridge regression underperformed the baseline (MAE of 4.13 min), proving that transit travel times exhibit non-linear spatial interactions. We selected HistGradientBoostingRegressor with squared error loss, which efficiently handles large tabular data and non-linear patterns."*
- **Terms:** Chronological Split, HistGradientBoostingRegressor, L2 Loss.
- **Avoid:** Do not claim random k-fold cross-validation was used; emphasize time-based splits.

### Slide 12: Model Evaluation & Out-of-Time Testing (60s)
> *"When evaluated on our 2.28M out-of-time test records, the HistGradientBoosting model achieved an MAE of 189.54 seconds (3.16 minutes), an RMSE of 332.22 seconds (5.54 minutes), and an R-squared of 0.9290. Compared to the historical baseline, this represents a 12.94-second reduction in MAE—a 6.39% relative improvement—and a 26.76-second reduction in RMSE. Note that we do not present the 3.2-minute MAE as an individual uncertainty interval; it is an aggregate model error metric across millions of trips."*
- **Terms:** Test Set Evaluation, MAE, RMSE, R-Squared.
- **Avoid:** Never say '±3.2 minutes uncertainty interval'.

### Slide 13: Feature Importance & Interpretability (45s)
> *"Permutation feature importance confirmed that segments_traversed accounts for 81.59% of model predictive power, reinforcing that physical corridor distance dominates travel time. Origin and destination stop indices contribute another 14.16%, providing localized adjustments for slower corridor zones. Calendar features like day of week provided minor marginal improvements. Crucially, we interpret feature importance as model predictive association, rather than physical causality."*
- **Terms:** Permutation Feature Importance, Predictive Association.
- **Avoid:** Do not claim features 'caused' delays.

### Slide 14: Application Demonstration (60s)
> *"We brought this research into a working prototype using Streamlit. On the Passenger view, users select a route, direction, origin, destination, and date. The app queries our serialized model in under 5 milliseconds and displays the predicted duration alongside the historical baseline median and test MAE. On the Operator view, analysts can inspect network KPIs, explore directional asymmetry, and filter the 62 high-variability segments. The app is lightweight, caching summaries in memory without loading the full 1.7 GB training CSV."*
- **Terms:** Streamlit, Service Architecture, In-Memory Caching.
- **Avoid:** Do not claim the app connects to live city bus APIs.

### Slide 15: Limitations, Product Trade-Offs & Conclusion (60s)
> *"To conclude, BusInsight demonstrates a disciplined data engineering and analytics workflow. A key product takeaway is the baseline trade-off: our historical median baseline was already very strong, explaining over 91% of variance. While machine learning provided a measurable 6.4% error reduction, in a production setting a product team must weigh whether that 13-second improvement justifies the ongoing operational overhead of an ML model over a fast lookup table. In terms of limitations, this is a historical prototype without live GPS feeds, traffic data, or ridership counts. Thank you, and I welcome your questions."*
- **Terms:** Product Trade-Offs, Operational Overhead, Scope Boundaries.
- **Avoid:** Do not overpromise future versions; keep discussion grounded.

---

## 10. Comprehensive Interview & Instructor Q&A

### Category A: Data & Transit Foundations
**Q1: Why did you choose this dataset, and why Astana?**
> *"The Astana transit dataset provides a rare combination of static GTFS schedules and millions of real-world automated vehicle location (AVL) segment observations. It provided an ideal testbed for evaluating transit predictability, data quality challenges, and travel-time modeling in a mid-sized capital city with defined trunk corridors."*

**Q2: What is GTFS, and what is GPS-derived AVL data?**
> *"GTFS (General Transit Feed Specification) is the global standard format for static public transit schedules, routes, and stop locations. GPS-derived AVL data represents actual empirical sensor pings recorded by on-board vehicle transponders, capturing actual stop arrival, departure, run, and dwell times."*

**Q3: How large was the dataset, and what were the primary data-quality issues?**
> *"The raw dataset contained 785,976 segment records across 19,769 trips. Major data quality challenges included zero-duration dwell/run records, a severe sensor telematics outage on September 3–4, and an operational anomaly where initial terminal dispatch (Segment 1) accumulated heavy layover holding times that skewed passenger travel times."*

---

### Category B: Data Preparation & Methodology
**Q4: Why did you exclude Segment 1 from passenger journey origins?**
> *"Our audit revealed that Segment 1 (initial dispatch from terminal) includes driver layovers, schedule recovery buffering, and dispatch holding (median dwell of 506–546 seconds on outbound routes). Including Segment 1 in passenger origin dropdowns artificially inflated trip estimates by 8 to 15 minutes. We preserved it for fleet dispatch analysis but excluded it from passenger trip starts."*

**Q5: Why retain September 3–4 analytically but exclude it from machine learning?**
> *"On September 3–4, daily recorded trips dropped by over 70% due to an external telematics collection failure. Retaining these records in analytical logs ensures historical audit fidelity, but excluding them from training partitions prevented our machine learning models from learning distorted patterns from sparse, unrepresentative data."*

**Q6: How was stop continuity validated?**
> *"We verified that for every trip, each segment's origin stop matched the preceding segment's destination stop, and that physical sequence numbers progressed monotonically without missing intermediate stops."*

---

### Category C: Machine Learning & Modeling
**Q7: What was your target variable, and why?**
> *"The target variable is `observed_journey_time_seconds`, representing the total elapsed time from the vehicle departing the passenger's origin stop to arriving at the destination stop. It captures actual elapsed travel duration including intermediate run times and dwells."*

**Q8: Why establish a historical-median baseline before training ML models?**
> *"In applied machine learning, complex models must justify their existence against simple, interpretable baselines. Because transit networks follow fixed physical geometry, we hypothesized that historical segment-pair medians would be very strong. Establishing this baseline gave us a strict benchmark ($R^2 = 0.9171$, MAE = 3.37 min) to measure whether ML provided genuine added value."*

**Q9: Why use a chronological train/val/test split instead of random k-fold cross-validation?**
> *"Random splitting causes temporal data leakage in time-series and transit telemetry: trips from the same hour or day would be in both train and test sets. A chronological split (July–August for training, early September for validation, late September for testing) accurately replicates prospective deployment conditions."*

**Q10: Why did you choose `HistGradientBoostingRegressor` over Linear or Ridge Regression?**
> *"Ridge regression performed poorly (MAE of 4.13 min, worse than baseline) because transit travel times exhibit non-linear spatial interactions between stops and segments. HistGradientBoosting handles non-linearities and bin-based tabular data efficiently, allowing fast training and sub-millisecond inference across millions of records."*

**Q11: Why is the ML model's improvement over the baseline relatively modest (6.39%)?**
> *"Because physical corridor distance (`segments_traversed`) accounts for over 81% of travel-time variance. A historical median table already captures distance and typical segment speeds. The ML model’s 12.94-second advantage comes from capturing non-linear stop-pair interactions and calendar effects, which are real but secondary to corridor distance."*

**Q12: What does your $R^2$ score of 0.9290 mean in practical terms?**
> *"It means the model explains 92.9% of the variance in stop-to-stop journey durations across the 2.28 million out-of-time test records, with the remaining 7.1% driven by unmeasured factors like traffic fluctuations, weather, and localized passenger boarding surges."*

---

### Category D: Product Thinking & Applications
**Q13: Why did you build two separate interfaces for Passengers and Operators?**
> *"Riders and transit planners have completely different needs. Riders care about prospective estimation: 'How long will my trip take before I board?' Operators care about retrospective diagnostics: 'Where are our corridor bottlenecks, which directions are asymmetric, and how long are buses dwelling at terminals?'"*

**Q14: Is this system operating in real-time? Where would live GPS fit in?**
> *"No, this is a historical predictive prototype. In a live production system, real-time GTFS-RT telemetry would fit as a dynamic adjustment layer: real-time bus locations would inform headway countdowns, and historical ML models would predict the remaining travel time once onboard."*

**Q15: If you were the Product Manager, would you deploy the ML model or the baseline lookup?**
> *"It depends on infrastructure constraints. If the priority is zero-maintenance, zero-dependency, ultra-lightweight deployment, the historical median lookup is compelling—it achieves 91.7% $R^2$ with no model drift. However, if the authority wants calendar sensitivity and higher accuracy, deploying the 421 KB HistGradientBoosting model is well-justified because its local inference latency is negligible."*

---

### Category E: Scope & Limitations
**Q16: Does the model account for traffic congestion or weather?**
> *"No. The dataset does not include independent traffic camera feeds, vehicle speed sensors, or meteorological logs. While traffic and weather certainly influence travel times, our model captures their historical downstream footprint empirically through time-of-day and calendar features, without making unsupported causal claims."*

**Q17: Can this model forecast passenger crowding or demand?**
> *"No. The dataset contains vehicle location logs, not automated passenger counters (APC) or electronic fare ticketing (AFC). Our 15.2M observations represent constructed vehicle trajectory pairs, not individual passenger volumes."*

---

## 11. "Tell Me About Your Project" — 60–90 Second Interview Answer

> *"BusInsight is an urban transit analytics and predictive travel-time prototype built on GPS automated vehicle location data from the public bus network in Astana, Kazakhstan.*
>
> *I set out to solve a dual problem: transit riders need reliable travel-time estimates before boarding, while transit planners need granular segment-level performance data to diagnose corridor delays.*
>
> *I analyzed over 785,000 GPS segment records across three trunk routes and constructed 15.2 million stop-to-stop journey observations. Before jumping into machine learning, I conducted a deep data-quality audit where I discovered that terminal dispatch segments accumulated massive layover dwells of 8 to 9 minutes. I isolated terminal dispatch from passenger origins to avoid inflating travel estimates, and isolated an anomalous sensor outage on September 3rd and 4th.*
>
> *I then built an analytical SQL layer in DuckDB that uncovered a 1.34-minute directional travel-time differential on Route 12 (with Direction 2 longer across all corridors) and mapped 62 high-variability corridor segments.*
>
> *For prediction, I first established a historical median baseline, which was surprisingly strong at a 3.37-minute MAE and a 0.917 R-squared. I then trained a HistGradientBoosting model on 10 strictly pre-journey features under a chronological split. On 2.28 million out-of-time test records, the model achieved an MAE of 3.16 minutes—a 6.4% error reduction over the baseline.*
>
> *Finally, I translated these findings into a modular Streamlit web app with separate passenger estimation and operator intelligence views. A key takeaway was the product trade-off: recognizing that while ML delivered a measurable 13-second improvement, an empirical baseline was already exceptionally capable."*

---

## 12. 30-Second Elevator Pitch

> *"BusInsight is an end-to-end transit intelligence prototype that analyzes 15.2 million GPS bus journey observations in Astana to provide pre-journey travel-time estimates for riders and corridor performance analytics for operators.*
>
> *I audited raw GTFS and AVL telemetry, engineered an analytical SQL layer uncovering directional corridor asymmetries, and trained a gradient-boosted regression model that reduced travel-time prediction error by 6.4% over a strong empirical baseline across 2.28 million test trips.*
>
> *I deployed the complete system as an interactive Streamlit application balancing data engineering, machine learning rigor, and product thinking."*

---

## 13. Portfolio Positioning Guardrails

### What BusInsight Proves:
- **Data Engineering & Quality:** Ability to audit raw telemetry, validate relational integrity, handle sensor disruptions, and enforce data governance rules.
- **SQL & Analytical Thinking:** Ability to structure analytical schemas, compute complex window functions, and extract operational insights (directional asymmetry, dwell dynamics).
- **Applied Machine Learning Rigor:** Discipline to establish simple empirical baselines first, enforce strict chronological splits, prevent feature leakage, and evaluate models on out-of-sample data.
- **Product & Persona Thinking:** Ability to translate analytical findings into intuitive user interfaces tailored to specific stakeholders (riders vs operators).
- **Truth in Data & Honest Communication:** Restraint to avoid inflated claims, distinguish association from causality, and communicate limitations transparently.

### What BusInsight Does NOT Claim:
- It is **not** a live transit dispatch or real-time vehicle tracking infrastructure.
- It does **not** forecast passenger demand, crowding, or ticketing revenue.
- It does **not** assert causal claims regarding external vehicle traffic or driver behavior.
- It does **not** present model error metrics as statistical confidence intervals.

---

## 14. Dataset Attribution & Academic Citation

BusInsight is built using the open Astana public bus dataset published by:

> Mansurova, A.; Mussina, A.; Aubakirov, S.; Nugumanova, A.; Yedilkhan, D. (2025).  
> *"From Raw GPS to GTFS: A Real-World Open Dataset for Bus Travel Time Prediction."*  
> *Data*, 10(8), 119.  
> - **Paper:** [https://doi.org/10.3390/data10080119](https://doi.org/10.3390/data10080119)  
> - **Dataset:** [https://doi.org/10.5281/zenodo.15769359](https://doi.org/10.5281/zenodo.15769359)  
> - **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

### Provider & Independent Implementation Statement
- **Original GPS Data Provider:** **INNOFORCE SOLUTIONS LLP**, published with permission from the rights holder as documented in the dataset publication.
- **Independent Project Notice:** BusInsight is an independent portfolio implementation. Neither the dataset authors, publication authors, nor INNOFORCE SOLUTIONS LLP created, reviewed, endorsed, or are affiliated with this project.

