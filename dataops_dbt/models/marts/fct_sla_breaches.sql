SELECT
    e.event_date,
    e.pipeline_id,
    p.pipeline_name,
    p.criticality,
    s.expected_completion_time,
    s.max_runtime_sec,
    MAX(e.event_timestamp) AS actual_completion_time,
    MAX(e.duration_sec) AS actual_runtime_sec,
    CASE
        WHEN MAX(e.event_timestamp)::time > s.expected_completion_time
        THEN 'breached'
        ELSE 'on_time'
    END AS sla_status,
    CASE
        WHEN MAX(e.duration_sec) > s.max_runtime_sec
        THEN 'exceeded'
        ELSE 'within_limit'
    END AS runtime_status
FROM {{ ref('stg_pipeline_events') }} e
JOIN {{ ref('stg_pipelines') }} p
    ON e.pipeline_id = p.pipeline_id
JOIN {{ ref('stg_slas') }} s
    ON e.pipeline_id = s.pipeline_id
WHERE e.event_type = 'pipeline_completed'
GROUP BY
    e.event_date,
    e.pipeline_id,
    p.pipeline_name,
    p.criticality,
    s.expected_completion_time,
    s.max_runtime_sec
ORDER BY e.event_date DESC