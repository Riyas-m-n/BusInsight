"""
BusInsight - Passenger Journey Estimator Component
Renders the primary, public-facing travel-time estimation interface with
cascading selectors, prominent journey duration result, and empirical error framing.
"""

from datetime import date
import streamlit as st

from ..services.metadata_service import (
    get_available_routes,
    get_route_info,
    get_available_directions,
    get_boarding_stops,
    get_destination_stops,
)
from ..services.model_service import predict_journey_duration
from ..services.baseline_service import get_baseline_estimate


def render_passenger_view():
    """Renders the Passenger Journey Estimator page."""
    # Top Section Intro
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 3px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;">
                🚌 Public Passenger Planner
            </div>
            <h1 style="margin: 0 0 6px 0; font-size: 2.1rem; color: #0F172A;">Plan a Bus Journey</h1>
            <p style="color: #64748B; font-size: 1.05rem; margin: 0;">
                Select your corridor and stops to estimate travel time derived from historical Astana transit observations.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_form, col_results = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("### 1. Journey Parameters")

        # 1. Route Selector
        routes = get_available_routes()
        route_options = {r: f"Route {r} — {get_route_info(r)['corridor']}" for r in routes}
        selected_route = st.selectbox(
            "Transit Route",
            options=routes,
            format_func=lambda r: route_options[r],
            help="Select one of the three monitored Astana transit trunk corridors."
        )

        route_info = get_route_info(selected_route)
        st.caption(f"_{route_info['description']}_")

        # 2. Direction Selector
        directions = get_available_directions(selected_route)
        dir_labels = {
            1: "Direction 1 (Outbound)",
            2: "Direction 2 (Inbound)"
        }
        selected_direction = st.selectbox(
            "Direction of Travel",
            options=directions,
            format_func=lambda d: dir_labels.get(d, f"Direction {d}"),
            help="Select outbound or inbound transit corridor direction."
        )

        # 3. Boarding Stop Selector (Segments >= 2)
        boarding_stops = get_boarding_stops(selected_route, selected_direction)
        if not boarding_stops:
            st.error("No valid boarding stops found for this route and direction.")
            return

        boarding_options = {
            s["segment"]: f"{s['stop_name']} (Stop #{s['segment']})"
            for s in boarding_stops
        }
        selected_start_segment = st.selectbox(
            "Boarding Stop (Origin)",
            options=[s["segment"] for s in boarding_stops],
            format_func=lambda seg: boarding_options[seg],
            help="Select your boarding stop. Note: Terminal dispatch (Segment 1) is excluded from origin options per operational layover isolation."
        )

        selected_start_stop = next(s for s in boarding_stops if s["segment"] == selected_start_segment)

        # 4. Destination Stop Selector (Must be downstream, destination_segment >= start_segment)
        destination_stops = get_destination_stops(
            selected_route,
            selected_direction,
            selected_start_segment
        )

        if not destination_stops:
            st.warning("No downstream destination stops available for this boarding stop.")
            return

        dest_options = {
            d["segment"]: f"{d['stop_name']} (+{d['segments_traversed']} stops)"
            for d in destination_stops
        }
        selected_dest_segment = st.selectbox(
            "Destination Stop",
            options=[d["segment"] for d in destination_stops],
            format_func=lambda seg: dest_options[seg],
            help="Select your destination stop along the route corridor."
        )

        selected_dest_stop = next(d for d in destination_stops if d["segment"] == selected_dest_segment)

        # 5. Travel Date Selector
        selected_date = st.date_input(
            "Planned Travel Date",
            value=date(2024, 8, 14),
            help="Date determines day-of-week, weekend indicator, and monthly seasonal calendar features."
        )

        day_name = selected_date.strftime("%A")
        is_wknd = selected_date.weekday() in [5, 6]
        st.caption(f"Operating schedule basis: **{day_name}** ({'Weekend' if is_wknd else 'Weekday'})")

    with col_results:
        st.markdown("### 2. Estimated Travel Time")

        # Execute Prediction
        prediction_result = predict_journey_duration(
            route_short_name=selected_route,
            direction_id=selected_direction,
            start_stop_id=selected_start_stop["stop_id"],
            destination_stop_id=selected_dest_stop["stop_id"],
            start_segment=selected_start_segment,
            destination_segment=selected_dest_segment,
            journey_date=selected_date
        )

        # Lookup Baseline
        baseline_result = get_baseline_estimate(
            route_short_name=selected_route,
            direction_id=selected_direction,
            start_segment=selected_start_segment,
            destination_segment=selected_dest_segment
        )

        if prediction_result["success"]:
            pred_sec = prediction_result["predicted_seconds"]
            pred_min = prediction_result["predicted_minutes"]
            hops = prediction_result["segments_traversed"]
            base_min = baseline_result["baseline_median_minutes"]

            # Dominant Primary Journey Result Card
            st.markdown(f"""
                <div style="background: #FFFFFF; border: 2px solid #2563EB; border-radius: 14px; padding: 24px; margin-bottom: 20px; box-shadow: 0 8px 16px -4px rgba(37, 99, 235, 0.1);">
                    <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; color: #2563EB; margin-bottom: 4px;">
                        YOUR JOURNEY &bull; ROUTE {selected_route} ({dir_labels.get(selected_direction, '')})
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 16px;">
                        {selected_start_stop['stop_name']} &rarr; {selected_dest_stop['stop_name']}
                    </div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">
                        Estimated Journey Time
                    </div>
                    <div style="font-size: 3.6rem; font-weight: 800; color: #1E40AF; line-height: 1.05; margin: 4px 0 8px 0;">
                        {pred_min:.0f} <span style="font-size: 1.35rem; font-weight: 600; color: #475569;">min</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #64748B;">
                        &asymp; {int(pred_sec)} seconds &bull; <strong>{hops}</strong> corridor segments ({hops} stops)
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Secondary Context Metrics
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.metric(
                    label="Model Test Error",
                    value="MAE: 3.2 min",
                    help="Historical Mean Absolute Error measured across the out-of-time test set (2.28M observations). This is an aggregate model error metric, not an individual prediction uncertainty interval."
                )
                st.caption("_Aggregate error across historical test set; not an individual journey uncertainty range._")

            with m_col2:
                if base_min is not None:
                    delta_val = round(pred_min - base_min, 1)
                    st.metric(
                        label="Historical Median Baseline",
                        value=f"{base_min:.1f} min",
                        delta=f"{delta_val:+.1f} min vs model",
                        delta_color="inverse",
                        help=f"Empirical median calculated from {baseline_result['sample_count']:,} historical observations."
                    )
                    st.caption(f"_{baseline_result['sample_count']:,} historical training observations for this OD pair._")
                else:
                    st.metric(label="Historical Median Baseline", value="N/A")
                    st.caption("_No exact segment-pair samples in historical baseline lookup._")

            # Compact Disclaimer
            st.markdown("""
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; padding: 12px 14px; border-radius: 6px; margin-top: 18px; font-size: 0.85rem; color: #334155; line-height: 1.5;">
                    <strong>Historical predictive prototype</strong> &mdash; this estimate is based on historical transit observations and is not live bus tracking or real-time ETA. Predictions reflect observed normal operating conditions using strictly pre-journey features.
                </div>
            """, unsafe_allow_html=True)

        else:
            st.error(f"Prediction Error: {prediction_result.get('error', 'Unknown error')}")
