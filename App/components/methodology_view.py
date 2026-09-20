"""
BusInsight - Methodology, Governance, Attribution & Roadmap Component
Renders scientific methodology standards, data governance guardrails,
official dataset attribution, and future engineering roadmap.
"""

import streamlit as st


def render_methodology_view():
    """Renders the Project Methodology, Governance, Attribution, and Roadmap view."""
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #F1F5F9; border: 1px solid #CBD5E1; color: #334155; padding: 3px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;">
                📖 Scientific Governance & Project Scope
            </div>
            <h1 style="margin: 0 0 6px 0;">Methodology, Attribution & Roadmap</h1>
            <p style="color: #64748B; font-size: 1rem; margin: 0;">
                Comprehensive documentation of data governance principles, open dataset attribution, and future transit technology capabilities.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tab_gov, tab_attr, tab_road = st.tabs([
        "🛡️ Methodology & Data Governance",
        "📑 Dataset & Scientific Attribution",
        "🚀 Future Roadmap"
    ])

    # -------------------------------------------------------------------------
    # 1. METHODOLOGY & DATA GOVERNANCE
    # -------------------------------------------------------------------------
    with tab_gov:
        st.markdown("### Non-Negotiable Data Governance Principles")
        st.caption("Six methodological guardrails established to prevent bias, eliminate data leakage, and ensure data integrity.")

        with st.expander("1. Terminal Dispatch Isolation (Segment 1 Exclusion)", expanded=True):
            st.markdown("""
                * **Operational Telemetry Reality:** Empirical analysis revealed that Segment 1 (the initial segment after leaving terminal dispatch) contains heavy layover buffering, schedule recovery holding, and driver break durations (median dwell: 506–546s on outbound routes).
                * **Governance Lock (Task 2B):** Segment 1 records are preserved in analytical databases for operator fleet management, but are **strictly excluded as origin boarding stops** for passenger travel-time modeling.
                * **Impact:** Prevents artificial 5–15 minute dwell inflations from distorting ordinary passenger journey estimates.
            """)

        with st.expander("2. September 3–4 Reduced-Coverage Outage Handling"):
            st.markdown("""
                * **Telematics Disruption:** An empirical audit identified an extreme telematics drop on September 3–4, 2024, where daily trip counts dropped severely due to cellular collection outages.
                * **Governance Lock (Task 2B/2C):** Disrupted dates are preserved in raw historical logs, but strictly excluded from ML training partitions to prevent learning from sparse, unrepresentative telemetry.
            """)

        with st.expander("3. Zero-Leakage Pre-Journey Feature Formulation"):
            st.markdown("""
                * **Methodological Standard:** A transit rider requesting an estimate before boarding does not have access to post-journey information.
                * **Strict Pre-Journey Features:** The ML model accepts solely:
                  `route_short_name`, `direction_id`, `start_stop_idx`, `dest_stop_idx`, `start_segment`, `destination_segment`, `segments_traversed`, `day_of_week`, `is_weekend`, `month`.
                * **Zero Data Leakage:** No intermediate run times, actual dwell durations, arrival timestamps, or total trip aggregates are permitted in inference.
            """)

        with st.expander("4. Observation Volume Terminology (Not Ridership)"):
            st.markdown("""
                * **Precision Notice:** The dataset contains automated vehicle location (AVL) stop events and mathematically reconstructed stop-to-stop vehicle observations ($N = 15,277,204$).
                * **No Passenger Counters:** The telemetry does **not** contain automated passenger counters (APC) or fare-card taps.
                * **Terminology Standard:** Volumes are strictly described as **journey observations** or **corridor observations**, never as individual passenger counts.
            """)

        with st.expander("5. Empirical Observation vs. Speculative Causality"):
            st.markdown("""
                * **Analytical Standard:** Corridor segments exhibiting high travel-time variability ($\text{IQR} \ge 68\text{s}$) are documented strictly through empirical measurement.
                * **No Unmeasured Inferences:** Without direct sensors for external roadway traffic, weather, or signal controllers, variability is never speculatively attributed to 'traffic congestion' or 'driver behavior'.
            """)

        with st.expander("6. Historical Predictive Scope (Not Live GPS)"):
            st.markdown("""
                * **Application Boundaries:** BusInsight is an offline historical machine-learning prototype designed for tactical planning and pre-journey estimation.
                * **No Live Feeds:** The platform does not claim real-time GPS tracking, live bus positioning, or dynamic congestion-adjusted ETAs.
            """)

    # -------------------------------------------------------------------------
    # 2. DATASET & ATTRIBUTION
    # -------------------------------------------------------------------------
    with tab_attr:
        st.markdown("### Open Dataset & Scientific Attribution")
        st.markdown("""
            BusInsight utilizes the open Astana bus operations dataset described in the scientific publication:
        """)

        st.markdown("""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #0284C7; border-radius: 8px; padding: 18px 20px; margin: 14px 0;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 6px;">
                    From Raw GPS to GTFS: A Real-World Open Dataset for Bus Travel Time Prediction
                </div>
                <div style="font-size: 0.9rem; color: #334155; margin-bottom: 12px;">
                    <strong>Authors:</strong> Aigerim Mansurova, Aigerim Mussina, Sanzhar Aubakirov, Aliya Nugumanova, Didar Yedilkhan (2025).<br>
                    <strong>Journal:</strong> <em>Data</em>, 10(8), 119.
                </div>
                <div style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
                    <div>📄 <strong>Paper DOI:</strong> <a href="https://doi.org/10.3390/data10080119" target="_blank" style="color: #0284C7;">https://doi.org/10.3390/data10080119</a></div>
                    <div>💾 <strong>Zenodo Dataset DOI:</strong> <a href="https://doi.org/10.5281/zenodo.15769359" target="_blank" style="color: #0284C7;">https://doi.org/10.5281/zenodo.15769359</a></div>
                    <div>⚖️ <strong>Dataset License:</strong> <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" style="color: #0284C7;">Creative Commons Attribution 4.0 International (CC BY 4.0)</a></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Data Provider & Independent Implementation Notice")
        st.markdown("""
            * **Original Data Provider:** The original raw GPS telemetry records were provided by **INNOFORCE SOLUTIONS LLP** and published with permission from the rights holder, as described in the source dataset publication.
            * **Independent Project Notice:** BusInsight is an independent portfolio, data engineering, and machine-learning implementation created for demonstration purposes using this publicly released open dataset. Neither the dataset authors, publication authors, nor INNOFORCE SOLUTIONS LLP created, reviewed, endorsed, or are affiliated with this project.
        """)

    # -------------------------------------------------------------------------
    # 3. FUTURE ROADMAP
    # -------------------------------------------------------------------------
    with tab_road:
        st.markdown("### Product & Engineering Roadmap")
        st.caption("Distinguishing validated offline capabilities from future production enhancements.")

        r_col1, r_col2 = st.columns(2, gap="large")

        with r_col1:
            st.markdown("#### ✅ Completed & Validated Capabilities")
            st.markdown("""
                * **Historical Telemetry Cleaning:** Automated audit, zero-duration scrubbing, coordinate validation across 785K segment events.
                * **Controlled Journey Reconstruction:** Generation of 15.28M stop-to-stop journey pairs under Segment 1 layover exclusion.
                * **Strict Pre-Journey ML Pipeline:** HistGradientBoosting (L2) trained on 14.48M rows, achieving 3.16 min MAE and 0.9290 R².
                * **Corridor Variability Identification:** 62 High-Variability corridor segments cataloged with IQR &ge; 68s.
                * **Directional Asymmetry Quantification:** Route 12's 20% directional travel-time spread empirically characterized.
                * **Dual-Persona Interface:** Streamlit web application providing Passenger planning and Operator corridor intelligence.
            """)

        with r_col2:
            st.markdown("#### 🚀 Planned Future Engineering")
            st.markdown("""
                * **Live Telematics Ingestion:** Connect GTFS-RT Kafka streams to ingest real-time automated vehicle location (AVL) pings.
                * **Real-Time Dynamic ETAs:** Complement offline pre-journey predictions with dynamic headway and vehicle-position adjustments.
                * **Contextual Weather & Incident Overlays:** Integrate municipal weather feeds and road incident telemetry to investigate external variance drivers.
                * **Network Scale:** Expand data pipeline across all 90+ urban bus routes in Astana's metropolitan transit system.
                * **Mobile Application:** Responsive PWA or native mobile client for on-the-go passenger trip planning.
                * **Operator Dispatch Alerts:** Automated notification subsystem when corridor travel times exceed empirical P90 thresholds.
            """)
