SELECT
    event_id,
    pipeline_id,
    task_id,
    event_type,
    status,
    event_timestamp::timestamp AS event_timestamp,
    event_timestamp::date AS event_date,
    duration_sec,
    records_in,
    records_out,
    error_message,
    created_at
FROM raw_pipeline_events