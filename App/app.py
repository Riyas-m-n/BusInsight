"""
BusInsight - Urban Transit Intelligence Web Application
Main entry point and application shell for Streamlit.
Organized into three distinct product tiers:
1. 🚌 Passenger (Journey Estimator)
2. 📊 Operator / Analyst (Corridor Intelligence, Protected)
3. 🔐 Administrator (System Management, Protected)
Plus 📚 Project (ML Architecture, Governance, Attribution & Roadmap) and Landing Front Door.
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

from App.components.landing_view import render_landing_view
from App.components.passenger_view import render_passenger_view
from App.components.operator_view import render_operator_view
from App.components.admin_view import render_admin_view
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


def init_session_state():
    """Initialize application session state variables."""
    if "active_role" not in st.session_state:
        st.session_state["active_role"] = "landing"
    if "operator_auth" not in st.session_state:
        st.session_state["operator_auth"] = False
    if "admin_auth" not in st.session_state:
        st.session_state["admin_auth"] = False


def main():
    load_custom_css()
    init_session_state()

    # Map between internal role keys and sidebar display options
    role_options = [
        "🏠 Home / Overview",
        "🚌 Passenger (Journey Estimator)",
        "📊 Operator / Analyst (Protected)",
        "🔐 Administrator (Protected)",
        "📚 Project (Model & Governance)"
    ]

    role_to_display = {
        "landing": "🏠 Home / Overview",
        "passenger": "🚌 Passenger (Journey Estimator)",
        "operator": "📊 Operator / Analyst (Protected)",
        "admin": "🔐 Administrator (Protected)",
        "project": "📚 Project (Model & Governance)"
    }

    display_to_role = {v: k for k, v in role_to_display.items()}

    current_display = role_to_display.get(st.session_state["active_role"], "🏠 Home / Overview")
    current_index = role_options.index(current_display) if current_display in role_options else 0

    # Sidebar Navigation & Product Metadata
    with st.sidebar:
        st.markdown("""
            <div style="padding: 10px 0 16px 0;">
                <h2 style="color: #1E3A8A; margin: 0; font-size: 1.6rem; display: flex; align-items: center; gap: 8px;">
                    🚌 BusInsight
                </h2>
                <p style="color: #64748B; font-size: 0.85rem; margin: 3px 0 0 0; font-weight: 500;">
                    Astana Urban Transit Intelligence
                </p>
            </div>
        """, unsafe_allow_html=True)

        selected_display = st.radio(
            "Product Navigation",
            options=role_options,
            index=current_index,
            label_visibility="collapsed"
        )

        selected_role = display_to_role[selected_display]
        if selected_role != st.session_state["active_role"]:
            st.session_state["active_role"] = selected_role
            st.rerun()

        st.markdown("---")

        # System telemetry metadata
        st.markdown("""
            <div style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 6px;">Corridor Scope</div>
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
            "**Historical Prototype Notice**: Predictions reflect historical transit distributions (July–Sept 2024) "
            "using strictly pre-journey features. Not a live GPS tracking feed or dynamic traffic ETA."
        )

    # Main Area Router
    active_role = st.session_state.get("active_role", "landing")

    if active_role == "landing":
        render_landing_view()

    elif active_role == "passenger":
        render_passenger_view()

    elif active_role == "operator":
        render_operator_view()

    elif active_role == "admin":
        render_admin_view()

    elif active_role == "project":
        render_project_shell()


def render_project_shell():
    """Renders the top-level Project documentation container."""
    tab_model, tab_methodology = st.tabs([
        "🤖 Model Architecture & Evaluation",
        "📖 Methodology, Attribution & Roadmap"
    ])

    with tab_model:
        render_model_view()

    with tab_methodology:
        render_methodology_view()


if __name__ == "__main__":
    main()
