CREATE TABLE slas (
    sla_id SERIAL PRIMARY KEY,
    pipeline_id INT REFERENCES pipelines(pipeline_id),
    expected_completion_time TIME,
    max_runtime_sec INT,
    freshness_threshold_min INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE schema_change_events (
    change_id SERIAL PRIMARY KEY,
    pipeline_id INT REFERENCES pipelines(pipeline_id),
    asset_id INT REFERENCES data_assets(asset_id),
    change_type TEXT,
    old_schema TEXT,
    new_schema TEXT,
    initiated_by TEXT,
    change_ts TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);