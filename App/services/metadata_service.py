"""
BusInsight Metadata Service

Loads and exposes network topology, route definitions, directional stop sequences,
and stop-to-index mappings for model feature encoding.
"""

import os
from typing import Dict, List, Any, Tuple
import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
ORIGINAL_DATA_DIR = os.path.join(PROJECT_ROOT, "Original Data")

ROUTE_METADATA = {
    10: {
        "short_name": 10,
        "name": "Route 10",
        "corridor": "Astana Railway Station – International Airport",
        "description": "Express trunk corridor connecting Central Railway Station to Nursultan Nazarbayev International Airport via Mangilik El Avenue."
    },
    12: {
        "short_name": 12,
        "name": "Route 12",
        "corridor": "Astana Railway Station – International Airport",
        "description": "Primary city corridor connecting Central Railway Station to International Airport via Kabanbay Batyr Avenue."
    },
    46: {
        "short_name": 46,
        "name": "Route 46",
        "corridor": "Karasu Street – Comfort Town",
        "description": "Cross-city residential trunk corridor connecting northern Karasu district to southwestern Comfort Town."
    }
}

DIRECTION_METADATA = {
    1: {"id": 1, "label": "Direction 1 (Outbound)", "short_label": "Direction 1"},
    2: {"id": 2, "label": "Direction 2 (Inbound)", "short_label": "Direction 2"}
}


@st.cache_data
def load_stop_index_mapping() -> Tuple[Dict[str, int], Dict[int, str]]:
    """
    Loads stops.txt and constructs deterministic stop_id to integer index mapping.
    Matches the exact encoding used during Task 3 model training.
    """
    stops_file = os.path.join(ORIGINAL_DATA_DIR, "stops.txt")
    stops_df = pd.read_csv(stops_file, sep="\t")
    sorted_stop_ids = sorted(stops_df["stop_id"].unique())
    stop_to_idx = {sid: idx for idx, sid in enumerate(sorted_stop_ids)}
    idx_to_stop = {idx: sid for sid, idx in stop_to_idx.items()}
    return stop_to_idx, idx_to_stop


@st.cache_data
def load_route_segment_sequences() -> pd.DataFrame:
    """
    Loads route_segment_summary.csv containing the ordered physical segments
    for each route and direction.
    """
    summary_file = os.path.join(DATA_DIR, "route_segment_summary.csv")
    df = pd.read_csv(summary_file)
    return df


def get_available_routes() -> List[int]:
    """Returns the list of monitored route numbers."""
    return sorted(list(ROUTE_METADATA.keys()))


def get_route_info(route_short_name: int) -> Dict[str, Any]:
    """Returns human-readable route information."""
    return ROUTE_METADATA.get(route_short_name, {
        "short_name": route_short_name,
        "name": f"Route {route_short_name}",
        "corridor": "Astana Corridor",
        "description": "Monitored transit corridor."
    })


def get_available_directions(route_short_name: int) -> List[int]:
    """Returns valid directions for the given route."""
    df = load_route_segment_sequences()
    dirs = df[df["route_short_name"] == route_short_name]["direction_id"].unique().tolist()
    return sorted(dirs)


def get_boarding_stops(route_short_name: int, direction_id: int) -> List[Dict[str, Any]]:
    """
    Returns ordered candidate boarding stops for the selected route and direction.
    Excludes Segment 1 (terminal dispatch) per approved project methodology.
    """
    df = load_route_segment_sequences()
    subset = df[
        (df["route_short_name"] == route_short_name) &
        (df["direction_id"] == direction_id) &
        (df["segment"] >= 2)
    ].sort_values("segment")

    stops = []
    for _, row in subset.iterrows():
        stops.append({
            "segment": int(row["segment"]),
            "stop_id": str(row["start_guid"]),
            "stop_name": str(row["start_stop_name"])
        })
    return stops


def get_destination_stops(route_short_name: int, direction_id: int, start_segment: int) -> List[Dict[str, Any]]:
    """
    Returns ordered candidate destination stops downstream from start_segment.
    destination_segment >= start_segment.
    """
    df = load_route_segment_sequences()
    subset = df[
        (df["route_short_name"] == route_short_name) &
        (df["direction_id"] == direction_id) &
        (df["segment"] >= start_segment)
    ].sort_values("segment")

    destinations = []
    for _, row in subset.iterrows():
        dest_seg = int(row["segment"])
        destinations.append({
            "segment": dest_seg,
            "stop_id": str(row["end_guid"]),
            "stop_name": str(row["end_stop_name"]),
            "segments_traversed": dest_seg - start_segment + 1
        })
    return destinations
