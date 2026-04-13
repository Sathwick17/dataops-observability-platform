SELECT
    sc.change_id,
    sc.change_ts::date AS change_date,
    sc.change_type,
    sc.initiated_by,
    sc.pipeline_id,
    p.pipeline_name,
    p.criticality,
    sc.asset_id,
    da.asset_name,
    sc.old_schema,
    sc.new_schema,
    COUNT(e.event_id) AS failures_after_change
FROM schema_change_events sc
JOIN {{ ref('stg_pipelines') }} p
    ON sc.pipeline_id = p.pipeline_id
JOIN data_assets da
    ON sc.asset_id = da.asset_id
LEFT JOIN {{ ref('stg_pipeline_events') }} e
    ON e.pipeline_id = sc.pipeline_id
    AND e.status = 'failed'
    AND e.event_timestamp > sc.change_ts
    AND e.event_timestamp < sc.change_ts + INTERVAL '24 hours'
GROUP BY
    sc.change_id,
    sc.change_ts,
    sc.change_type,
    sc.initiated_by,
    sc.pipeline_id,
    p.pipeline_name,
    p.criticality,
    sc.asset_id,
    da.asset_name,
    sc.old_schema,
    sc.new_schema
ORDER BY sc.change_ts DESC