# dataops-observability-platform

End-to-end DataOps platform for monitoring pipeline failures, schema changes, SLA breaches, and downstream impact using Kafka, Airflow, PostgreSQL, dbt, Superset, and RAG.

# DataOps Change Impact & Pipeline Failure Observability Platform

An end-to-end DataOps project that simulates pipeline execution events, schema changes, data quality issues, and operational incidents to monitor downstream impact, SLA breaches, and pipeline reliability.

This project is being built as a local, fully containerized data platform using Docker, with a focus on modern data engineering workflows across batch ETL, event-driven ingestion, orchestration, transformation, dashboarding, and retrieval-augmented troubleshooting.

## Goal

Modern data teams often struggle to answer questions like:

- What changed before this pipeline started failing?
- Which downstream assets were impacted by a schema change?
- Which pipelines are repeatedly breaching SLAs?
- Are data quality issues isolated or recurring across assets?
- How can engineers and analysts investigate failures faster?

This project aims to build a centralized observability platform to answer those questions using a combination of streaming events, warehouse modeling, orchestration, BI dashboards, and an optional RAG-based troubleshooting layer.

## Project Scope

The platform will:

- Simulate pipeline and task lifecycle events
- Capture schema change and data quality events
- Store raw operational data in PostgreSQL
- Use dbt to create clean, analytics-ready models
- Track pipeline health, SLA breaches, and downstream impact
- Surface operational insights through dashboards
- Add a RAG-based assistant for grounded failure investigation

## Tech Stack

- **Python** — event generation, ETL scripts, ingestion, helper services
- **Docker Compose** — local orchestration of all services
- **PostgreSQL** — raw and transformed operational data storage
- **Apache Kafka** — streaming pipeline, schema, and incident events
- **Apache Airflow** — workflow orchestration, scheduling, and monitoring
- **dbt Core** — SQL transformations, testing, and modeling
- **Apache Superset** — dashboarding and operational analytics
- **RAG layer** — retrieval-based troubleshooting over logs, metadata, and runbooks
- **GitHub** — version control, documentation, and portfolio visibility

## Planned Architecture

Python Event Generators / ETL
            |
            v
         Kafka Topics  --->  Python Consumer / Ingestion
            |                          |
            v                          v
        Airflow Orchestration ---> PostgreSQL Raw Layer
                                      |
                                      v
                                   dbt Core
                                      |
                                      v
                              Analytics / Mart Layer
                                      |
                                      v
                                Apache Superset
                                      |
                                      v
                         RAG Troubleshooting Assistant
