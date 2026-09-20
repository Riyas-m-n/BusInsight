#!/usr/bin/env python3
"""
BusInsight - Exploratory Data Analysis & Visualizations (Task 4)

Executes SQL-backed analytical aggregations across analytical segment and journey data,
exports 6 clean summary CSVs to Data/, and generates 8 portfolio-quality figures
to Reports/figures/.

Memory Protection:
  - Uses DuckDB view engine (SQL/businsight.duckdb) without loading full 1.6+ GB CSVs into pandas.
  - Aggregations occur in-engine; only compact summary tables are returned to Python.
"""

import os
import sys
import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
SQL_DIR = os.path.join(PROJECT_ROOT, "SQL")
DB_PATH = os.path.join(SQL_DIR, "businsight.duckdb")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "Reports", "figures")

# Visual style setup
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.labelweight": "bold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 16,
    "figure.titleweight": "bold"
})

BRAND_NAVY = "#1B365D"
BRAND_BLUE = "#4A90E2"
BRAND_TEAL = "#2E8B57"
BRAND_ORANGE = "#E67E22"
BRAND_RED = "#C0392B"
BRAND_GREY = "#7F8C8D"


def ensure_database(conn):
    """Ensures DuckDB views exist."""
    tables = [r[0] for r in conn.sql("SHOW TABLES").fetchall()]
    if "analytical_segment_data" not in tables or "journey_ml_ready" not in tables:
        print("[EDA] Rebuilding SQL views catalog...")
        from build_sql_database import build_database
        build_database()


