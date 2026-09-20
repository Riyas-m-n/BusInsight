"""
BusInsight - Operator & Analyst Intelligence Dashboard Component
Renders protected corridor performance monitoring, directional travel-time asymmetry,
segment variability (62 high-variability segments), and dwell dynamics derived from Task 4 SQL & EDA.
"""

import os
import streamlit as st

from ..services.analytics_service import (
    load_route_summary,
    load_route_direction_summary,
    load_segment_summary,
    load_high_variability_segments,
    load_dwell_summary,
    load_hop_scaling_summary,
    load_day_summary,
)

OPERATOR_USER = os.environ.get("BUSINSIGHT_OPERATOR_USER", "operator")
OPERATOR_PASSWORD = os.environ.get("BUSINSIGHT_OPERATOR_PASSWORD", "transit2024")


def render_operator_view():
    """Renders the Operator / Analyst area with authentication protection."""
    if not st.session_state.get("operator_auth", False):
        render_operator_login()
        return

    render_authenticated_operator()


def render_operator_login():
    """Renders the authentication form for transit operators and analysts."""
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #CCFBF1; border: 1px solid #99F6E4; color: #0F766E; padding: 3px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;">
                🔒 Protected Operations Workspace
            </div>
            <h1 style="margin: 0 0 6px 0;">Transit Operations Login</h1>
            <p style="color: #64748B; font-size: 1rem; margin: 0;">
                Authorized access for municipal transit planners, operations controllers, and corridor analysts.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_form, col_info = st.columns([1.2, 1], gap="large")

    with col_form:
        st.markdown("### Sign In to Operations")

        with st.form("operator_login_form"):
            user_input = st.text_input("Operator Username", key="ops_user_input")
            pass_input = st.text_input("Password", type="password", key="ops_pass_input")
            submit = st.form_submit_button("Authenticate & Open Dashboard", type="primary", use_container_width=True)

            if submit:
                if user_input.strip() == OPERATOR_USER and pass_input == OPERATOR_PASSWORD:
                    st.session_state["operator_auth"] = True
                    st.session_state["operator_username"] = user_input.strip()
                    st.success("Authentication successful! Loading operations workspace...")
                    st.rerun()
                else:
                    st.error("Authentication failed: Invalid operator credentials.")

        st.caption(
            "💡 **Prototype demo notice**: Default analyst credentials are configured via environment variables "
            "(`BUSINSIGHT_OPERATOR_USER` / `BUSINSIGHT_OPERATOR_PASSWORD`)."
        )

    with col_info:
        st.markdown("### Operations Intelligence Scope")
        st.markdown("""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.25rem; font-size: 0.9rem; color: #334155; line-height: 1.6;">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 8px;">Analyst Modules Included:</div>
                <ul style="margin: 0 0 1rem 0; padding-left: 20px;">
                    <li><strong>Route Performance:</strong> Network KPIs, corridor summaries, directional asymmetry quantification.</li>
                    <li><strong>Segment Variability:</strong> Full inventory of the 62 empirical high-variability segments (N &ge; 500, IQR &ge; 68s).</li>
                    <li><strong>Dwell & Journey Trends:</strong> Terminal dispatch holding vs routine stop dwell, hop-tier progression, day patterns.</li>
                </ul>
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">Guardrail Standard:</div>
                <div>All metrics reflect empirical telemetry observations without speculative causal assumptions regarding unmeasured external traffic.</div>
            </div>
        """, unsafe_allow_html=True)


