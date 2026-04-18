from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import psycopg2
import os
import subprocess

default_args = {
    "owner": "dataops",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dataops_observability",
    default_args=default_args,
    description="Refreshes dbt models, checks SLA breaches, and runs change impact analysis hourly",
    schedule_interval="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["dataops", "observability"],
) as dag:

    # -----------------------------------------------------------------------
    # Task 1: Run dbt models
    # -----------------------------------------------------------------------
    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="cd /opt/airflow/dags && echo 'dbt run placeholder - replace with actual dbt run command in Phase 9'",
    )

    # -----------------------------------------------------------------------
    # Task 2: Check SLA breaches
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
    # Task 3: Run change impact analysis  ← NEW
    #
    # Calls the analyzer script we built in Phase 7.
    # subprocess.run() executes it as a child process, exactly like
    # running it manually in the terminal.
    #
    # Why subprocess instead of importing the function directly?
    # Airflow workers run in their own environment inside Docker.
    # Using subprocess keeps the DAG clean — it just orchestrates,
    # the actual logic lives in app/impact/.
    #
    # If the script crashes (returncode != 0), we raise an Exception
    # so Airflow marks the task as FAILED and triggers the retry.
    # -----------------------------------------------------------------------
    def run_change_impact_analysis():
        result = subprocess.run(
            ["python", "/opt/airflow/app/impact/change_impact_analyzer.py"],
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "POSTGRES_HOST": "dataops_postgres",
                "POSTGRES_DB":   "dataops",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres",
            }
        )
        print(result.stdout)
        if result.returncode != 0:
            raise Exception(f"Change impact analysis failed:\n{result.stderr}")

    analyze_impact = PythonOperator(
        task_id="analyze_change_impact",
        python_callable=run_change_impact_analysis,
    )

    # -----------------------------------------------------------------------
    # Task 4: Log pipeline summary
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
    # Task dependencies
    # BEFORE: run_dbt_models >> check_sla >> log_summary
    # AFTER:  run_dbt_models >> check_sla >> analyze_impact >> log_summary
    # -----------------------------------------------------------------------
    run_dbt_models >> check_sla >> analyze_impact >> log_summary