CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_name TEXT NOT NULL,
    team_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pipelines (
    pipeline_id SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    team_id INT REFERENCES teams(team_id),
    schedule_type TEXT,
    criticality TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    pipeline_id INT REFERENCES pipelines(pipeline_id),
    task_name TEXT NOT NULL,
    task_type TEXT,
    task_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE data_assets (
    asset_id SERIAL PRIMARY KEY,
    asset_name TEXT NOT NULL,
    pipeline_id INT REFERENCES pipelines(pipeline_id),
    asset_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw_pipeline_events (
    event_id SERIAL PRIMARY KEY,
    pipeline_id INT REFERENCES pipelines(pipeline_id),
    task_id INT REFERENCES tasks(task_id),
    event_type TEXT,
    status TEXT,
    event_timestamp TIMESTAMP,
    duration_sec INT,
    records_in INT,
    records_out INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
