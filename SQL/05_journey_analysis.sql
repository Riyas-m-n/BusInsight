-- ==============================================================================
-- BusInsight - SQL Analysis
-- Query 05: Journey Length (Hop Tier) & Day-of-Week Analysis
-- Description: Analyzes passenger journey travel times across topological hop distances
-- (segments traversed) and calendar day of week.
-- Uses standard passenger journeys from journey_ml_ready.
-- ==============================================================================

-- Part A: Journey Performance by Hop-Distance Tier
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
),
hop_tier_summary AS (
    SELECT
        hop_tier,
        tier_rank,
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
),

-- Part B: Journey Performance by Day of Week & Weekend
day_of_week_summary AS (
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
)
-- Display Hop Tier Results (Can be queried independently by filtering or via script)
SELECT
    'HOP_TIER' AS analysis_type,
    hop_tier AS category_name,
    total_journeys,
    NULL AS distinct_trips,
    avg_duration_min,
    median_duration_min,
    p10_duration_min,
    p90_duration_min,
    iqr_duration_min,
    std_duration_min,
    cv_duration
FROM hop_tier_summary

UNION ALL

SELECT
    'DAY_OF_WEEK' AS analysis_type,
    day_name || ' (' || CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END || ')' AS category_name,
    total_journeys,
    distinct_trips,
    avg_duration_min,
    median_duration_min,
    p10_duration_min,
    p90_duration_min,
    iqr_duration_min,
    std_duration_min,
    NULL AS cv_duration
FROM day_of_week_summary
ORDER BY analysis_type, category_name;