def render_authenticated_operator():
    """Renders the full, authenticated Operator workspace."""
    col_hdr, col_btn = st.columns([4, 1])
    with col_hdr:
        st.markdown("""
            <div style="margin-bottom: 12px;">
                <div style="display: inline-flex; align-items: center; gap: 6px; background: #CCFBF1; border: 1px solid #99F6E4; color: #0F766E; padding: 3px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;">
                    ✅ Authenticated Session: Transit Operations Analyst
                </div>
                <h1 style="margin: 0 0 4px 0;">Corridor Operations & Performance</h1>
                <p style="color: #64748B; font-size: 0.95rem; margin: 0;">
                    Empirical corridor monitoring, directional travel-time asymmetry, segment variability, and dwell dynamics.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="btn_operator_logout", use_container_width=True):
            st.session_state["operator_auth"] = False
            st.rerun()

    # Three Productized Operations Tabs
    tab_route, tab_variability, tab_dwell = st.tabs([
        "📈 Route Performance",
        "⚠️ Segment Variability (62 Segments)",
        "⏱️ Dwell & Journey Trends"
    ])

    # -------------------------------------------------------------------------
    # 1. ROUTE PERFORMANCE
    # -------------------------------------------------------------------------
    with tab_route:
        st.markdown("### Corridor Network Summary")
        st.caption("Aggregated telemetry across 3 monitored trunk corridors over the full observation period (July–September 2024).")

        df_routes = load_route_summary()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monitored Routes", "3 Routes", "Routes 10, 12, 46")
        with col2:
            st.metric("Corridor Segments", "300 Segments", "Physical Stops (Seg >= 2)")
        with col3:
            st.metric("Segment Records", f"{df_routes['total_segment_observations'].sum():,}", "Raw Segment Events")
        with col4:
            st.metric("Journey Observations", f"{df_routes['total_passenger_journeys'].sum():,}", "Constructed Stop-to-Stop")

        st.markdown("#### Route-Level Performance Metrics")
        display_df = df_routes[[
            "route_short_name",
            "route_long_name",
            "total_segment_observations",
            "distinct_trips",
            "distinct_operating_dates",
            "median_segment_run_time_sec",
            "median_segment_dwell_time_sec",
            "total_passenger_journeys",
            "median_journey_time_min",
            "p10_journey_time_min",
            "p90_journey_time_min"
        ]].copy()

        display_df.columns = [
            "Route",
            "Corridor Name",
            "Segment Obs",
            "Trips",
            "Days",
            "Med Run (s)",
            "Med Dwell (s)",
            "Journey Obs",
            "Med Journey (min)",
            "P10 (min)",
            "P90 (min)"
        ]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("#### Directional Asymmetry Analysis")
        st.caption("Empirical travel-time comparison between Direction 1 (Outbound) and Direction 2 (Inbound).")

        df_dir = load_route_direction_summary()
        dir_labels = {1: "Direction 1 (Outbound)", 2: "Direction 2 (Inbound)"}
        df_dir["direction_label"] = df_dir["direction_id"].map(dir_labels)
        display_dir = df_dir[[
            "route_short_name",
            "direction_id",
            "direction_label",
            "total_segment_records",
            "total_journey_observations",
            "median_journey_min",
            "p10_journey_min",
            "p90_journey_min",
            "p10_p90_range_min"
        ]].copy()

        display_dir.columns = [
            "Route",
            "Dir ID",
            "Direction Label",
            "Segment Obs",
            "Journey Obs",
            "Median (min)",
            "P10 (min)",
            "P90 (min)",
            "P10-P90 Spread (min)"
        ]

        st.dataframe(display_dir, use_container_width=True, hide_index=True)

        st.markdown("""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 0.9rem; color: #334155;">
                <strong>Directional Findings:</strong>
                <ul style="margin: 4px 0 0 16px; padding: 0;">
                    <li><strong>Route 12 Asymmetry:</strong> Displays significant structural asymmetry: Direction 1 (Outbound) median is <strong>21.0 min</strong> versus <strong>17.5 min</strong> for Direction 2 (Inbound) &mdash; a <strong>3.5 min (20.0%) differential</strong>.</li>
                    <li><strong>Route 10 Balance:</strong> Tightly balanced across directions (20.3 min Outbound vs 19.9 min Inbound).</li>
                    <li><strong>Route 46 Duration:</strong> Largest overall travel times with 26.5 min Outbound and 25.8 min Inbound (P90 reaching 43.5 min).</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. SEGMENT VARIABILITY
    # -------------------------------------------------------------------------
    with tab_variability:
        st.markdown("### High-Variability Corridor Segments")
        st.markdown("""
            Corridor segments meeting the validated project threshold: **N &ge; 500 observations** and **IQR &ge; 68.0 seconds**.
            A total of **62 segments** out of 300 exhibit this empirical travel-time spread.
        """)

        df_high_var = load_high_variability_segments()

        # Route Filter
        r_filter = st.selectbox("Filter Segments by Route", ["All Routes", "Route 10", "Route 12", "Route 46"], key="var_route_filter")
        if r_filter == "Route 10":
            df_filtered = df_high_var[df_high_var["route_short_name"] == 10]
        elif r_filter == "Route 12":
            df_filtered = df_high_var[df_high_var["route_short_name"] == 12]
        elif r_filter == "Route 46":
            df_filtered = df_high_var[df_high_var["route_short_name"] == 46]
        else:
            df_filtered = df_high_var

        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.metric("Total Flagged Segments", f"{len(df_high_var)} Segments", "Across All 3 Routes")
        with col_v2:
            st.metric("Currently Displayed", f"{len(df_filtered)} Segments", r_filter)
        with col_v3:
            max_iqr = df_filtered["iqr_run_time_sec"].max() if not df_filtered.empty else 0
            st.metric("Max Segment IQR", f"{max_iqr:.1f} s", "Widest spread in selection")

        # Table Display
        display_var = df_filtered[[
            "route_short_name",
            "direction_id",
            "segment",
            "start_stop_sample",
            "end_stop_sample",
            "n_obs",
            "median_run_time_sec",
            "iqr_run_time_sec",
            "p10_run_time_sec",
            "p90_run_time_sec"
        ]].copy()

        display_var.columns = [
            "Route",
            "Dir",
            "Seg #",
            "Origin Stop",
            "Next Stop",
            "Sample (N)",
            "Median (s)",
            "IQR (s)",
            "P10 (s)",
            "P90 (s)"
        ]

        st.dataframe(display_var, use_container_width=True, hide_index=True)

        st.markdown("""
            <div style="background-color: #FEF3C7; border-left: 4px solid #D97706; padding: 12px 14px; border-radius: 4px; margin-top: 14px; font-size: 0.85rem; color: #92400E;">
                <strong>Terminology & Methodological Standard:</strong><br>
                These segments are classified strictly as <strong>High-Variability Segments</strong> based on statistical dispersion (IQR &ge; 68s).
                The dataset does not contain external vehicular traffic counts, roadway incidents, or weather telemetry; therefore, variability is never speculatively attributed to 'traffic congestion' or 'bottlenecks'.
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. DWELL & JOURNEY TRENDS
    # -------------------------------------------------------------------------
    with tab_dwell:
        st.markdown("### Operational Dwell Dynamics & Holding Analysis")
        st.caption("Empirical comparison between Terminal Dispatch (Segment 1) and Standard Passenger Stops (Segments &ge; 2).")

        df_dwell = load_dwell_summary()
        st.dataframe(df_dwell, use_container_width=True, hide_index=True)

        st.markdown("""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-top: 12px; font-size: 0.9rem; color: #334155;">
                <strong>Dwell Analysis Summary:</strong>
                <ul style="margin: 4px 0 0 16px; padding: 0;">
                    <li><strong>Terminal Dispatch (Segment 1):</strong> Exhibits substantial layover holding and initial dispatch buffering (median dwell: 506–546s on outbound corridors). Excluded from passenger origin selections to prevent artificial trip inflation.</li>
                    <li><strong>Standard Passenger Stops (Segments &ge; 2):</strong> Reflect routine boarding and alighting with median dwell times tightly clustered between <strong>22.0 and 27.0 seconds</strong> (accounting for 20% to 23% of total segment duration).</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Hop-Tier Scaling & Day-of-Week Operational Trends")

        d_col1, d_col2 = st.columns(2, gap="large")

        with d_col1:
            st.markdown("#### Hop-Length Scaling")
            st.caption("Journey duration scaling across hop tiers (segments traversed).")
            df_hop = load_hop_scaling_summary()
            st.dataframe(df_hop, use_container_width=True, hide_index=True)

        with d_col2:
            st.markdown("#### Day-of-Week Patterns")
            st.caption("Travel time stability across Monday–Sunday operating schedules.")
            df_day = load_day_summary()
            st.dataframe(df_day, use_container_width=True, hide_index=True)
