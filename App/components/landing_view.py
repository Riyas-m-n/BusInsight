"""
BusInsight - Main Landing View Component
Renders the compact product front-door fitting comfortably into a single desktop viewport
with clear role-based entry paths: Passenger, Operator / Analyst, and Admin.
"""

import streamlit as st


def render_landing_view():
    """Renders the clean, compact, product-oriented landing page."""
    # 1. Compact Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 0.5rem 1rem 0.4rem 1rem; max-width: 800px; margin: 0 auto;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 2px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.35rem;">
                🚌 Astana Urban Transit Intelligence
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; color: #0F172A; letter-spacing: -0.025em; line-height: 1.1; margin: 0 0 0.2rem 0;">
                BusInsight
            </h1>
            <p style="font-size: 1.05rem; font-weight: 600; color: #2563EB; margin: 0 0 0.25rem 0;">
                Historical Bus Journey Intelligence
            </p>
            <p style="font-size: 0.88rem; color: #475569; line-height: 1.4; margin: 0 auto 0.5rem auto; max-width: 600px;">
                Estimate historical bus journey times and explore route performance using observed transit operations data from Astana's urban network.
            </p>
            <div style="font-size: 0.95rem; font-weight: 700; color: #1E293B; margin-bottom: 0.4rem;">
                What would you like to do?
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Three Role Cards in One Horizontal Row
    col_pass, col_ops, col_admin = st.columns(3, gap="medium")

    # 1. PASSENGER (Primary Public Action)
    with col_pass:
        st.markdown("""
            <div style="background: #FFFFFF; border: 2px solid #2563EB; border-radius: 10px; padding: 0.9rem 0.85rem; position: relative; box-shadow: 0 4px 10px -2px rgba(37, 99, 235, 0.08); margin-bottom: 0.4rem;">
                <div style="position: absolute; top: -9px; right: 12px; background: #2563EB; color: #FFFFFF; font-size: 0.65rem; font-weight: 700; padding: 1px 8px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.04em;">
                    Public Access
                </div>
                <div style="font-size: 1.5rem; margin-bottom: 0.2rem;">🚌</div>
                <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #2563EB; letter-spacing: 0.04em;">
                    Passenger Experience
                </div>
                <h3 style="font-size: 1.08rem; font-weight: 700; color: #0F172A; margin: 0.1rem 0 0.25rem 0;">
                    Plan a Journey
                </h3>
                <p style="font-size: 0.8rem; color: #64748B; line-height: 1.35; margin: 0; min-height: 42px;">
                    Estimate travel time between bus stops using historical transit observations and gradient-boosted ML.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚌 Plan My Journey", key="btn_hero_passenger", use_container_width=True, type="primary"):
            st.session_state["active_role"] = "passenger"
            st.rerun()

    # 2. OPERATOR / ANALYST (Protected)
    with col_ops:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid #0D9488; border-radius: 10px; padding: 0.9rem 0.85rem; position: relative; box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.04); margin-bottom: 0.4rem;">
                <div style="position: absolute; top: -9px; right: 12px; background: #F1F5F9; border: 1px solid #CBD5E1; color: #475569; font-size: 0.65rem; font-weight: 700; padding: 1px 8px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.04em;">
                    🔒 Protected
                </div>
                <div style="font-size: 1.5rem; margin-bottom: 0.2rem;">📊</div>
                <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #0D9488; letter-spacing: 0.04em;">
                    Operator / Analyst
                </div>
                <h3 style="font-size: 1.08rem; font-weight: 700; color: #0F172A; margin: 0.1rem 0 0.25rem 0;">
                    Corridor Operations
                </h3>
                <p style="font-size: 0.8rem; color: #64748B; line-height: 1.35; margin: 0; min-height: 42px;">
                    Analyze route performance, directional asymmetry, 62 high-variability segments, and dwell dynamics.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("📊 Open Operations", key="btn_hero_operator", use_container_width=True):
            st.session_state["active_role"] = "operator"
            st.rerun()

    # 3. ADMIN (Protected)
    with col_admin:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3px solid #475569; border-radius: 10px; padding: 0.9rem 0.85rem; position: relative; box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.04); margin-bottom: 0.4rem;">
                <div style="position: absolute; top: -9px; right: 12px; background: #F1F5F9; border: 1px solid #CBD5E1; color: #475569; font-size: 0.65rem; font-weight: 700; padding: 1px 8px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.04em;">
                    🔐 System Owner
                </div>
                <div style="font-size: 1.5rem; margin-bottom: 0.2rem;">🔐</div>
                <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.04em;">
                    Administrator
                </div>
                <h3 style="font-size: 1.08rem; font-weight: 700; color: #0F172A; margin: 0.1rem 0 0.25rem 0;">
                    Manage BusInsight
                </h3>
                <p style="font-size: 0.8rem; color: #64748B; line-height: 1.35; margin: 0; min-height: 42px;">
                    Manage authorized users, access levels, system overview, and future platform capabilities.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔐 Admin Login", key="btn_hero_admin", use_container_width=True):
            st.session_state["active_role"] = "admin"
            st.rerun()

    # 3. Quick Platform Scope Bar
    st.markdown("""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.55rem 0.85rem; margin: 0.65rem 0 0.45rem 0;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 0.5rem; text-align: center;">
                <div>
                    <div style="font-size: 0.68rem; font-weight: 600; text-transform: uppercase; color: #64748B;">Network Corridors</div>
                    <div style="font-size: 1.12rem; font-weight: 700; color: #0F172A;">3 Routes (10, 12, 46)</div>
                </div>
                <div style="border-left: 1px solid #CBD5E1; padding-left: 0.75rem;">
                    <div style="font-size: 0.68rem; font-weight: 600; text-transform: uppercase; color: #64748B;">Physical Stops</div>
                    <div style="font-size: 1.12rem; font-weight: 700; color: #0F172A;">201 Stops &bull; 300 Segments</div>
                </div>
                <div style="border-left: 1px solid #CBD5E1; padding-left: 0.75rem;">
                    <div style="font-size: 0.68rem; font-weight: 600; text-transform: uppercase; color: #64748B;">Telemetry Scope</div>
                    <div style="font-size: 1.12rem; font-weight: 700; color: #0F172A;">15.28M Journey Obs</div>
                </div>
                <div style="border-left: 1px solid #CBD5E1; padding-left: 0.75rem;">
                    <div style="font-size: 0.68rem; font-weight: 600; text-transform: uppercase; color: #64748B;">ML Architecture</div>
                    <div style="font-size: 1.12rem; font-weight: 700; color: #0F172A;">HistGB Regressor (L2)</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 4. Project Research & Documentation Secondary Action
    st.markdown("""
        <div style="text-align: center; color: #64748B; font-size: 0.8rem; margin: 0.35rem 0 0.25rem 0;">
            Interested in the technical methodology, model benchmarks, or dataset attribution?
        </div>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        if st.button("📚 Explore Project Documentation & Methodology", key="btn_hero_project", use_container_width=True):
            st.session_state["active_role"] = "project"
            st.rerun()
