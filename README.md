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
![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

</div>

---

## Overview

Modern data teams operate blind. Pipelines fail silently, schemas drift without warning, and SLA breaches go undetected until they hit a business stakeholder. Root cause investigation is slow, manual, and expensive.

**DataOps Observability Platform** is a production-grade monitoring system that gives data teams complete visibility into their pipeline ecosystem — tracking health, quality, and reliability in real time, and using **Google Gemini AI** to slash incident resolution time from hours to seconds.

Built end-to-end across streaming ingestion, SQL modeling, orchestration, and AI-powered investigation, this platform demonstrates what a mature DataOps practice looks like in practice.

---

## Business Impact

| Problem | Without This Platform | With This Platform |
|---|---|---|
| Pipeline failures | Discovered by downstream stakeholders | Caught in real time, team alerted immediately |
| Schema changes | Silent breakages across reports | Detected on arrival, impact traced automatically |
| SLA breaches | Noticed after the fact | Tracked proactively with breach prediction |
| Root cause analysis | Hours of manual log digging | Natural language query → AI-generated answer in seconds |
| Data trust | Low — teams unsure if numbers are right | High — every asset has a verified health status |

---

## What This Platform Does

- Monitors every pipeline run — status, duration, records processed, and failure reasons
- Detects schema drift across data assets and traces downstream impact automatically
- Tracks SLA compliance and surfaces breaches before they reach business consumers
- Ingests live pipeline events via Kafka for real-time observability
- Orchestrates all workflows through Airflow with retry logic and dependency management
- Serves AI-powered root cause analysis through a FastAPI endpoint backed by Google Gemini
- Validated across **10,000+ synthetic pipeline events** spanning failures, retries, schema changes, and SLA violations

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
                        Dashboards        (Google Gemini API)
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
| Google Gemini | Cloud LLM powering the RAG incident investigation layer |
| FastAPI | REST API interface for AI-powered troubleshooting |
| Docker Compose | Fully containerized local environment |

---

## Quick Start

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running. That's it.

**1. Clone the repo**
```bash
git clone https://github.com/Sathwick17/dataops-observability-platform.git
cd dataops-observability-platform
```

**2. Configure environment**
```bash
cp .env.example .env
```
Open `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```
> Get a free key at [Google AI Studio](https://aistudio.google.com/) — takes under a minute.

**3. Spin up the entire platform**
```bash
docker compose up -d
```
All services (PostgreSQL, Kafka, Airflow, Grafana, FastAPI) pull and start automatically. Wait ~60 seconds for everything to initialize.

**4. Access the platform**

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana Dashboards | http://localhost:3000 | admin / grafana123 |
| Airflow UI | http://localhost:8080 | admin / admin123 |
| RAG API (Swagger) | http://localhost:8000/docs | — |

**5. Generate pipeline data**
```bash
docker compose exec app python app/generator/generate_events.py
```
This seeds the platform with synthetic pipeline events so dashboards and the RAG layer have data to work with.

**To shut down:**
```bash
docker compose down
```

---

## Database Schema

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
| 5 | Kafka Streaming Layer | ✅ Done |
| 6 | Airflow Orchestration | ✅ Done |
| 7 | Change Impact Logic | ✅ Done |
| 8 | RAG Layer (Gemini + FastAPI) | ✅ Done |
| 9 | Final Polish & Scale Testing | ✅ Done |

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

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:059669,100:0ea5e9&height=80&section=footer" width="100%"/>

</div>
