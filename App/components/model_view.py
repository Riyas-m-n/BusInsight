"""
BusInsight - Machine Learning Performance Component
Renders model architecture specifications, validation benchmarks, out-of-time test metrics,
and permutation feature importance with non-causal interpretation notices.
"""

import streamlit as st

from ..services.analytics_service import (
    load_model_comparison,
    load_feature_importance,
    load_test_metrics,
    load_model_metadata,
)


def render_model_view():
    """Renders the Model Performance & Evaluation view."""
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #EEF2FF; border: 1px solid #C7D2FE; color: #3730A3; padding: 3px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;">
                🤖 ML Engineering & Benchmarks
            </div>
            <h1 style="margin: 0 0 6px 0;">Machine Learning Architecture & Evaluation</h1>
            <p style="color: #64748B; font-size: 1rem; margin: 0;">
                Empirical benchmarking, out-of-time test evaluation, and permutation feature importance across 14.48M training observations.
            </p>
        </div>
    """, unsafe_allow_html=True)

    metadata = load_model_metadata()
    test_metrics = load_test_metrics()

    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Selected Model",
            value="HistGradientBoosting",
            help="scikit-learn HistGradientBoostingRegressor with squared error loss (L2)."
        )
    with col2:
        st.metric(
            label="Test Set MAE",
            value=f"{test_metrics['selected_model_metrics']['mae_minutes']} min",
            delta=f"-{test_metrics['comparison']['pct_mae_improvement']:.1f}% vs Baseline",
            help=f"{test_metrics['selected_model_metrics']['mae_seconds']}s MAE on out-of-time test partition (2.28M observations)."
        )
    with col3:
        st.metric(
            label="Test R² Score",
            value=f"{test_metrics['selected_model_metrics']['r2_score']:.4f}",
            delta=f"+{test_metrics['comparison']['abs_r2_difference']:.4f} vs Baseline",
            help="Proportion of travel-time variance explained by the model."
        )
    with col4:
        st.metric(
            label="Evaluation Dataset",
            value="14.48M Obs",
            help=f"Train: {metadata['row_counts']['train']:,} | Val: {metadata['row_counts']['val']:,} | Test: {metadata['row_counts']['test']:,}"
        )

    st.markdown("---")

    col_bench, col_imp = st.columns([1.1, 1], gap="large")

    with col_bench:
        st.markdown("### Validation Benchmark Comparison")
        st.caption("Chronological validation split evaluation across candidate models and empirical historical baseline.")

        df_comp = load_model_comparison()
        display_comp = df_comp[[
            "model_name",
            "val_mae_minutes",
            "val_rmse_minutes",
            "val_r2",
            "mae_improvement_pct"
        ]].copy()
        display_comp.columns = [
            "Model Architecture",
            "Val MAE (min)",
            "Val RMSE (min)",
            "Val R²",
            "MAE Imprv %"
        ]

        st.dataframe(display_comp, use_container_width=True, hide_index=True)

        st.markdown("#### Out-of-Time Test Set Evaluation (2,281,911 Obs)")
        test_eval_data = {
            "Metric": ["Sample Size (N)", "MAE (seconds)", "MAE (minutes)", "RMSE (seconds)", "RMSE (minutes)", "R² Score"],
            "Historical Baseline": [
                f"{test_metrics['n_observations']:,}",
                f"{test_metrics['baseline']['mae_seconds']} s",
                f"{test_metrics['baseline']['mae_minutes']} min",
                f"{test_metrics['baseline']['rmse_seconds']} s",
                f"{test_metrics['baseline']['rmse_minutes']} min",
                f"{test_metrics['baseline']['r2_score']:.4f}"
            ],
            "Selected HistGB Model": [
                f"{test_metrics['n_observations']:,}",
                f"{test_metrics['selected_model_metrics']['mae_seconds']} s",
                f"{test_metrics['selected_model_metrics']['mae_minutes']} min",
                f"{test_metrics['selected_model_metrics']['rmse_seconds']} s",
                f"{test_metrics['selected_model_metrics']['rmse_minutes']} min",
                f"{test_metrics['selected_model_metrics']['r2_score']:.4f}"
            ],
            "Delta (% Improvement)": [
                "—",
                f"-{test_metrics['comparison']['abs_mae_difference']} s (-{test_metrics['comparison']['pct_mae_improvement']}%)",
                "-0.21 min",
                f"-{test_metrics['comparison']['abs_rmse_difference']} s (-{test_metrics['comparison']['pct_rmse_improvement']}%)",
                "-0.45 min",
                f"+{test_metrics['comparison']['abs_r2_difference']:.4f}"
            ]
        }
        st.dataframe(test_eval_data, use_container_width=True, hide_index=True)

    with col_imp:
        st.markdown("### Permutation Feature Importance")
        st.caption("Empirical importance calculated by measuring test MAE degradation under feature column permutation.")

        df_fi = load_feature_importance()
        st.dataframe(df_fi, use_container_width=True, hide_index=True)

        st.markdown("""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 0.85rem; color: #334155; line-height: 1.5;">
                <strong>Interpretation & Non-Causality Guardrail:</strong><br>
                Feature importance rankings (e.g. <code>segments_traversed</code> at 81.59%, stop indices at 14.16%) describe empirical predictive associations within the trained model's decision tree splits.
                They do <strong>not</strong> establish physical roadway causality, driver behavior, or external traffic mechanics.
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 14px; border-radius: 4px; margin-top: 12px; font-size: 0.85rem; color: #1E40AF;">
                <strong>Engineering Takeaway:</strong><br>
                The historical median baseline achieved an R² of 0.9171. HistGradientBoosting improved this to 0.9290 (a 6.39% MAE reduction). This highlights that transit distance (hop count) establishes a dominant linear baseline, while non-linear spatial interactions provide a measurable but modest refinement.
            </div>
        """, unsafe_allow_html=True)
