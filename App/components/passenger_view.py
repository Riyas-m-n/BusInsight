"""
BusInsight - Passenger Journey Estimator Component
Renders the interactive pre-journey travel time estimation interface with
dependent stop selections, model inference, baseline comparison, and transparency notices.
"""

from datetime import date, datetime
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
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="margin-bottom: 6px;">Passenger Journey-Time Estimator</h1>
            <p style="color: #64748b; font-size: 1.05rem; margin: 0;">
                Pre-journey travel time estimation powered by gradient-boosted historical regression.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Informational banner
    st.info(
        "**Historical Pre-Journey Prototype**: This tool provides travel-time estimates derived from "
        "historical transit telemetry using 10 strictly pre-journey features. "
        "It does not use live GPS tracking, live bus positions, or real-time traffic data.",
        icon="ℹ️"
    )

    col_form, col_results = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("### 1. Select Journey Parameters")

        # 1. Route Selector
        routes = get_available_routes()
        route_options = {r: f"Route {r} — {get_route_info(r)['corridor']}" for r in routes}
        selected_route = st.selectbox(
            "Transit Route",
            options=routes,
            format_func=lambda r: route_options[r],
            help="Select one of the three monitored Astana transit corridors."
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
            s["segment"]: f"Stop: {s['stop_name']} (Seg #{s['segment']})"
            for s in boarding_stops
        }
        selected_start_segment = st.selectbox(
            "Boarding Stop (Origin)",
            options=[s["segment"] for s in boarding_stops],
            format_func=lambda seg: boarding_options[seg],
            help="Select your boarding stop. Note: Terminal dispatch segment 1 is excluded from origin stops."
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
            d["segment"]: f"Stop: {d['stop_name']} (+{d['segments_traversed']} hops)"
            for d in destination_stops
        }
        selected_dest_segment = st.selectbox(
            "Destination Stop",
            options=[d["segment"] for d in destination_stops],
            format_func=lambda seg: dest_options[seg],
            help="Select your destination stop along the route."
        )

        selected_dest_stop = next(d for d in destination_stops if d["segment"] == selected_dest_segment)

        # 5. Travel Date Selector
        st.markdown("#### Travel Date")
        selected_date = st.date_input(
            "Planned Travel Date",
            value=date(2024, 8, 14),
            help="Date determines day-of-week, weekend indicator, and seasonal calendar features."
        )

        day_name = selected_date.strftime("%A")
        is_wknd = selected_date.weekday() in [5, 6]
        st.caption(f"Selected: **{day_name}** ({'Weekend' if is_wknd else 'Weekday'})")

    with col_results:
        st.markdown("### 2. Journey Estimation Results")

        # Run Prediction
        prediction_result = predict_journey_duration(
            route_short_name=selected_route,
            direction_id=selected_direction,
            start_stop_id=selected_start_stop["stop_id"],
            destination_stop_id=selected_dest_stop["stop_id"],
            start_segment=selected_start_segment,
            destination_segment=selected_dest_segment,
            journey_date=selected_date
        )

        # Baseline Historical Lookup
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

            # Key Metric Display
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                            border-radius: 12px; padding: 24px; color: white; margin-bottom: 20px;
                            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);">
                    <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8;">
                        Estimated Travel Time
                    </div>
                    <div style="font-size: 2.75rem; font-weight: 800; color: #38bdf8; line-height: 1.1; margin: 6px 0;">
                        {pred_min:.1f} <span style="font-size: 1.25rem; font-weight: 500; color: #cbd5e1;">min</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #94a3b8;">
                        ≈ {int(pred_sec)} seconds &nbsp;|&nbsp; <strong>{hops}</strong> corridor segments traversed
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Secondary comparison metrics
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric(
                    label="Model Test Error",
                    value="3.2 min",
                    delta="Test MAE (189.5s)",
                    delta_color="off",
                    help="Historical Mean Absolute Error (MAE) measured on the out-of-time test set (2.28M observations). Note: This is an aggregate historical model error metric, not an individual prediction uncertainty bound."
                )
            with m_col2:
                base_min = baseline_result["baseline_median_minutes"]
                if base_min is not None:
                    delta_val = round(pred_min - base_min, 1)
                    st.metric(
                        label="Historical Median",
                        value=f"{base_min:.1f} min",
                        delta=f"{delta_val:+.1f} min vs model",
                        delta_color="inverse",
                        help=f"Empirical median from {baseline_result['sample_count']:,} historical observations."
                    )
                else:
                    st.metric(label="Historical Median", value="N/A")
            with m_col3:
                st.metric(
                    label="Corridor Distance",
                    value=f"{hops} hops",
                    help=f"Segments traversed from Segment {selected_start_segment} to {selected_dest_segment}."
                )

            # Journey Summary Card
            st.markdown("#### Journey Details")
            st.markdown(f"""
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #64748b; font-size: 0.9rem;">Origin Stop</span>
                        <span style="font-weight: 600; font-size: 0.9rem;">{selected_start_stop['stop_name']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #64748b; font-size: 0.9rem;">Destination Stop</span>
                        <span style="font-weight: 600; font-size: 0.9rem;">{selected_dest_stop['stop_name']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #64748b; font-size: 0.9rem;">Corridor Span</span>
                        <span style="font-weight: 600; font-size: 0.9rem;">Segment #{selected_start_segment} → #{selected_dest_segment}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 0.9rem;">Historical Sample Basis</span>
                        <span style="font-weight: 600; font-size: 0.9rem;">{baseline_result.get('sample_count', 0):,} observations</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Model feature vector expander
            with st.expander("View Encoded Pre-Journey Features (Auditing)"):
                st.json(prediction_result.get("feature_vector_dict", {}))

        else:
            st.error(f"Prediction Error: {prediction_result.get('error', 'Unknown error')}")

        # Transparency / Disclaimer Box
        st.markdown("""
            <div style="background-color: #fefce8; border-left: 4px solid #eab308; padding: 12px 14px; border-radius: 4px; margin-top: 16px; font-size: 0.85rem; color: #713f12;">
                <strong>Methodology & Limitations Notice:</strong>
                <ul style="margin: 4px 0 0 16px; padding: 0;">
                    <li>Predictions are generated solely from 10 strictly pre-journey features (hop count, stop indices, day of week, calendar month).</li>
                    <li>No post-journey knowledge or live telematics are used (zero data leakage).</li>
                    <li>Terminal dispatch (Segment 1) is excluded from origin choices due to operational layover characteristics.</li>
                    <li>Actual travel times may fluctuate due to localized incidents, weather, or operational variations.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
