"""
BusInsight - Operator & Analyst Intelligence Dashboard
Provides transit authority analysts and dispatch controllers with granular
operational insights, directional asymmetry analysis, corridor segment variability,
dwell dynamics, and hop-length travel-time patterns derived from Task 4 SQL & EDA.
"""

import pandas as pd
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


def render_operator_view():
    """Renders the Operator / Analyst Dashboard."""
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin-bottom: 6px;">Transit Operations & Corridor Intelligence</h1>
            <p style="color: #64748b; font-size: 1.05rem; margin: 0;">
                Corridor performance monitoring, directional travel-time asymmetry, segment variability, and dwell dynamics.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Tabs for organized analysis
    tab_overview, tab_directional, tab_segments, tab_dwell, tab_scaling = st.tabs([
        "Route Overview",
        "Directional Asymmetry",
        "Segment Variability (62 High-Variability Segments)",
        "Dwell Dynamics & Dispatch",
        "Hop-Tier & Day-of-Week Trends"
    ])

    # -------------------------------------------------------------
    # TAB 1: ROUTE OVERVIEW
    # -------------------------------------------------------------
    with tab_overview:
        st.markdown("### Corridor Network Summary")
        st.caption("Aggregated telemetry across 3 monitored trunk routes over the full observation period (July–September 2024).")

        # Top KPI cards
        df_routes = load_route_summary()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monitored Routes", "3 Routes", "Routes 10, 12, 46")
        with col2:
            st.metric("Corridor Segments", "300 Segments", "Standard Stops (Seg >= 2)")
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
            "Distinct Trips",
            "Days Monitored",
            "Med Seg Run (s)",
            "Med Dwell (s)",
            "Journey Obs",
            "Med Journey (min)",
            "P10 (min)",
            "P90 (min)"
        ]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("""
            <div style="background-color: #f1f5f9; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 0.9rem; color: #334155;">
                <strong>Corridor Context:</strong>
                <ul style="margin: 4px 0 0 16px; padding: 0;">
                    <li><strong>Route 10</strong>: Direct express trunk connecting Central Railway Station to Airport via Mangilik El Ave (lowest median journey time: 19.9 min).</li>
                    <li><strong>Route 12</strong>: City trunk connecting Central Railway Station to Airport via Kabanbay Batyr Ave (median journey time: 18.8 min).</li>
                    <li><strong>Route 46</strong>: Longest cross-city residential trunk connecting Karasu to Comfort Town (highest median journey time: 26.1 min, P90 of 43.1 min).</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 2: DIRECTIONAL ASYMMETRY
    # -------------------------------------------------------------
    with tab_directional:
        st.markdown("### Directional Travel-Time Asymmetry")
        st.caption("Comparison of travel time distributions between Outbound (Direction 1) and Inbound (Direction 2).")

        df_dir = load_route_direction_summary()

        dir_table = df_dir[[
            "route_short_name",
            "direction_id",
            "distinct_trips",
            "median_journey_min",
            "iqr_journey_sec",
            "p10_journey_min",
            "p90_journey_min",
            "p10_p90_range_min"
        ]].copy()

        dir_table.columns = [
            "Route",
            "Direction",
            "Distinct Trips",
            "Median Journey (min)",
            "IQR (sec)",
            "P10 (min)",
            "P90 (min)",
            "P10-P90 Spread (min)"
        ]

        st.dataframe(dir_table, use_container_width=True, hide_index=True)

        # Visual comparison
        st.markdown("#### Directional Median Journey Time (Minutes)")
        chart_df = df_dir.pivot(index="route_short_name", columns="direction_id", values="median_journey_min")
        chart_df.columns = ["Direction 1 (Outbound)", "Direction 2 (Inbound)"]
        st.bar_chart(chart_df)

        st.markdown("""
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 0.9rem; color: #334155;">
                <strong>Key Directional Findings:</strong>
                <ul style="margin: 4px 0 0 16px; padding: 0;">
                    <li><strong>Route 12 Structural Asymmetry:</strong> Outbound (Direction 1) exhibits a median journey time of <strong>21.0 min</strong> compared to <strong>17.5 min</strong> for Inbound (Direction 2) — a <strong>3.5 min (20.0%) differential</strong> driven by roadway topology and stop spacing.</li>
                    <li><strong>Route 10 Balance:</strong> Route 10 exhibits tight directional parity (20.3 min Outbound vs 19.9 min Inbound, a difference of only 0.4 min / 2.0%).</li>
                    <li><strong>Route 46 Uniformity:</strong> Route 46 maintains consistent median times (25.8 min Outbound vs 26.6 min Inbound), but Direction 2 exhibits higher dispersion (P90 of 44.5 min vs 41.7 min).</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 3: SEGMENT VARIABILITY
    # -------------------------------------------------------------
    with tab_segments:
        st.markdown("### Corridor Segment Performance & Variability")
        st.caption("Detailed segment-by-segment analysis identifying the 62 high-variability corridor segments.")

        df_high_var = load_high_variability_segments()
        df_all_segs = load_segment_summary()

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Total Corridor Segments", f"{len(df_all_segs)} Segments", "Across 3 Routes & 2 Directions")
        with col_metric2:
            st.metric("High-Variability Segments", f"{len(df_high_var)} Segments", "Criteria: N >= 500 & IQR >= 68s")
        with col_metric3:
            pct_high = (len(df_high_var) / len(df_all_segs)) * 100
            st.metric("Corridor Share", f"{pct_high:.1f}%", "Flagged as High-Variability Segments")

        st.markdown("#### High-Variability Segment Inventory")
        filter_route = st.selectbox(
            "Filter Segments by Route",
            options=["All Routes"] + [f"Route {r}" for r in [10, 12, 46]],
            index=0
        )

        filtered_df = df_high_var if filter_route == "All Routes" else df_high_var[
            df_high_var["route_short_name"] == int(filter_route.split()[-1])
        ]

        st.dataframe(
            filtered_df[[
                "route_short_name",
                "direction_id",
                "segment",
                "start_stop_sample",
                "end_stop_sample",
                "n_obs",
                "median_total_time_sec",
                "iqr_total_time_sec",
                "p90_total_time_sec",
                "cv_total_time"
            ]].sort_values("iqr_total_time_sec", ascending=False),
            column_config={
                "route_short_name": "Route",
                "direction_id": "Dir",
                "segment": "Seg #",
                "start_stop_sample": "Origin Stop",
                "end_stop_sample": "Destination Stop",
                "n_obs": "Observations",
                "median_total_time_sec": "Med Time (s)",
                "iqr_total_time_sec": "IQR (s)",
                "p90_total_time_sec": "P90 Time (s)",
                "cv_total_time": "CV"
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("""
            <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 0.9rem; color: #991b1b;">
                <strong>Analyst Guidance:</strong>
                High-variability segments (IQR &ge; 68s) represent physical corridor locations where travel times exhibit substantial variance.
                Dispatch controllers can target these specific segments for headway management, transit signal priority (TSP), or stop-bay enforcement.
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 4: DWELL DYNAMICS
    # -------------------------------------------------------------
    with tab_dwell:
        st.markdown("### Dwell Dynamics & Terminal Dispatch Isolation")
        st.caption("Empirical justification for isolating Segment 1 (terminal dispatch) from standard corridor stops.")

        df_dwell = load_dwell_summary()

        st.dataframe(
            df_dwell[[
                "route_short_name",
                "direction_id",
                "segment_class",
                "n_observations",
                "median_dwell_sec",
                "zero_dwell_pct",
                "dwell_over_30s_pct",
                "dwell_share_of_total_time_pct"
            ]],
            column_config={
                "route_short_name": "Route",
                "direction_id": "Dir",
                "segment_class": "Segment Classification",
                "n_observations": "Observations",
                "median_dwell_sec": "Median Dwell (s)",
                "zero_dwell_pct": "Zero Dwell %",
                "dwell_over_30s_pct": "Dwell > 30s %",
                "dwell_share_of_total_time_pct": "Dwell Share %"
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("""
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 0.9rem; color: #166534;">
                <strong>Methodological Findings (Task 2B / Task 4 Audit):</strong>
                <ul style="margin: 4px 0 0 16px; padding: 0;">
                    <li><strong>Standard Passenger Stops (Segments &ge; 2):</strong> Dwell times reflect routine passenger boarding and alighting, with median dwell times between <strong>22.0 and 27.0 seconds</strong> across routes, accounting for approximately <strong>20% to 23%</strong> of total segment travel time.</li>
                    <li><strong>Terminal Dispatch (Segment 1):</strong> Segment 1 incorporates initial dispatch/terminal holding time and driver layovers, resulting in substantial dwell accumulation (median dwell of <strong>506.5s to 546.0s</strong> on outbound Routes 10 and 46, with P90 exceeding 2,300 seconds).</li>
                    <li><strong>Governance Lock:</strong> In accordance with Task 2B, Segment 1 is preserved in analytical datasets for fleet dispatch monitoring, but strictly excluded from passenger journey starts.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 5: HOP-TIER & DAY-OF-WEEK TRENDS
    # -------------------------------------------------------------
    with tab_scaling:
        st.markdown("### Hop-Tier Scaling & Day-of-Week Patterns")

        col_left, col_right = st.columns(2, gap="large")

        with col_left:
            st.markdown("#### Travel Time by Hop Tier (Segments Traversed)")
            df_hop = load_hop_scaling_summary()
            st.dataframe(
                df_hop[[
                    "hop_tier",
                    "total_journeys",
                    "median_duration_min",
                    "iqr_duration_min",
                    "cv_duration"
                ]],
                column_config={
                    "hop_tier": "Hop Tier (Hops)",
                    "total_journeys": "Journey Obs",
                    "median_duration_min": "Median (min)",
                    "iqr_duration_min": "IQR (min)",
                    "cv_duration": "CV"
                },
                use_container_width=True,
                hide_index=True
            )
            st.caption("Journey duration increases with hop length in the observed data, with hop count serving as the primary predictive driver.")

        with col_right:
            st.markdown("#### Day-of-Week Operational Patterns")
            df_day = load_day_summary()
            st.dataframe(
                df_day[[
                    "day_name",
                    "is_weekend",
                    "total_journeys",
                    "median_duration_min",
                    "iqr_duration_min"
                ]],
                column_config={
                    "day_name": "Day of Week",
                    "is_weekend": "Weekend",
                    "total_journeys": "Journey Obs",
                    "median_duration_min": "Median (min)",
                    "iqr_duration_min": "IQR (min)"
                },
                use_container_width=True,
                hide_index=True
            )
            st.caption("Weekday travel time distributions remain consistent Monday–Friday, with modest variability compression during weekend schedules.")
