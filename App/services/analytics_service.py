"""
BusInsight - Analytics & Reporting Service
Loads and provides cached access to Task 4 exploratory data analysis summaries
and Task 3 machine learning model evaluation metrics.
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
ML_DIR = PROJECT_ROOT / "ML"


@st.cache_data
def load_route_summary() -> pd.DataFrame:
    """Load overall route-level summary."""
    return pd.read_csv(DATA_DIR / "eda_route_summary.csv")


@st.cache_data
def load_route_direction_summary() -> pd.DataFrame:
    """Load route-direction asymmetry summary."""
    return pd.read_csv(DATA_DIR / "eda_route_direction_summary.csv")


@st.cache_data
def load_segment_summary() -> pd.DataFrame:
    """Load detailed corridor segment statistics including high-variability flags."""
    return pd.read_csv(DATA_DIR / "eda_segment_summary.csv")


@st.cache_data
def load_high_variability_segments() -> pd.DataFrame:
    """Filter segments to the 62 high-variability corridor segments (N >= 500, IQR >= 68s)."""
    df = load_segment_summary()
    return df[df["is_high_variability_segment"] == True].copy()


@st.cache_data
def load_dwell_summary() -> pd.DataFrame:
    """Load dwell dynamics summary comparing terminal dispatch vs standard corridor stops."""
    return pd.read_csv(DATA_DIR / "eda_dwell_summary.csv")


@st.cache_data
def load_hop_scaling_summary() -> pd.DataFrame:
    """Load travel time variability across hop tiers."""
    return pd.read_csv(DATA_DIR / "eda_hop_length_summary.csv")


@st.cache_data
def load_day_summary() -> pd.DataFrame:
    """Load day-of-week travel time and variability patterns."""
    return pd.read_csv(DATA_DIR / "eda_day_summary.csv")


@st.cache_data
def load_model_comparison() -> pd.DataFrame:
    """Load Task 3 validation comparison across historical baseline and ML models."""
    return pd.read_csv(ML_DIR / "model_comparison.csv")


@st.cache_data
def load_feature_importance() -> pd.DataFrame:
    """Load permutation feature importance rankings from ML evaluation."""
    return pd.read_csv(ML_DIR / "feature_importance.csv")


@st.cache_data
def load_test_metrics() -> Dict[str, Any]:
    """Load final out-of-time test partition evaluation metrics."""
    with open(ML_DIR / "test_metrics.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_model_metadata() -> Dict[str, Any]:
    """Load model training metadata, features, and split counts."""
    with open(ML_DIR / "model_metadata.json", "r", encoding="utf-8") as f:
        return json.load(f)
