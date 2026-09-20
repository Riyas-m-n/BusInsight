-- ==============================================================================
-- BusInsight - SQL Analysis
-- Query 02: Route and Direction Performance
-- Description: Analyzes observed travel-time performance across route and direction.
-- Computes measurable distribution statistics (Median, IQR, P10, P90, StdDev, CV)
-- for both segment operations and passenger journeys without synthetic scores.
-- ==============================================================================

WITH direction_segment_metrics AS (
    SELECT
        route_short_name,
        direction_id,
        COUNT(*) AS total_segment_records,
        COUNT(DISTINCT trip_id) AS distinct_trips,
        -- Travel times for non-terminal passenger segments (segment > 1)
        ROUND(AVG(CASE WHEN segment > 1 THEN total_segment_time_seconds END), 2) AS avg_segment_duration_sec,
        ROUND(MEDIAN(CASE WHEN segment > 1 THEN total_segment_time_seconds END), 2) AS median_segment_duration_sec,
        ROUND(QUANTILE_CONT(CASE WHEN segment > 1 THEN total_segment_time_seconds END, 0.10), 2) AS p10_segment_duration_sec,
        ROUND(QUANTILE_CONT(CASE WHEN segment > 1 THEN total_segment_time_seconds END, 0.90), 2) AS p90_segment_duration_sec,
        ROUND(QUANTILE_CONT(CASE WHEN segment > 1 THEN total_segment_time_seconds END, 0.75) - 
              QUANTILE_CONT(CASE WHEN segment > 1 THEN total_segment_time_seconds END, 0.25), 2) AS iqr_segment_duration_sec,
        ROUND(STDDEV(CASE WHEN segment > 1 THEN total_segment_time_seconds END), 2) AS std_segment_duration_sec
    FROM analytical_segment_data
    GROUP BY route_short_name, direction_id
),
direction_journey_metrics AS (
    SELECT
        route_short_name,
        direction_id,
        COUNT(*) AS total_journey_observations,
        ROUND(MIN(observed_journey_time_seconds), 2) AS min_journey_sec,
        ROUND(MAX(observed_journey_time_seconds), 2) AS max_journey_sec,
        ROUND(AVG(observed_journey_time_seconds), 2) AS avg_journey_sec,
        ROUND(MEDIAN(observed_journey_time_seconds), 2) AS median_journey_sec,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.10), 2) AS p10_journey_sec,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.90), 2) AS p90_journey_sec,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.75) - 
              QUANTILE_CONT(observed_journey_time_seconds, 0.25), 2) AS iqr_journey_sec,
        ROUND(STDDEV(observed_journey_time_seconds), 2) AS std_journey_sec,
        -- Coefficient of variation (StdDev / Mean)
        ROUND(STDDEV(observed_journey_time_seconds) / NULLIF(AVG(observed_journey_time_seconds), 0), 4) AS cv_journey,
        -- Conversions to minutes for operational reporting
        ROUND(MEDIAN(observed_journey_time_seconds) / 60.0, 2) AS median_journey_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.10) / 60.0, 2) AS p10_journey_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.90) / 60.0, 2) AS p90_journey_min,
        ROUND((QUANTILE_CONT(observed_journey_time_seconds, 0.90) - 
               QUANTILE_CONT(observed_journey_time_seconds, 0.10)) / 60.0, 2) AS p10_p90_range_min
    FROM journey_ml_ready
    GROUP BY route_short_name, direction_id
)
SELECT
    j.route_short_name,
    j.direction_id,
    -- Segment operation counts
    s.distinct_trips,
    s.total_segment_records,
    s.median_segment_duration_sec,
    s.iqr_segment_duration_sec,
    -- Journey metrics (seconds)
    j.total_journey_observations,
    j.min_journey_sec,
    j.max_journey_sec,
    j.avg_journey_sec,
    j.median_journey_sec,
    j.p10_journey_sec,
    j.p90_journey_sec,
    j.iqr_journey_sec,
    j.std_journey_sec,
    j.cv_journey,
    -- Journey metrics (minutes for reporting)
    j.median_journey_min,
    j.p10_journey_min,
    j.p90_journey_min,
    j.p10_p90_range_min
FROM direction_journey_metrics j
JOIN direction_segment_metrics s 
  ON j.route_short_name = s.route_short_name 
 AND j.direction_id = s.direction_id
ORDER BY j.route_short_name, j.direction_id;
