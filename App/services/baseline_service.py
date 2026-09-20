"""
BusInsight - Baseline Lookup Service
Retrieves historical segment-pair median journey times and fallback statistics
from approved ML baseline artifacts.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASELINE_LOOKUP_FILE = PROJECT_ROOT / "ML" / "baseline_lookup.csv"
BASELINE_FALLBACK_FILE = PROJECT_ROOT / "ML" / "baseline_segments_fallback.csv"


@st.cache_data
def load_baseline_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the precomputed baseline tables into memory."""
    df_lookup = pd.read_csv(BASELINE_LOOKUP_FILE)
    df_fallback = pd.read_csv(BASELINE_FALLBACK_FILE)
    return df_lookup, df_fallback


def get_baseline_estimate(
    route_short_name: int,
    direction_id: int,
    start_segment: int,
    destination_segment: int,
) -> Dict[str, Any]:
    """
    Look up the historical median journey time for a given OD segment pair.
    Falls back to segments_traversed median if the exact segment pair is missing.
    """
    df_lookup, df_fallback = load_baseline_tables()
    segments_traversed = destination_segment - start_segment + 1

    # Attempt exact OD pair match
    match = df_lookup[
        (df_lookup["route_short_name"] == route_short_name)
        & (df_lookup["direction_id"] == direction_id)
        & (df_lookup["start_segment"] == start_segment)
        & (df_lookup["destination_segment"] == destination_segment)
    ]

    if not match.empty:
        row = match.iloc[0]
        med_sec = float(row["baseline_median_seconds"])
        sample_count = int(row["sample_count"])
        return {
            "baseline_median_seconds": med_sec,
            "baseline_median_minutes": round(med_sec / 60.0, 1),
            "sample_count": sample_count,
            "lookup_type": "Exact OD Segment Pair",
            "segments_traversed": segments_traversed,
        }

    # Fallback to segments_traversed match
    fb_match = df_fallback[
        (df_fallback["route_short_name"] == route_short_name)
        & (df_fallback["direction_id"] == direction_id)
        & (df_fallback["segments_traversed"] == segments_traversed)
    ]

    if not fb_match.empty:
        row = fb_match.iloc[0]
        med_sec = float(row["fallback_median_seconds"])
        sample_count = int(row["sample_count"])
        return {
            "baseline_median_seconds": med_sec,
            "baseline_median_minutes": round(med_sec / 60.0, 1),
            "sample_count": sample_count,
            "lookup_type": "Route-Direction Hop Fallback",
            "segments_traversed": segments_traversed,
        }

    return {
        "baseline_median_seconds": None,
        "baseline_median_minutes": None,
        "sample_count": 0,
        "lookup_type": "Unavailable",
        "segments_traversed": segments_traversed,
    }
