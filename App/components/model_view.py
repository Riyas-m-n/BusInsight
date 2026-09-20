"""
BusInsight - Model Performance & Evaluation Component
Displays architecture specifications, validation benchmarks, out-of-time test metrics,
and permutation feature importance for the machine-learning pipeline.
"""

import pandas as pd
import streamlit as st

from ..services.analytics_service import (
    load_model_comparison,
    load_feature_importance,
    load_test_metrics,
    load_model_metadata,
)


def render_model_view():
    """Renders the Model Performance & Evaluation page."""
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin-bottom: 6px;">Machine Learning Architecture & Evaluation</h1>
            <p style="color: #64748b; font-size: 1.05rem; margin: 0;">
                Empirical benchmarking, out-of-time test evaluation, and permutation feature importance.
            </p>
        </div>
    """, unsafe_allow_html=True)

    metadata = load_model_metadata()
    test_metrics = load_test_metrics()

    # Top KPI cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Selected Model",
            value="HistGradientBoosting",
            help="scikit-learn HistGradientBoostingRegressor with squared error loss."
        )
    with col2:
        st.metric(
            label="Test MAE",
            value=f"{test_metrics['selected_model_metrics']['mae_minutes']} min",
            delta=f"-{test_metrics['comparison']['pct_mae_improvement']:.1f}% vs Baseline",
            help=f"{test_metrics['selected_model_metrics']['mae_seconds']}s MAE on out-of-time test partition."
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
            label="Total Dataset",
            value="14.48M Obs",
            help=f"Train: {metadata['row_counts']['train']:,} | Val: {metadata['row_counts']['val']:,} | Test: {metadata['row_counts']['test']:,}"
        )

    st.markdown("---")

    col_bench, col_imp = st.columns([1, 1], gap="large")

    with col_bench:
        st.markdown("### Validation Benchmark Comparison")
        st.caption("Chronological validation split evaluation across candidate models and historical baseline.")

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

        st.markdown("#### Out-of-Time Test Set Evaluation")
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
            "Performance Delta": [
                "—",
                f"-{test_metrics['comparison']['abs_mae_difference']} s (-{test_metrics['comparison']['pct_mae_improvement']}%)",
                "-0.21 min",
                f"-{test_metrics['comparison']['abs_rmse_difference']} s (-{test_metrics['comparison']['pct_rmse_improvement']}%)",
                "-0.44 min",
                f"+{test_metrics['comparison']['abs_r2_difference']:.4f}"
            ]
        }
        st.dataframe(pd.DataFrame(test_eval_data), use_container_width=True, hide_index=True)

    with col_imp:
        st.markdown("### Permutation Feature Importance")
        st.caption("Contribution of each pre-journey feature to model error reduction (measured on validation partition). Reflects predictive association within the model, not operational causality.")

        df_feat = load_feature_importance()
        feat_chart_df = df_feat.set_index("feature")["relative_importance_pct"]
        st.bar_chart(feat_chart_df)

        st.dataframe(
            df_feat[[
                "feature",
                "importance_mean_mae_drop_seconds",
                "relative_importance_pct"
            ]],
            column_config={
                "feature": "Feature Name",
                "importance_mean_mae_drop_seconds": "Mean MAE Impact (s)",
                "relative_importance_pct": "Relative Share (%)"
            },
            use_container_width=True,
            hide_index=True
        )

    # Narrative Technical Explanation
    st.markdown("""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-top: 20px;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">Engineering & Modeling Insights</h4>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.95rem; color: #475569; line-height: 1.6;">
                <li><strong>Hop Distance Dominance:</strong> <code>segments_traversed</code> accounts for <strong>81.59%</strong> of model importance, reflecting the predictive relationship between journey duration and corridor hop count.</li>
                <li><strong>Spatial Adjustments:</strong> The stop index identifiers (<code>start_stop_idx</code> at 7.35% and <code>dest_stop_idx</code> at 6.81%) provide localized corrections for corridor segments with higher dwell or slower progression.</li>
                <li><strong>Strict Pre-Journey Guardrails:</strong> Zero post-journey features or live telemetry were incorporated, ensuring strict adherence to real-world prediction timing and zero test data contamination.</li>
                <li><strong>Predictive Association, Not Causality:</strong> Feature importance ranks relative predictive utility within the trained tree model; it does not measure or prove physical traffic causality.</li>
                <li><strong>Linear vs Tree Modeling:</strong> Ridge Regression underperformed the historical baseline (MAE of 4.13 min vs 3.38 min), demonstrating that transit travel-time behavior has non-linear spatial interactions that require tree-based partitioning.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
