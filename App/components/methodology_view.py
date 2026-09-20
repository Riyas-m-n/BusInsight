"""
BusInsight - About, Methodology & Governance Component
Documents project architecture, methodology decisions, data governance guardrails,
and operational limitations.
"""

import streamlit as st


def render_methodology_view():
    """Renders the About, Methodology & Limitations page."""
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="margin-bottom: 6px;">Project Architecture & Governance</h1>
            <p style="color: #64748b; font-size: 1.05rem; margin: 0;">
                Comprehensive documentation of methodology decisions, data engineering standards, and analytical guardrails.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        ### 1. Project Overview
        **BusInsight** is an enterprise-grade transit analytics and predictive intelligence platform developed for the
        urban bus network in **Astana, Kazakhstan**. Operating on automated vehicle location (AVL) and transit operations
        telemetry collected between **July 1 and September 30, 2024**, the system translates over **15.2 million journey observations**
        into actionable transit intelligence for riders and operators.
    """)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            #### System Capabilities
            * **Passenger Travel-Time Estimation:** Pre-journey travel-time predictions derived from historical telemetry using gradient-boosted decision trees.
            * **Directional Asymmetry Analysis:** Quantifies travel-time imbalances between outbound and inbound corridors (e.g., Route 12's 20% directional spread).
            * **Corridor Variability Analysis:** Empirically identifies 62 high-variability segments ($N \ge 500$, $\text{IQR} \ge 68\text{s}$) across 300 corridor segments.
            * **Dwell & Dispatch Dynamics:** Disentangles terminal layover regulation from passenger stop dwell times.
        """)

    with col2:
        st.markdown("""
            #### Monitored Corridors
            * **Route 10:** Express trunk connecting Central Railway Station to Nursultan Nazarbayev International Airport via Mangilik El Avenue.
            * **Route 12:** Urban trunk connecting Central Railway Station to International Airport via Kabanbay Batyr Avenue.
            * **Route 46:** Cross-city residential trunk connecting Karasu to Comfort Town.
        """)

    st.markdown("---")
    st.markdown("### 2. Methodological Guardrails & Data Governance")

    st.markdown("""
        To maintain strict scientific rigor and avoid deceptive or unsupported claims, BusInsight adheres to six non-negotiable data governance principles:
    """)

    with st.expander("1. Terminal Dispatch Isolation (Segment 1 Exclusion)", expanded=True):
        st.markdown("""
            * **Operational Reality:** Analysis revealed that Segment 1 (the initial segment from terminal dispatch) incorporates driver layovers, schedule recovery buffering, and initial dispatch/terminal holding time.
            * **Data Governance Decision (Task 2B Lock):** Segment 1 records are preserved in analytical databases for operator fleet management, but are **strictly excluded** as origin boarding stops for passenger journey-time modeling.
            * **Impact:** Eliminates artificial 5–15 minute dwell inflations from passenger-facing travel-time estimates.
        """)

    with st.expander("2. September 3–4 Reduced-Coverage Handling"):
        st.markdown("""
            * **Data Anomaly:** An empirical audit identified an extreme telematics disruption on September 3–4, 2024, where daily trip counts dropped precipitously due to cellular/GPS collection outages.
            * **Data Governance Decision (Task 2B/2C Lock):** The disrupted dates are preserved in raw historical logs, but strictly excluded from model training partitions to prevent learning from sparse, biased telemetry.
        """)

    with st.expander("3. Zero-Leakage Pre-Journey Feature Formulation"):
        st.markdown("""
            * **Methodological Requirement:** A passenger requesting a travel-time estimate before boarding does not have access to post-journey information.
            * **Strict Pre-Journey Features:** The ML model accepts only:
              `route_short_name`, `direction_id`, `start_stop_idx`, `dest_stop_idx`, `start_segment`, `destination_segment`, `segments_traversed`, `day_of_week`, `is_weekend`, `month`.
            * **Zero Data Leakage:** No intermediate run times, actual dwell durations, arrival timestamps, or total trip aggregates are permitted in inference.
        """)

    with st.expander("4. Clarification on Observation Counts vs. Ridership"):
        st.markdown("""
            * **Precision Notice:** The dataset contains automated vehicle location (AVL) stop events and mathematically generated stop-to-stop journey observations ($N = 15,277,204$).
            * **No Direct Ridership:** The source telemetry does **not** contain automated passenger counter (APC) data or electronic fare collection (AFC) records.
            * **Terminology:** Volumes are strictly described as **journey observations** or **corridor observations**, never as individual passenger counts.
        """)

    with st.expander("5. Empirical Observation vs. Speculative Causality"):
        st.markdown("""
            * **Analytical Standard:** Corridor segments exhibiting high travel-time variability ($\text{IQR} \ge 68\text{s}$) are documented strictly through empirical measurement.
            * **No Unmeasured Inferences:** Without direct sensors for external vehicle traffic, weather conditions, or signal controller logs, variability is never speculatively attributed to 'traffic congestion' or 'driver behavior'.
        """)

    with st.expander("6. Historical Predictive Prototype (Not Live GPS / Real-Time ETA)"):
        st.markdown("""
            * **Scope of Application:** This application is a historical machine-learning prototype designed for planning and tactical analysis.
            * **No Real-Time Feeds:** The platform does not claim live GPS tracking, live bus positioning, or real-time incident-adjusted ETAs.
        """)

    st.markdown("---")
    st.markdown("### 3. Pipeline Architecture & Deliverables")

    st.markdown("""
        | Milestone | Core Objective | Key Deliverables |
        | :--- | :--- | :--- |
        | **Task 1** | Pipeline & Data Audit | Schema validation, zero-duration cleansing, initial audit report |
        | **Task 2A** | Segment 1 Investigation | Dwell-vs-runtime analysis, dispatch layover characterization |
        | **Task 2B** | Controlled Journey Regeneration | 15.28M journey dataset regenerated under locked Segment 1 & Sep 3–4 rules |
        | **Task 2C** | ML-Ready Dataset Preparation | 14.48M row ML dataset, pre-journey time-of-day investigation, historical baseline |
        | **Task 3** | ML Model Training & Evaluation | Benchmark across Baseline, Ridge, HistGradientBoosting; test set evaluation |
        | **Task 4** | SQL & Exploratory Data Analysis | DuckDB analytics, 62 high-variability segments, directional asymmetry, dwell dynamics |
        | **Task 5** | Production Web Application | Modular Streamlit application with Passenger & Operator interfaces |
    """)