def export_summary_csvs(conn):
    """Executes SQL queries and exports 6 summary datasets to Data/."""
    print("\n--- Generating Summary Datasets ---")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Route Summary
    print("[1/6] Generating Data/eda_route_summary.csv ...")
    with open(os.path.join(SQL_DIR, "01_route_overview.sql"), "r", encoding="utf-8") as f:
        q_route = f.read()
    df_route = conn.sql(q_route).df()
    df_route.to_csv(os.path.join(DATA_DIR, "eda_route_summary.csv"), index=False)
    print(f"      Saved {len(df_route)} rows.")
    
    # 2. Route-Direction Summary
    print("[2/6] Generating Data/eda_route_direction_summary.csv ...")
    with open(os.path.join(SQL_DIR, "02_route_direction_performance.sql"), "r", encoding="utf-8") as f:
        q_dir = f.read()
    df_dir = conn.sql(q_dir).df()
    df_dir.to_csv(os.path.join(DATA_DIR, "eda_route_direction_summary.csv"), index=False)
    print(f"      Saved {len(df_dir)} rows.")
    
    # 3. Segment Performance & High-Variability
    print("[3/6] Generating Data/eda_segment_summary.csv ...")
    with open(os.path.join(SQL_DIR, "03_segment_performance.sql"), "r", encoding="utf-8") as f:
        q_seg = f.read()
    df_seg = conn.sql(q_seg).df()
    df_seg.to_csv(os.path.join(DATA_DIR, "eda_segment_summary.csv"), index=False)
    print(f"      Saved {len(df_seg)} rows (High variability count: {df_seg['is_high_variability_segment'].sum()}).")
    
    # 4. Dwell Time Summary
    print("[4/6] Generating Data/eda_dwell_summary.csv ...")
    with open(os.path.join(SQL_DIR, "04_travel_time_variability.sql"), "r", encoding="utf-8") as f:
        q_dwell = f.read()
    df_dwell = conn.sql(q_dwell).df()
    df_dwell.to_csv(os.path.join(DATA_DIR, "eda_dwell_summary.csv"), index=False)
    print(f"      Saved {len(df_dwell)} rows.")
    
    # 5. Hop Length Summary
    print("[5/6] Generating Data/eda_hop_length_summary.csv ...")
    q_hop = """
    WITH journey_hop_tiers AS (
        SELECT
            CASE 
                WHEN segments_traversed BETWEEN 1 AND 5 THEN '1. Short (1-5 hops)'
                WHEN segments_traversed BETWEEN 6 AND 15 THEN '2. Medium (6-15 hops)'
                WHEN segments_traversed BETWEEN 16 AND 30 THEN '3. Long (16-30 hops)'
                ELSE '4. Very Long (>30 hops)'
            END AS hop_tier,
            CASE 
                WHEN segments_traversed BETWEEN 1 AND 5 THEN 1
                WHEN segments_traversed BETWEEN 6 AND 15 THEN 2
                WHEN segments_traversed BETWEEN 16 AND 30 THEN 3
                ELSE 4
            END AS tier_rank,
            observed_journey_time_seconds
        FROM journey_ml_ready
    )
    SELECT
        hop_tier,
        COUNT(*) AS total_journeys,
        ROUND(MIN(observed_journey_time_seconds) / 60.0, 2) AS min_duration_min,
        ROUND(AVG(observed_journey_time_seconds) / 60.0, 2) AS avg_duration_min,
        ROUND(MEDIAN(observed_journey_time_seconds) / 60.0, 2) AS median_duration_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.10) / 60.0, 2) AS p10_duration_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.90) / 60.0, 2) AS p90_duration_min,
        ROUND((QUANTILE_CONT(observed_journey_time_seconds, 0.75) - 
               QUANTILE_CONT(observed_journey_time_seconds, 0.25)) / 60.0, 2) AS iqr_duration_min,
        ROUND(STDDEV(observed_journey_time_seconds) / 60.0, 2) AS std_duration_min,
        ROUND(STDDEV(observed_journey_time_seconds) / NULLIF(AVG(observed_journey_time_seconds), 0), 4) AS cv_duration
    FROM journey_hop_tiers
    GROUP BY hop_tier, tier_rank
    ORDER BY tier_rank;
    """
    df_hop = conn.sql(q_hop).df()
    df_hop.to_csv(os.path.join(DATA_DIR, "eda_hop_length_summary.csv"), index=False)
    print(f"      Saved {len(df_hop)} rows.")
    
    # 6. Day of Week Summary
    print("[6/6] Generating Data/eda_day_summary.csv ...")
    q_day = """
    SELECT
        day_of_week,
        CASE day_of_week
            WHEN 0 THEN 'Monday'
            WHEN 1 THEN 'Tuesday'
            WHEN 2 THEN 'Wednesday'
            WHEN 3 THEN 'Thursday'
            WHEN 4 THEN 'Friday'
            WHEN 5 THEN 'Saturday'
            WHEN 6 THEN 'Sunday'
        END AS day_name,
        is_weekend,
        COUNT(*) AS total_journeys,
        COUNT(DISTINCT trip_id) AS distinct_trips,
        ROUND(AVG(observed_journey_time_seconds) / 60.0, 2) AS avg_duration_min,
        ROUND(MEDIAN(observed_journey_time_seconds) / 60.0, 2) AS median_duration_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.10) / 60.0, 2) AS p10_duration_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.90) / 60.0, 2) AS p90_duration_min,
        ROUND((QUANTILE_CONT(observed_journey_time_seconds, 0.75) - 
               QUANTILE_CONT(observed_journey_time_seconds, 0.25)) / 60.0, 2) AS iqr_duration_min,
        ROUND(STDDEV(observed_journey_time_seconds) / 60.0, 2) AS std_duration_min
    FROM journey_ml_ready
    GROUP BY day_of_week, is_weekend
    ORDER BY day_of_week;
    """
    df_day = conn.sql(q_day).df()
    df_day.to_csv(os.path.join(DATA_DIR, "eda_day_summary.csv"), index=False)
    print(f"      Saved {len(df_day)} rows.")
    
    return df_route, df_dir, df_seg, df_dwell, df_hop, df_day


