"""
BusInsight Model Service

Loads the serialized HistGradientBoostingRegressor model artifact (ML/best_model.joblib)
and performs pre-journey passenger travel-time inference using the approved 10-feature schema.
"""

import os
from typing import Dict, Any, Optional
from datetime import date
import numpy as np
import joblib
import streamlit as st

from .metadata_service import load_stop_index_mapping

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "ML", "best_model.joblib")
METADATA_PATH = os.path.join(PROJECT_ROOT, "ML", "model_metadata.json")


@st.cache_resource
def load_trained_model():
    """
    Loads and caches the serialized HistGradientBoostingRegressor model artifact.
    Size: ~421 KB.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Trained model artifact not found at {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    return model


def predict_journey_duration(
    route_short_name: int,
    direction_id: int,
    start_stop_id: str,
    destination_stop_id: str,
    start_segment: int,
    destination_segment: int,
    journey_date: date
) -> Dict[str, Any]:
    """
    Executes travel-time prediction for a passenger journey using the trained ML model.

    Features (Strictly pre-journey):
      1. route_short_name (10, 12, 46)
      2. direction_id (1, 2)
      3. start_stop_idx (0..200 from stops.txt)
      4. dest_stop_idx (0..200 from stops.txt)
      5. start_segment (2..62)
      6. destination_segment (2..62)
      7. segments_traversed (hop distance)
      8. day_of_week (0..6)
      9. is_weekend (0, 1)
      10. month (7, 8, 9)
    """
    try:
        model = load_trained_model()
        stop_to_idx, _ = load_stop_index_mapping()

        if start_stop_id not in stop_to_idx:
            return {"success": False, "error": f"Unknown origin stop ID: {start_stop_id}"}
        if destination_stop_id not in stop_to_idx:
            return {"success": False, "error": f"Unknown destination stop ID: {destination_stop_id}"}

        if destination_segment < start_segment:
            return {
                "success": False,
                "error": "Invalid journey: Destination segment must be downstream of start segment."
            }

        start_stop_idx = stop_to_idx[start_stop_id]
        dest_stop_idx = stop_to_idx[destination_stop_id]
        segments_traversed = int(destination_segment - start_segment + 1)

        day_of_week = int(journey_date.weekday())
        is_weekend = 1 if day_of_week in [5, 6] else 0
        month = int(journey_date.month)

        feature_vector = np.array([[
            int(route_short_name),
            int(direction_id),
            int(start_stop_idx),
            int(dest_stop_idx),
            int(start_segment),
            int(destination_segment),
            int(segments_traversed),
            int(day_of_week),
            int(is_weekend),
            int(month)
        ]])

        raw_pred_seconds = float(model.predict(feature_vector)[0])
        pred_seconds = max(1.0, round(raw_pred_seconds, 1))
        pred_minutes = round(pred_seconds / 60.0, 1)

        return {
            "success": True,
            "predicted_seconds": pred_seconds,
            "predicted_minutes": pred_minutes,
            "segments_traversed": segments_traversed,
            "features": {
                "route_short_name": route_short_name,
                "direction_id": direction_id,
                "start_stop_idx": start_stop_idx,
                "dest_stop_idx": dest_stop_idx,
                "start_segment": start_segment,
                "destination_segment": destination_segment,
                "segments_traversed": segments_traversed,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "month": month
            },
            "error": None
        }

    except Exception as e:
        return {"success": False, "error": f"Model inference error: {str(e)}"}
