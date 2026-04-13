# DataOps Change Impact & Pipeline Failure Observability Platform

End-to-end DataOps platform for monitoring pipeline failures, schema changes, SLA breaches, and downstream impact using Kafka, Airflow, PostgreSQL, dbt, Grafana, and RAG.

## Problem Statement

Modern data teams often lack centralized visibility into whether their pipelines are running on time, producing quality data, and delivering reliable outputs to downstream consumers. When failures happen, root cause investigation is slow and manual. This platform addresses that gap.

## What This Platform Does

- Tracks every pipeline run — status, duration, records processed
- Detects failures, retries, and SLA breaches in real time
- Traces downstream impact when a schema change or failure occurs
- Monitors data quality across assets
- Provides AI-assisted root cause investigation via a RAG-based API

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data generation, ETL scripts, Kafka producer/consumer |
| PostgreSQL | Raw and transformed data storage |
| Apache Kafka | Real-time event streaming |
| Apache Airflow | Workflow orchestration and scheduling |
| dbt Core | SQL transformations and data modeling |
| Grafana | Operational dashboards and observability |
| Ollama + LLaMA | Local RAG model for incident investigation |
| FastAPI | API interface for RAG-based troubleshooting |
| Docker Compose | Full local containerized environment |

## Architecture

```text
Python Event Generators / ETL Scripts
              |
              v
         Kafka Topics  ────►  Python Consumer / Ingestion
              |                          |
              v                          v
      Airflow Orchestration ────►  PostgreSQL Raw Layer
                                        |
                                        v
                                    dbt Core
                                        |
                                        v
                               Analytics Mart Layer
                                        |
                              ┌─────────┴──────────┐
                              v                    v
                           Grafana            FastAPI + RAG
                        Dashboards         (Ollama + LLaMA)
```

## Project Phases

| Phase | Description | Status |
|---|---|---|
| 0 | Project Setup | ✅ Done |
| 1 | Base Data Layer | ✅ Done |
| 2 | Historical Data Generation & Batch ETL | 🔄 In Progress |
| 3 | SQL Modeling and dbt Layer | ⬜ Pending |
| 4 | Grafana Dashboard Layer | ⬜ Pending |
| 5 | Kafka Streaming Layer | ⬜ Pending |
| 6 | Airflow Orchestration | ⬜ Pending |
| 7 | Change Impact Logic | ⬜ Pending |
| 8 | RAG Layer (Ollama + FastAPI) | ⬜ Pending |
| 9 | Final Polish | ⬜ Pending |

## Database Schema

The platform models operational pipeline telemetry across these core tables:

- `teams` — ownership of pipelines
- `pipelines` — pipeline definitions and metadata
- `tasks` — individual steps within each pipeline
- `data_assets` — output datasets produced by pipelines
- `slas` — SLA definitions per pipeline
- `schema_change_events` — tracks schema drift across assets
- `raw_pipeline_events` — core event log (failures, retries, completions)

## Repository Structure

```text
dataops-observability-platform/
├── docker-compose.yml
├── .env.example
├── README.md
├── app/
│   ├── generator/         # Synthetic data generation scripts
│   ├── ingestion/         # ETL loader scripts
│   ├── rag/               # RAG layer and FastAPI
│   └── utils/             # Shared utilities
├── sql/
│   ├── init/              # Postgres init scripts
│   └── queries/           # Ad hoc queries
├── dbt/                   # dbt project
├── airflow/
│   ├── dags/              # Airflow DAGs
│   ├── logs/
│   └── plugins/
├── kafka/                 # Kafka configs and helpers
├── data/
│   ├── seeds/             # Reference/seed data
│   ├── raw/               # Raw input files
│   └── generated/         # Synthetic generated data
└── docs/                  # Architecture diagrams and notes
```

## Key Use Cases

- Monitor pipeline success rates, retry patterns, and runtime trends
- Track SLA breaches by pipeline and team
- Detect schema changes and trace downstream asset impact
- Investigate root causes using AI-assisted troubleshooting
- Surface data quality issues before they reach consumers

## Resume Value

This project demonstrates end-to-end skills across:

- **Data Engineering** — Kafka, Airflow, ETL/ELT, Docker, pipeline design
- **Analytics Engineering** — dbt modeling, SQL marts, data quality
- **Data Analyst** — Grafana dashboards, KPI monitoring, trend analysis
- **AI/ML Engineering** — RAG implementation, local LLM integration, FastAPI

## Setup

```bash
git clone https://github.com/Sathwick17/dataops-observability-platform.git
cd dataops-observability-platform
cp .env.example .env
docker compose up -d
```

## Status

Currently in active development. Building incrementally with clean commits.

## Author

Sathwick Kiran