def generate_visualizations(conn, df_route, df_dir, df_seg, df_dwell, df_hop, df_day):
    """Generates 8 publication-grade charts to Reports/figures/."""
    print("\n--- Generating Portfolio Visualizations ---")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # Figure 1: Median Journey Travel Time by Route
    print("[Fig 1/8] Median Journey Travel Time by Route ...")
    fig, ax = plt.subplots(figsize=(8, 5))
    routes = [f"Route {r}" for r in df_route["route_short_name"]]
    medians = df_route["median_journey_time_min"]
    bars = ax.bar(routes, medians, color=[BRAND_BLUE, BRAND_TEAL, BRAND_ORANGE], width=0.5, edgecolor="black", linewidth=0.8)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.6, f"{yval:.1f} min", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_ylabel("Median Observed Duration (Minutes)")
    ax.set_title("Median Passenger Journey Duration by Route", pad=15)
    ax.set_ylim(0, max(medians) * 1.25)
    ax.text(0.99, -0.12, "Source: BusInsight journey_ml_ready (14.48M journeys). Note: Observed duration from boarding to alighting.",
            transform=ax.transAxes, ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig01_median_journey_time_by_route.png"), dpi=300)
    plt.close(fig)
    
    # Figure 2: P10–P90 Journey Travel-Time Range by Route
    print("[Fig 2/8] P10–P90 Journey Travel-Time Range by Route ...")
    fig, ax = plt.subplots(figsize=(9, 5))
    y_pos = np.arange(len(df_route))
    for i, row in df_route.iterrows():
        p10 = row["p10_journey_time_min"]
        p90 = row["p90_journey_time_min"]
        med = row["median_journey_time_min"]
        ax.plot([p10, p90], [i, i], color=BRAND_NAVY, linewidth=3, solid_capstyle="round")
        ax.plot(med, i, marker="o", markersize=10, color=BRAND_ORANGE, zorder=5)
        ax.plot(p10, i, marker="|", markersize=12, markeredgewidth=2.5, color=BRAND_NAVY)
        ax.plot(p90, i, marker="|", markersize=12, markeredgewidth=2.5, color=BRAND_NAVY)
        ax.text(p10 - 1.2, i, f"P10: {p10:.1f}m", ha="right", va="center", fontsize=9, fontweight="bold")
        ax.text(p90 + 1.2, i, f"P90: {p90:.1f}m", ha="left", va="center", fontsize=9, fontweight="bold")
        ax.text(med, i + 0.22, f"Median: {med:.1f}m", ha="center", va="bottom", fontsize=9, color=BRAND_ORANGE, fontweight="bold")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"Route {r}" for r in df_route["route_short_name"]])
    ax.set_xlabel("Observed Journey Duration (Minutes)")
    ax.set_title("P10 to P90 Journey Duration Dispersion by Route", pad=15)
    ax.set_xlim(0, 75)
    ax.text(0.99, -0.15, "Source: BusInsight journey_ml_ready. Whiskers mark P10 to P90 range; orange circle denotes median.",
            transform=ax.transAxes, ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig02_p10_p90_journey_time_range_by_route.png"), dpi=300)
    plt.close(fig)
    
    # Figure 3: Journey Travel Time by Hop-Length Tier
    print("[Fig 3/8] Journey Travel Time by Hop-Length Tier ...")
    fig, ax = plt.subplots(figsize=(10, 5))
    tiers = [t.split(". ")[1] for t in df_hop["hop_tier"]]
    x = np.arange(len(tiers))
    width = 0.35
    b1 = ax.bar(x - width/2, df_hop["median_duration_min"], width, label="Median Duration", color=BRAND_BLUE, edgecolor="black", linewidth=0.7)
    b2 = ax.bar(x + width/2, df_hop["iqr_duration_min"], width, label="Dispersion (IQR)", color=BRAND_ORANGE, edgecolor="black", linewidth=0.7)
    for b in b1:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.8, f"{b.get_height():.1f}m", ha="center", fontsize=9, fontweight="bold")
    for b in b2:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.8, f"{b.get_height():.1f}m", ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(tiers)
    ax.set_ylabel("Minutes")
    ax.set_title("Observed Journey Duration & Travel-Time Dispersion by Hop Tier", pad=15)
    ax.legend(frameon=True)
    ax.set_ylim(0, max(df_hop["median_duration_min"]) * 1.25)
    ax.text(0.99, -0.14, "Source: BusInsight journey_ml_ready. Compares median duration and IQR (dispersion) across distance tiers.",
            transform=ax.transAxes, ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig03_journey_time_by_hop_tier.png"), dpi=300)
    plt.close(fig)
    
    # Figure 4: Route/Direction Travel-Time Comparison
    print("[Fig 4/8] Route/Direction Travel-Time Comparison ...")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    df_dir_plot = df_dir.copy()
    df_dir_plot["label"] = df_dir_plot.apply(lambda r: f"R{r['route_short_name']} Dir {r['direction_id']}", axis=1)
    x = np.arange(len(df_dir_plot))
    colors = [BRAND_NAVY if r["direction_id"] == 1 else BRAND_TEAL for _, r in df_dir_plot.iterrows()]
    bars = ax.bar(x, df_dir_plot["median_journey_min"], color=colors, width=0.55, edgecolor="black", linewidth=0.8)
    for bar, (_, row) in zip(bars, df_dir_plot.iterrows()):
        h = bar.get_height()
        iqr = row["iqr_journey_sec"] / 60.0
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.6, f"{h:.1f}m\n(IQR:{iqr:.1f}m)", ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(df_dir_plot["label"])
    ax.set_ylabel("Median Journey Duration (Minutes)")
    ax.set_title("Median Journey Duration by Route & Direction", pad=15)
    ax.set_ylim(0, max(df_dir_plot["median_journey_min"]) * 1.3)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=BRAND_NAVY, label="Direction 1"),
        Patch(facecolor=BRAND_TEAL, label="Direction 2")
    ]
    ax.legend(handles=legend_elements, loc="upper left", frameon=True)
    ax.text(0.99, -0.12, "Source: BusInsight journey_ml_ready. Shows directional symmetry/asymmetry across corridors.",
            transform=ax.transAxes, ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig04_route_direction_comparison.png"), dpi=300)
    plt.close(fig)
    
    # Figure 5: Top High-Variability Segments
    print("[Fig 5/8] Top High-Variability Segments ...")
    df_top_var = df_seg[df_seg["is_high_variability_segment"] == 1].head(10).copy()
    fig, ax = plt.subplots(figsize=(11, 6))
    labels = [
        f"R{r['route_short_name']}-D{r['direction_id']}-Seg{r['segment']}: {str(r['start_stop_sample'])[:18]}..."
        for _, r in df_top_var.iterrows()
    ]
    y_pos = np.arange(len(df_top_var))
    bars = ax.barh(y_pos, df_top_var["iqr_total_time_sec"], color=BRAND_RED, edgecolor="black", linewidth=0.7)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 3, bar.get_y() + bar.get_height()/2, f"{w:.1f}s", va="center", ha="left", fontsize=9, fontweight="bold")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Interquartile Range (IQR) of Total Segment Time (Seconds)")
    ax.set_title("Top 10 High-Variability Corridor Segments (N >= 500, Top Quartile IQR)", pad=15)
    ax.text(0.99, -0.12, "Source: BusInsight analytical_segment_data. Segments defined as high variability via measured statistical dispersion.",
            transform=ax.transAxes, ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig05_top_high_variability_segments.png"), dpi=300)
    plt.close(fig)
    
    # Figure 6: Top High-Dwell Segments
    print("[Fig 6/8] Top High-Dwell Segments ...")
    df_top_dwell = df_seg.sort_values(by="median_dwell_time_sec", ascending=False).head(10).copy()
    fig, ax = plt.subplots(figsize=(11, 6))
    labels = [
        f"R{r['route_short_name']}-D{r['direction_id']}-Seg{r['segment']}: {str(r['start_stop_sample'])[:18]}..."
        for _, r in df_top_dwell.iterrows()
    ]
    y_pos = np.arange(len(df_top_dwell))
    b1 = ax.barh(y_pos - 0.18, df_top_dwell["median_dwell_time_sec"], height=0.35, label="Median Dwell", color=BRAND_BLUE, edgecolor="black", linewidth=0.7)
    b2 = ax.barh(y_pos + 0.18, df_top_dwell["p90_dwell_time_sec"], height=0.35, label="P90 Dwell", color=BRAND_ORANGE, edgecolor="black", linewidth=0.7)
    for bar in b1:
        w = bar.get_width()
        ax.text(w + 1, bar.get_y() + bar.get_height()/2, f"{w:.0f}s", va="center", ha="left", fontsize=8)
    for bar in b2:
        w = bar.get_width()
        ax.text(w + 1, bar.get_y() + bar.get_height()/2, f"{w:.0f}s", va="center", ha="left", fontsize=8, fontweight="bold")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Dwell Time (Seconds)")
    ax.set_title("Top 10 Passenger Segments by Observed Stop Dwell Time", pad=15)
    ax.legend(loc="lower right", frameon=True)
    ax.text(0.99, -0.12, "Source: BusInsight analytical_segment_data (segment > 1). Terminal dispatch segment 1 excluded.",
            transform=ax.transAxes, ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig06_top_high_dwell_segments.png"), dpi=300)
    plt.close(fig)
    
    # Figure 7: Day-of-Week Journey Duration Comparison
    print("[Fig 7/8] Day-of-Week Journey Duration Comparison ...")
    fig, ax = plt.subplots(figsize=(9, 5))
    days = df_day["day_name"]
    colors = [BRAND_BLUE if w == 0 else BRAND_ORANGE for w in df_day["is_weekend"]]
    bars = ax.bar(days, df_day["median_duration_min"], color=colors, width=0.55, edgecolor="black", linewidth=0.8)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.4, f"{h:.1f}m", ha="center", fontsize=9, fontweight="bold")
    ax.set_ylabel("Median Journey Duration (Minutes)")
    ax.set_title("Observed Median Passenger Journey Duration by Day of Week", pad=15)
    ax.set_ylim(0, max(df_day["median_duration_min"]) * 1.25)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=BRAND_BLUE, label="Weekday (Mon-Fri)"),
        Patch(facecolor=BRAND_ORANGE, label="Weekend (Sat-Sun)")
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True)
    ax.text(0.99, -0.12, "Source: BusInsight journey_ml_ready. Illustrates weekly operational travel-time cycle.",
            transform=ax.transAxes, ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig07_day_of_week_journey_duration.png"), dpi=300)
    plt.close(fig)
    
    # Figure 8: Segment Travel-Time Distribution for Selected High-Variability Segments
    print("[Fig 8/8] Segment Travel-Time Distributions ...")
    top_3_segs = df_top_var.head(3)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=False)
    for idx, (_, r) in enumerate(top_3_segs.iterrows()):
        ax = axes[idx]
        route = r["route_short_name"]
        direction = r["direction_id"]
        seg = r["segment"]
        q_sample = f"""
        SELECT total_segment_time_seconds 
        FROM analytical_segment_data
        WHERE route_short_name = {route} AND direction_id = {direction} AND segment = {seg}
          AND total_segment_time_seconds <= 1200
        """
        vals = conn.sql(q_sample).df()["total_segment_time_seconds"]
        ax.hist(vals, bins=35, color=BRAND_BLUE, edgecolor="black", alpha=0.7, density=True)
        ax.axvline(r["median_total_time_sec"], color=BRAND_RED, linestyle="--", linewidth=2, label=f"Median: {r['median_total_time_sec']:.0f}s")
        ax.axvline(r["p90_total_time_sec"], color=BRAND_ORANGE, linestyle=":", linewidth=2, label=f"P90: {r['p90_total_time_sec']:.0f}s")
        ax.set_title(f"Route {route} Dir {direction} Seg {seg}\n(IQR: {r['iqr_total_time_sec']:.0f}s, N={r['n_obs']:,})", fontsize=11)
        ax.set_xlabel("Total Segment Duration (Seconds)")
        ax.set_ylabel("Density" if idx == 0 else "")
        ax.legend(fontsize=8, loc="upper right")
    fig.suptitle("Observed Total Travel-Time Distributions for Top High-Variability Segments", fontsize=13, fontweight="bold", y=1.02)
    fig.text(0.99, -0.04, "Source: BusInsight analytical_segment_data. Capped at 1200s for display clarity.",
             ha="right", fontsize=8, style="italic", color=BRAND_GREY)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig08_segment_travel_time_distributions.png"), dpi=300)
    plt.close(fig)
    
    print("[EDA] All 8 publication figures generated successfully in Reports/figures/.")


def main():
    print("==================================================================")
    print("BusInsight - Task 4: SQL + Exploratory Data Analysis Runner")
    print("==================================================================")
    
    conn = duckdb.connect(DB_PATH)
    ensure_database(conn)
    
    df_route, df_dir, df_seg, df_dwell, df_hop, df_day = export_summary_csvs(conn)
    generate_visualizations(conn, df_route, df_dir, df_seg, df_dwell, df_hop, df_day)
    
    conn.close()
    print("\n[EDA] Task 4 execution pipeline completed successfully!")


if __name__ == "__main__":
    main()
