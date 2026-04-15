<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0ea5e9,100:059669&height=160&section=header&text=DataOps%20Observability%20Platform&fontSize=28&fontColor=ffffff&fontAlignY=50&desc=Pipeline%20Monitoring%20%7C%20Schema%20Drift%20%7C%20SLA%20Tracking%20%7C%20RAG-Powered%20RCA&descAlignY=72&descSize=13" width="100%"/>

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-0ea5e9?style=for-the-badge&logo=python&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-0ea5e9?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## Overview

Modern data teams often lack centralized visibility into whether their pipelines are running on time, producing quality data, and delivering reliable outputs to downstream consumers. When failures occur, root cause investigation is slow and manual.

This platform addresses that gap — providing end-to-end observability across pipeline health, schema changes, SLA breaches, and downstream impact, with an AI-assisted RAG layer for incident investigation.

---

## What This Platform Does

- Tracks every pipeline run — status, duration, and records processed
- Detects failures, retries, and SLA breaches in real time
- Traces downstream impact when a schema change or failure occurs
- Monitors data quality across assets
- Provides AI-assisted root cause investigation via a RAG-based API

---

## Architecture

```
Python Event Generators / ETL Scripts
              │
              ▼
         Kafka Topics  ────►  Python Consumer / Ingestion
              │                          │
              ▼                          ▼
      Airflow Orchestration ────►  PostgreSQL Raw Layer
                                        │
                                        ▼
                                    dbt Core
                                        │
                                        ▼
                               Analytics Mart Layer
                                        │
                              ┌─────────┴──────────┐
                              ▼                    ▼
                           Grafana            FastAPI + RAG
                        Dashboards         (Ollama + LLaMA)
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Data generation, ETL scripts, Kafka producer/consumer |
| PostgreSQL | Raw and transformed data storage |
| Apache Kafka | Real-time event streaming |
| Apache Airflow | Workflow orchestration and scheduling |
| dbt Core | SQL transformations and data modeling |
| Grafana | Operational dashboards and observability |
| Ollama + LLaMA | Local RAG model for incident investigation |
| FastAPI | API interface for RAG-based troubleshooting |
| Docker Compose | Full local containerized environment |

---

## Database Schema

The platform models operational pipeline telemetry across these core tables:

| Table | Description |
|-------|-------------|
| `teams` | Ownership of pipelines |
| `pipelines` | Pipeline definitions and metadata |
| `tasks` | Individual steps within each pipeline |
| `data_assets` | Output datasets produced by pipelines |
| `slas` | SLA definitions per pipeline |
| `schema_change_events` | Tracks schema drift across assets |
| `raw_pipeline_events` | Core event log — failures, retries, completions |

---

## Project Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project Setup | ✅ Done |
| 1 | Base Data Layer | ✅ Done |
| 2 | Historical Data Generation & Batch ETL | ✅ Done |
| 3 | SQL Modeling and dbt Layer | ✅ Done |
| 4 | Grafana Dashboard Layer | ✅ Done |
| 5 | Kafka Streaming Layer | 🔄 In Progress |
| 6 | Airflow Orchestration | ⬜ Pending |
| 7 | Change Impact Logic | ⬜ Pending |
| 8 | RAG Layer (Ollama + FastAPI) | ⬜ Pending |
| 9 | Final Polish | ⬜ Pending |

---

## Repository Structure

```
dataops-observability-platform/
├── docker-compose.yml
├── .env.example
├── app/
│   ├── generator/         # Synthetic data generation scripts
│   ├── ingestion/         # ETL loader scripts
│   ├── rag/               # RAG layer and FastAPI
│   └── utils/             # Shared utilities
├── sql/
│   ├── init/              # PostgreSQL init scripts
│   └── queries/           # Ad hoc queries
├── dbt/                   # dbt project
├── airflow/
│   └── dags/              # Airflow DAGs
├── kafka/                 # Kafka configs and helpers
├── data/
│   ├── seeds/             # Reference/seed data
│   ├── raw/               # Raw input files
│   └── generated/         # Synthetic generated data
└── docs/                  # Architecture diagrams and notes
```

---

## Setup

```bash
git clone https://github.com/Sathwick17/dataops-observability-platform.git
cd dataops-observability-platform
cp .env.example .env
docker compose up -d
```

> **Status:** Currently in active development. Building incrementally with clean commits.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:059669,100:0ea5e9&height=80&section=footer" width="100%"/>

</div>
