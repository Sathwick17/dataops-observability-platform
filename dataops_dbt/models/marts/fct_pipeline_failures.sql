SELECT
    e.event_date,
    e.pipeline_id,
    p.pipeline_name,
    p.criticality,
    p.schedule_type,
    COUNT(*) AS failure_count,
    COUNT(DISTINCT e.task_id) AS failed_tasks,
    ROUND(AVG(e.duration_sec)::numeric, 2) AS avg_failure_duration_sec,
    MIN(e.event_timestamp) AS first_failure_time,
    MAX(e.event_timestamp) AS last_failure_time
FROM {{ ref('stg_pipeline_events') }} e
JOIN {{ ref('stg_pipelines') }} p
    ON e.pipeline_id = p.pipeline_id
WHERE e.status = 'failed'
GROUP BY
    e.event_date,
    e.pipeline_id,
    p.pipeline_name,
    p.criticality,
    p.schedule_type
ORDER BY e.event_date DESC, failure_count DESC