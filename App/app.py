"""
BusInsight - Urban Transit Intelligence Web Application
Main entry point and application shell for Streamlit.
Integrates Passenger Journey Estimation, Operations Dashboard, ML Performance,
and Methodology Documentation.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure project root and App directory are on Python path
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from App.components.passenger_view import render_passenger_view
from App.components.operator_view import render_operator_view
from App.components.model_view import render_model_view
from App.components.methodology_view import render_methodology_view

# Streamlit Page Configuration
st.set_page_config(
    page_title="BusInsight | Astana Transit Intelligence",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """Inject custom transit-themed CSS stylesheet."""
    css_file = APP_DIR / "styles" / "main.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    load_custom_css()

    # Sidebar Navigation & Branding
    with st.sidebar:
        st.markdown("""
            <div style="padding: 10px 0 20px 0;">
                <h2 style="color: #1E3A8A; margin: 0; font-size: 1.6rem; display: flex; align-items: center; gap: 8px;">
                    🚌 BusInsight
                </h2>
                <p style="color: #64748B; font-size: 0.85rem; margin: 2px 0 0 0;">
                    Astana Urban Transit Intelligence
                </p>
            </div>
        """, unsafe_allow_html=True)

        page_selection = st.radio(
            "Navigation",
            options=[
                "Passenger Estimator",
                "Operations Dashboard",
                "ML Performance",
                "Methodology & Governance"
            ],
            format_func=lambda p: {
                "Passenger Estimator": "🧭 Passenger Estimator",
                "Operations Dashboard": "📊 Operations Dashboard",
                "ML Performance": "🤖 ML Performance",
                "Methodology & Governance": "📖 Methodology & Governance"
            }[p],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")

        # System telemetry metadata
        st.markdown("""
            <div style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
                <div style="font-weight: 600; color: #1e293b; margin-bottom: 6px;">Network Scope</div>
                <div>📍 <strong>City:</strong> Astana, Kazakhstan</div>
                <div>🚌 <strong>Routes:</strong> 10, 12, 46</div>
                <div>🛣️ <strong>Segments:</strong> 300 Physical Stops</div>
                <div>📈 <strong>Telemetry:</strong> 15.28M Journey Obs</div>
                <div>⚙️ <strong>Model:</strong> HistGB Regressor (L2)</div>
                <div>🔒 <strong>Status:</strong> Validated & Locked</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption(
            "**Historical Prototype Notice**: Predictions reflect historical distributions (July–Sept 2024) "
            "using strictly pre-journey features. Not a live GPS tracking feed."
        )

    # Main Application Header Banner
    st.markdown("""
        <div class="businsight-header">
            <h1>BusInsight Transit Analytics</h1>
            <p>Empirical performance intelligence and predictive travel-time estimation for Astana's urban bus network.</p>
        </div>
    """, unsafe_allow_html=True)

    # Route to selected page
    if page_selection == "Passenger Estimator":
        render_passenger_view()
    elif page_selection == "Operations Dashboard":
        render_operator_view()
    elif page_selection == "ML Performance":
        render_model_view()
    elif page_selection == "Methodology & Governance":
        render_methodology_view()


if __name__ == "__main__":
    main()
