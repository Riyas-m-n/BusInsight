#!/usr/bin/env python3
"""
BusInsight - Build SQL Database (Task 4)

Creates or refreshes the lightweight DuckDB database catalog (SQL/businsight.duckdb)
using persistent SQL views mapped directly to existing project CSV files.

This ensures zero data duplication of the 4.8 GB analytical CSVs while providing
fast, SQL-compatible analytical querying across segment-level and journey-level data.
"""

import os
import sys
import duckdb

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQL_DIR = os.path.join(PROJECT_ROOT, "SQL")
DB_PATH = os.path.join(SQL_DIR, "businsight.duckdb")

DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
ANALYTICAL_SEGMENT_CSV = os.path.join(DATA_DIR, "analytical_segment_data.csv").replace("\\", "/")
JOURNEY_TRAINING_CSV = os.path.join(DATA_DIR, "journey_training_data.csv").replace("\\", "/")
JOURNEY_ML_READY_CSV = os.path.join(DATA_DIR, "journey_ml_ready.csv").replace("\\", "/")


def build_database(db_path: str = DB_PATH) -> None:
    """Creates the DuckDB view catalog."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"[DuckDB] Connecting to database catalog at: {db_path}")
    conn = duckdb.connect(db_path)
    
    print("[DuckDB] Registering view: analytical_segment_data ...")
    conn.sql(f"""
        CREATE OR REPLACE VIEW analytical_segment_data AS 
        SELECT * FROM read_csv('{ANALYTICAL_SEGMENT_CSV}', dateformat='%d-%m-%y');
    """)
    
    print("[DuckDB] Registering view: journey_training_data ...")
    conn.sql(f"""
        CREATE OR REPLACE VIEW journey_training_data AS 
        SELECT * FROM read_csv('{JOURNEY_TRAINING_CSV}', dateformat='%d-%m-%y');
    """)
    
    print("[DuckDB] Registering view: journey_ml_ready ...")
    conn.sql(f"""
        CREATE OR REPLACE VIEW journey_ml_ready AS 
        SELECT * FROM read_csv(
            '{JOURNEY_ML_READY_CSV}', 
            columns={{
                'split': 'VARCHAR',
                'trip_id': 'BIGINT',
                'route_short_name': 'BIGINT',
                'direction_id': 'BIGINT',
                'date': 'DATE',
                'day_of_week': 'BIGINT',
                'is_weekend': 'BIGINT',
                'month': 'BIGINT',
                'start_stop_id': 'VARCHAR',
                'destination_stop_id': 'VARCHAR',
                'start_segment': 'BIGINT',
                'destination_segment': 'BIGINT',
                'segments_traversed': 'BIGINT',
                'observed_journey_time_seconds': 'BIGINT'
            }},
            header=true, 
            delim=',', 
            strict_mode=false,
            dateformat='%d-%m-%y'
        );
    """)
    
    # Validation query
    seg_cnt = conn.sql("SELECT COUNT(*) FROM analytical_segment_data").fetchone()[0]
    train_cnt = conn.sql("SELECT COUNT(*) FROM journey_training_data").fetchone()[0]
    ml_cnt = conn.sql("SELECT COUNT(*) FROM journey_ml_ready").fetchone()[0]
    
    print("\n[DuckDB] Verification Results:")
    print(f"  - analytical_segment_data : {seg_cnt:,} rows")
    print(f"  - journey_training_data   : {train_cnt:,} rows")
    print(f"  - journey_ml_ready        : {ml_cnt:,} rows")
    
    conn.close()
    
    file_size_kb = os.path.getsize(db_path) / 1024
    print(f"[DuckDB] Catalog build complete. Size: {file_size_kb:.2f} KB (Zero source data duplicated).")


if __name__ == "__main__":
    build_database()
