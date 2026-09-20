"""
BusInsight - Main Landing View Component
Renders the product front-door with clear role-based entry paths:
Passenger (primary), Operator / Analyst (protected), and Admin (protected).
"""

import streamlit as st


def render_landing_view():
    """Renders the clean, product-oriented landing page."""
    # Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 2.5rem 1rem 1.5rem 1rem; max-width: 820px; margin: 0 auto;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 4px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem;">
                🚌 Astana Urban Transit Intelligence
            </div>
            <h1 style="font-size: 2.75rem; font-weight: 800; color: #0F172A; letter-spacing: -0.025em; line-height: 1.15; margin: 0 0 0.75rem 0;">
                BusInsight
            </h1>
            <p style="font-size: 1.35rem; font-weight: 600; color: #2563EB; margin: 0 0 1rem 0;">
                Historical Bus Journey Intelligence
            </p>
            <p style="font-size: 1.05rem; color: #475569; line-height: 1.6; margin: 0 auto 2rem auto; max-width: 640px;">
                Estimate historical bus journey times and explore route performance using observed transit operations data from Astana's urban network.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.2rem; font-weight: 700; color: #1E293B; margin: 0;">
                What would you like to do?
            </h3>
        </div>
    """, unsafe_allow_html=True)

    # Three Role Cards
    col_pass, col_ops, col_admin = st.columns(3, gap="medium")

    # 1. PASSENGER (Primary Public Action)
    with col_pass:
        st.markdown("""
            <div style="background: #FFFFFF; border: 2px solid #2563EB; border-radius: 14px; padding: 1.75rem 1.25rem; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.08); position: relative;">
                <div style="position: absolute; top: -12px; right: 16px; background: #2563EB; color: #FFFFFF; font-size: 0.7rem; font-weight: 700; padding: 2px 10px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">
                    Public Access
                </div>
                <div>
                    <div style="font-size: 2.25rem; margin-bottom: 0.75rem;">🚌</div>
                    <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #2563EB; letter-spacing: 0.05em;">
                        Passenger Experience
                    </div>
                    <h3 style="font-size: 1.35rem; font-weight: 700; color: #0F172A; margin: 0.25rem 0 0.5rem 0;">
                        Plan a Journey
                    </h3>
                    <p style="font-size: 0.9rem; color: #64748B; line-height: 1.5; margin: 0 0 1.25rem 0;">
                        Estimate travel time between bus stops using historical transit observations and gradient-boosted ML.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚌 Plan My Journey", key="btn_hero_passenger", use_container_width=True, type="primary"):
            st.session_state["active_role"] = "passenger"
            st.rerun()

    # 2. OPERATOR / ANALYST (Protected)
    with col_ops:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-top: 4px solid #0D9488; border-radius: 14px; padding: 1.75rem 1.25rem; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); position: relative;">
                <div style="position: absolute; top: -12px; right: 16px; background: #F1F5F9; border: 1px solid #CBD5E1; color: #475569; font-size: 0.7rem; font-weight: 700; padding: 2px 10px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">
                    🔒 Protected
                </div>
                <div>
                    <div style="font-size: 2.25rem; margin-bottom: 0.75rem;">📊</div>
                    <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #0D9488; letter-spacing: 0.05em;">
                        Operator / Analyst
                    </div>
                    <h3 style="font-size: 1.35rem; font-weight: 700; color: #0F172A; margin: 0.25rem 0 0.5rem 0;">
                        Corridor Operations
                    </h3>
                    <p style="font-size: 0.9rem; color: #64748B; line-height: 1.5; margin: 0 0 1.25rem 0;">
                        Analyze route performance, directional asymmetry, 62 high-variability segments, and dwell dynamics.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("📊 Open Operations", key="btn_hero_operator", use_container_width=True):
            st.session_state["active_role"] = "operator"
            st.rerun()

    # 3. ADMIN (Protected)
    with col_admin:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-top: 4px solid #475569; border-radius: 14px; padding: 1.75rem 1.25rem; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); position: relative;">
                <div style="position: absolute; top: -12px; right: 16px; background: #F1F5F9; border: 1px solid #CBD5E1; color: #475569; font-size: 0.7rem; font-weight: 700; padding: 2px 10px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">
                    🔐 System Owner
                </div>
                <div>
                    <div style="font-size: 2.25rem; margin-bottom: 0.75rem;">🔐</div>
                    <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.05em;">
                        Administrator
                    </div>
                    <h3 style="font-size: 1.35rem; font-weight: 700; color: #0F172A; margin: 0.25rem 0 0.5rem 0;">
                        Manage BusInsight
                    </h3>
                    <p style="font-size: 0.9rem; color: #64748B; line-height: 1.5; margin: 0 0 1.25rem 0;">
                        Manage authorized users, access levels, system overview, and future platform capabilities.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔐 Admin Login", key="btn_hero_admin", use_container_width=True):
            st.session_state["active_role"] = "admin"
            st.rerun()

    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)

    # Quick Platform Stats Bar
    st.markdown("""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 1rem; text-align: center;">
                <div>
                    <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B;">Network Corridors</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #0F172A;">3 Routes (10, 12, 46)</div>
                </div>
                <div style="border-left: 1px solid #E2E8F0; padding-left: 1rem;">
                    <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B;">Physical Stops</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #0F172A;">201 Stops &bull; 300 Segments</div>
                </div>
                <div style="border-left: 1px solid #E2E8F0; padding-left: 1rem;">
                    <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B;">Telemetry Scope</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #0F172A;">15.28M Journey Obs</div>
                </div>
                <div style="border-left: 1px solid #E2E8F0; padding-left: 1rem;">
                    <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B;">ML Architecture</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #0F172A;">HistGB Regressor (L2)</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Project Research & Documentation Link
    st.markdown("""
        <div style="text-align: center; padding: 1rem; color: #64748B; font-size: 0.9rem;">
            Interested in the technical methodology, model benchmarks, or dataset attribution?
        </div>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        if st.button("📚 Explore Project Documentation & Methodology", key="btn_hero_project", use_container_width=True):
            st.session_state["active_role"] = "project"
            st.rerun()
