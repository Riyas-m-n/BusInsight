-- ==============================================================================
-- BusInsight - SQL Analysis
-- Query 01: Route Overview
-- Description: Route operational overview and journey-observation totals.
-- Computes distinct operational counts, segment travel-time metrics,
-- and dispersion statistics.
-- Notes:
--   1. Segment metrics are calculated on standard corridor segments (segment > 1)
--      to separate terminal dispatch behavior from line travel.
--   2. Journey counts represent generated stop-to-stop journey observations.
-- ==============================================================================

WITH route_segment_stats AS (
    SELECT
        route_short_name,
        route_long_name,
        COUNT(*) AS total_segment_observations,
        COUNT(DISTINCT trip_id) AS distinct_trips,
        COUNT(DISTINCT date) AS distinct_operating_dates,
        COUNT(DISTINCT deviceid) AS distinct_devices,
        COUNT(DISTINCT start_point) AS distinct_stops,
        COUNT(DISTINCT segment) AS distinct_segments,
        -- Standard passenger segment travel times (excluding terminal dispatch segment 1)
        ROUND(AVG(CASE WHEN segment > 1 THEN run_time_in_seconds END), 2) AS avg_segment_run_time_sec,
        ROUND(MEDIAN(CASE WHEN segment > 1 THEN run_time_in_seconds END), 2) AS median_segment_run_time_sec,
        ROUND(AVG(CASE WHEN segment > 1 THEN dwell_time_in_seconds END), 2) AS avg_segment_dwell_time_sec,
        ROUND(MEDIAN(CASE WHEN segment > 1 THEN dwell_time_in_seconds END), 2) AS median_segment_dwell_time_sec,
        ROUND(AVG(CASE WHEN segment > 1 THEN total_segment_time_seconds END), 2) AS avg_total_segment_time_sec,
        ROUND(MEDIAN(CASE WHEN segment > 1 THEN total_segment_time_seconds END), 2) AS median_total_segment_time_sec,
        ROUND(STDDEV(CASE WHEN segment > 1 THEN total_segment_time_seconds END), 2) AS std_total_segment_time_sec,
        ROUND(QUANTILE_CONT(CASE WHEN segment > 1 THEN total_segment_time_seconds END, 0.75) - 
              QUANTILE_CONT(CASE WHEN segment > 1 THEN total_segment_time_seconds END, 0.25), 2) AS iqr_total_segment_time_sec
    FROM analytical_segment_data
    GROUP BY route_short_name, route_long_name
),
route_journey_stats AS (
    SELECT
        route_short_name,
        COUNT(*) AS total_passenger_journeys,
        ROUND(AVG(observed_journey_time_seconds) / 60.0, 2) AS avg_journey_time_min,
        ROUND(MEDIAN(observed_journey_time_seconds) / 60.0, 2) AS median_journey_time_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.10) / 60.0, 2) AS p10_journey_time_min,
        ROUND(QUANTILE_CONT(observed_journey_time_seconds, 0.90) / 60.0, 2) AS p90_journey_time_min
    FROM journey_ml_ready
    GROUP BY route_short_name
)
SELECT
    s.route_short_name,
    s.route_long_name,
    s.total_segment_observations,
    s.distinct_trips,
    s.distinct_operating_dates,
    s.distinct_devices,
    s.distinct_stops,
    s.distinct_segments,
    -- Segment-level metrics (sec)
    s.avg_segment_run_time_sec,
    s.median_segment_run_time_sec,
    s.avg_segment_dwell_time_sec,
    s.median_segment_dwell_time_sec,
    s.avg_total_segment_time_sec,
    s.median_total_segment_time_sec,
    s.std_total_segment_time_sec,
    s.iqr_total_segment_time_sec,
    -- Journey-level metrics (min)
    j.total_passenger_journeys,
    j.avg_journey_time_min,
    j.median_journey_time_min,
    j.p10_journey_time_min,
    j.p90_journey_time_min
FROM route_segment_stats s
JOIN route_journey_stats j ON s.route_short_name = j.route_short_name
ORDER BY s.route_short_name;
