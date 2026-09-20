-- ==============================================================================
-- BusInsight - SQL Analysis
-- Query 04: Dwell Time & Travel-Time Variability Analysis
-- Description: Detailed analysis of stop dwell times and their contribution to
-- corridor travel-time variability.
-- Separates ordinary passenger stops (segment > 1) from terminal dispatch (segment 1).
-- ==============================================================================

WITH dwell_analysis_by_route_dir AS (
    SELECT
        route_short_name,
        direction_id,
        CASE WHEN segment = 1 THEN 'Terminal Dispatch (Segment 1)' ELSE 'Standard Passenger Stops (Segment > 1)' END AS segment_class,
        COUNT(*) AS n_observations,
        -- Dwell summary statistics
        ROUND(AVG(dwell_time_in_seconds), 2) AS avg_dwell_sec,
        ROUND(MEDIAN(dwell_time_in_seconds), 2) AS median_dwell_sec,
        ROUND(QUANTILE_CONT(dwell_time_in_seconds, 0.90), 2) AS p90_dwell_sec,
        ROUND(STDDEV(dwell_time_in_seconds), 2) AS std_dwell_sec,
        ROUND(QUANTILE_CONT(dwell_time_in_seconds, 0.75) - 
              QUANTILE_CONT(dwell_time_in_seconds, 0.25), 2) AS iqr_dwell_sec,
        -- Threshold occurrences
        SUM(CASE WHEN dwell_time_in_seconds = 0 THEN 1 ELSE 0 END) AS zero_dwell_count,
        ROUND(100.0 * SUM(CASE WHEN dwell_time_in_seconds = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS zero_dwell_pct,
        SUM(CASE WHEN dwell_time_in_seconds > 30 THEN 1 ELSE 0 END) AS dwell_over_30s_count,
        ROUND(100.0 * SUM(CASE WHEN dwell_time_in_seconds > 30 THEN 1 ELSE 0 END) / COUNT(*), 2) AS dwell_over_30s_pct,
        SUM(CASE WHEN dwell_time_in_seconds > 60 THEN 1 ELSE 0 END) AS dwell_over_60s_count,
        ROUND(100.0 * SUM(CASE WHEN dwell_time_in_seconds > 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS dwell_over_60s_pct,
        -- Dwell contribution to total corridor duration
        ROUND(100.0 * SUM(dwell_time_in_seconds) / NULLIF(SUM(total_segment_time_seconds), 0), 2) AS dwell_share_of_total_time_pct
    FROM analytical_segment_data
    GROUP BY route_short_name, direction_id, 
             CASE WHEN segment = 1 THEN 'Terminal Dispatch (Segment 1)' ELSE 'Standard Passenger Stops (Segment > 1)' END
)
SELECT
    route_short_name,
    direction_id,
    segment_class,
    n_observations,
    avg_dwell_sec,
    median_dwell_sec,
    p90_dwell_sec,
    std_dwell_sec,
    iqr_dwell_sec,
    zero_dwell_count,
    zero_dwell_pct,
    dwell_over_30s_count,
    dwell_over_30s_pct,
    dwell_over_60s_count,
    dwell_over_60s_pct,
    dwell_share_of_total_time_pct
FROM dwell_analysis_by_route_dir
ORDER BY route_short_name, direction_id, segment_class DESC;
