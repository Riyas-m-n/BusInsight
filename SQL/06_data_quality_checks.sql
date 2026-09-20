-- ==============================================================================
-- BusInsight - SQL Analysis
-- Query 06: Analytical Data Quality & Integrity Validation
-- Description: Systematically executes 12 data-quality and boundary checks
-- confirming established Task 1/2/3 properties across the analytical datasets.
-- ==============================================================================

WITH validation_results AS (
    -- Check 1: Row count of analytical_segment_data (Expected: 785,976)
    SELECT
        '1. analytical_segment_data row count' AS check_name,
        'analytical_segment_data' AS target_dataset,
        '785976' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 785976 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM analytical_segment_data

    UNION ALL

    -- Check 2: Row count of journey_training_data (Expected: 15,277,204)
    SELECT
        '2. journey_training_data row count' AS check_name,
        'journey_training_data' AS target_dataset,
        '15277204' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 15277204 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM journey_training_data

    UNION ALL

    -- Check 3: Row count of journey_ml_ready (Expected: 14,477,686)
    SELECT
        '3. journey_ml_ready row count' AS check_name,
        'journey_ml_ready' AS target_dataset,
        '14477686' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 14477686 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM journey_ml_ready

    UNION ALL

    -- Check 4: Duplicate (trip_id, segment) in analytical_segment_data (Expected: 0)
    SELECT
        '4. Duplicate (trip_id, segment) pairs' AS check_name,
        'analytical_segment_data' AS target_dataset,
        '0' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM (
        SELECT trip_id, segment
        FROM analytical_segment_data
        GROUP BY trip_id, segment
        HAVING COUNT(*) > 1
    ) dupes

    UNION ALL

    -- Check 5: Negative run time in analytical_segment_data (Expected: 0)
    SELECT
        '5. Negative run_time_in_seconds' AS check_name,
        'analytical_segment_data' AS target_dataset,
        '0' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM analytical_segment_data
    WHERE run_time_in_seconds < 0

    UNION ALL

    -- Check 6: Negative dwell time in analytical_segment_data (Expected: 0)
    SELECT
        '6. Negative dwell_time_in_seconds' AS check_name,
        'analytical_segment_data' AS target_dataset,
        '0' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM analytical_segment_data
    WHERE dwell_time_in_seconds < 0

    UNION ALL

    -- Check 7: Distinct route count in analytical_segment_data (Expected: 3)
    SELECT
        '7. Distinct route_short_name count' AS check_name,
        'analytical_segment_data' AS target_dataset,
        '3' AS expected_value,
        CAST(COUNT(DISTINCT route_short_name) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(DISTINCT route_short_name) = 3 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM analytical_segment_data

    UNION ALL

    -- Check 8: Distinct direction count in analytical_segment_data (Expected: 2)
    SELECT
        '8. Distinct direction_id count' AS check_name,
        'analytical_segment_data' AS target_dataset,
        '2' AS expected_value,
        CAST(COUNT(DISTINCT direction_id) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(DISTINCT direction_id) = 2 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM analytical_segment_data

    UNION ALL

    -- Check 9: Zero-duration journeys in journey_ml_ready (Expected: 0)
    SELECT
        '9. Zero-duration journeys in ML-ready' AS check_name,
        'journey_ml_ready' AS target_dataset,
        '0' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM journey_ml_ready
    WHERE observed_journey_time_seconds <= 0

    UNION ALL

    -- Check 10: Segment 1 origins in journey_ml_ready (Expected: 0 per locked exclusion)
    SELECT
        '10. Segment 1 origin journeys in ML-ready' AS check_name,
        'journey_ml_ready' AS target_dataset,
        '0' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM journey_ml_ready
    WHERE start_segment = 1

    UNION ALL

    -- Check 11: September 3-4 records in journey_ml_ready (Expected: 0 per locked exclusion)
    SELECT
        '11. Sep 3-4 records in journey_ml_ready' AS check_name,
        'journey_ml_ready' AS target_dataset,
        '0' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM journey_ml_ready
    WHERE date IN ('03-09-24', '04-09-24', '2024-09-03', '2024-09-04')

    UNION ALL

    -- Check 12: September 3-4 preserved in analytical_segment_data (Expected: > 0)
    SELECT
        '12. Sep 3-4 preserved in analytical_segment_data' AS check_name,
        'analytical_segment_data' AS target_dataset,
        '> 0' AS expected_value,
        CAST(COUNT(*) AS VARCHAR) AS observed_value,
        CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM analytical_segment_data
    WHERE strftime(date, '%Y-%m-%d') IN ('2024-09-03', '2024-09-04')
)
SELECT * FROM validation_results;
