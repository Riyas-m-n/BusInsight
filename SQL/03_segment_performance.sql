-- ==============================================================================
-- BusInsight - SQL Analysis
-- Query 03: Segment Performance & High-Variability Segment Identification
-- Description: Analyzes segment travel-time distributions and identifies corridor
-- segments with high observed dispersion (high travel-time variability).
--
-- High-Variability Segment Definition:
--   1. Population: All standard passenger segments (segment > 1).
--   2. Minimum Observation Filter: N >= 500 observations to prevent small-sample bias.
--   3. Dispersion Metric: Interquartile Range of total segment time (IQR = P75 - P25).
--   4. Identification Threshold: Upper quartile (>= 75th percentile) of IQR
--      within the eligible corridor segment population.
-- ==============================================================================

WITH segment_base_stats AS (
    SELECT
        route_short_name,
        direction_id,
        segment,
        MIN(start_stop_name) AS start_stop_sample,
        MIN(end_stop_name) AS end_stop_sample,
        COUNT(*) AS n_obs,
        -- Run time metrics (seconds)
        ROUND(AVG(run_time_in_seconds), 2) AS mean_run_time_sec,
        ROUND(MEDIAN(run_time_in_seconds), 2) AS median_run_time_sec,
        ROUND(QUANTILE_CONT(run_time_in_seconds, 0.10), 2) AS p10_run_time_sec,
        ROUND(QUANTILE_CONT(run_time_in_seconds, 0.90), 2) AS p90_run_time_sec,
        ROUND(QUANTILE_CONT(run_time_in_seconds, 0.75) - 
              QUANTILE_CONT(run_time_in_seconds, 0.25), 2) AS iqr_run_time_sec,
        ROUND(STDDEV(run_time_in_seconds), 2) AS std_run_time_sec,
        -- Dwell time metrics (seconds)
        ROUND(AVG(dwell_time_in_seconds), 2) AS mean_dwell_time_sec,
        ROUND(MEDIAN(dwell_time_in_seconds), 2) AS median_dwell_time_sec,
        ROUND(QUANTILE_CONT(dwell_time_in_seconds, 0.90), 2) AS p90_dwell_time_sec,
        ROUND(STDDEV(dwell_time_in_seconds), 2) AS std_dwell_time_sec,
        -- Total segment duration (seconds)
        ROUND(AVG(total_segment_time_seconds), 2) AS mean_total_time_sec,
        ROUND(MEDIAN(total_segment_time_seconds), 2) AS median_total_time_sec,
        ROUND(QUANTILE_CONT(total_segment_time_seconds, 0.10), 2) AS p10_total_time_sec,
        ROUND(QUANTILE_CONT(total_segment_time_seconds, 0.90), 2) AS p90_total_time_sec,
        ROUND(QUANTILE_CONT(total_segment_time_seconds, 0.75) - 
              QUANTILE_CONT(total_segment_time_seconds, 0.25), 2) AS iqr_total_time_sec,
        ROUND(STDDEV(total_segment_time_seconds), 2) AS std_total_time_sec,
        ROUND(STDDEV(total_segment_time_seconds) / NULLIF(AVG(total_segment_time_seconds), 0), 4) AS cv_total_time
    FROM analytical_segment_data
    WHERE segment > 1 -- Standard passenger segments only
    GROUP BY route_short_name, direction_id, segment
),
eligible_population_thresholds AS (
    SELECT
        QUANTILE_CONT(iqr_total_time_sec, 0.75) AS p75_iqr_threshold
    FROM segment_base_stats
    WHERE n_obs >= 500
)
SELECT
    s.route_short_name,
    s.direction_id,
    s.segment,
    s.start_stop_sample,
    s.end_stop_sample,
    s.n_obs,
    -- Run time
    s.mean_run_time_sec,
    s.median_run_time_sec,
    s.p10_run_time_sec,
    s.p90_run_time_sec,
    s.iqr_run_time_sec,
    s.std_run_time_sec,
    -- Dwell time
    s.mean_dwell_time_sec,
    s.median_dwell_time_sec,
    s.p90_dwell_time_sec,
    s.std_dwell_time_sec,
    -- Total segment duration
    s.mean_total_time_sec,
    s.median_total_time_sec,
    s.p10_total_time_sec,
    s.p90_total_time_sec,
    s.iqr_total_time_sec,
    s.std_total_time_sec,
    s.cv_total_time,
    -- High variability classification
    CASE 
        WHEN s.n_obs >= 500 AND s.iqr_total_time_sec >= t.p75_iqr_threshold THEN 1 
        ELSE 0 
    END AS is_high_variability_segment
FROM segment_base_stats s
CROSS JOIN eligible_population_thresholds t
ORDER BY s.iqr_total_time_sec DESC, s.n_obs DESC;
