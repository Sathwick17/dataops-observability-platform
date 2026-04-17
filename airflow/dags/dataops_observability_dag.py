from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import psycopg2
import os

# ---------------------------------------------------------------------------
# Default arguments — applied to every task in the DAG
# retries=1 means if a task fails, Airflow retries it once automatically
# retry_delay=5 minutes between retries
# ---------------------------------------------------------------------------
default_args = {
    "owner": "dataops",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ---------------------------------------------------------------------------
# DAG definition
# schedule_interval="@hourly" means this DAG runs every hour automatically
# catchup=False means don't backfill missed runs
# ---------------------------------------------------------------------------
with DAG(
    dag_id="dataops_observability",
    default_args=default_args,
    description="Refreshes dbt models and checks SLA breaches hourly",
    schedule_interval="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["dataops", "observability"],
) as dag:

    # -----------------------------------------------------------------------
    # Task 1: Run dbt models
    # BashOperator runs a shell command
    # This refreshes all 3 mart tables: fct_pipeline_failures,
    # fct_sla_breaches, fct_schema_change_impact
    # -----------------------------------------------------------------------
    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="cd /opt/airflow/dags && echo 'dbt run placeholder - replace with actual dbt run command in Phase 9'",
    )

    # -----------------------------------------------------------------------
    # Task 2: Check SLA breaches
    # PythonOperator runs a Python function
    # Counts breaches in the last hour and logs to Postgres
    # -----------------------------------------------------------------------
    def check_sla_breaches():
        conn = psycopg2.connect(
            host="dataops_postgres",
            port=5432,
            dbname=os.getenv("POSTGRES_DB", "dataops"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*)
            FROM public.fct_sla_breaches
            WHERE sla_status = 'breached'
            AND event_date >= CURRENT_DATE
        """)
        breach_count = cur.fetchone()[0]
        print(f"SLA breaches today: {breach_count}")
        cur.close()
        conn.close()
        return breach_count

    check_sla = PythonOperator(
        task_id="check_sla_breaches",
        python_callable=check_sla_breaches,
    )

    # -----------------------------------------------------------------------
    # Task 3: Log pipeline summary
    # Counts today's failures and prints a summary
    # -----------------------------------------------------------------------
    def log_pipeline_summary():
        conn = psycopg2.connect(
            host="dataops_postgres",
            port=5432,
            dbname=os.getenv("POSTGRES_DB", "dataops"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) AS total_events,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS total_failures,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS total_successes
            FROM public.raw_pipeline_events
            WHERE DATE(event_timestamp) = CURRENT_DATE
        """)
        row = cur.fetchone()
        print(f"Today's Summary — Total: {row[0]} | Failures: {row[1]} | Successes: {row[2]}")
        cur.close()
        conn.close()

    log_summary = PythonOperator(
        task_id="log_pipeline_summary",
        python_callable=log_pipeline_summary,
    )

    # -----------------------------------------------------------------------
    # Task dependencies — defines the order tasks run
    # run_dbt_models first, then check_sla, then log_summary
    # -----------------------------------------------------------------------
    run_dbt_models >> check_sla >> log_summary