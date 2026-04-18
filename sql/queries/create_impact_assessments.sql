-- sql/queries/create_impact_assessments.sql
--
-- This table stores the RESULTS of our impact analysis.
-- Every time a schema change is detected, the analyzer runs,
-- figures out the blast radius, and writes one row here.

CREATE TABLE IF NOT EXISTS change_impact_assessments (
    assessment_id            SERIAL PRIMARY KEY,

    -- Links back to the schema change that triggered this assessment
    -- If the change_id doesn't exist in schema_change_events, the insert will fail.
    -- That's intentional — it enforces data integrity.
    change_id                INTEGER REFERENCES schema_change_events(change_id),

    assessed_at              TIMESTAMP DEFAULT NOW(),

    -- What asset changed
    changed_asset_id         INTEGER REFERENCES data_assets(asset_id),
    change_type              VARCHAR(50),

    -- The blast radius numbers (used by Grafana)
    impacted_pipeline_count  INTEGER,
    impacted_asset_count     INTEGER,

    -- Comma-separated names of CRITICAL pipelines that are at risk
    -- Stored as text because it's for display/alerting, not for joining
    critical_pipelines       TEXT,

    -- The risk score (0 to 100) and its label
    impact_score             NUMERIC(5, 2),
    severity_label           VARCHAR(20),

    -- Plain English summary — this is what the LLM reads in Phase 8
    summary_text             TEXT
);