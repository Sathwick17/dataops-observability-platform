import csv
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=os.getenv("POSTGRES_PORT", 5432),
        database=os.getenv("POSTGRES_DB", "dataops"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )

DATA_DIR = "data/generated"

def load_csv(conn, filepath, table, columns, transform=None):
    cursor = conn.cursor()
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if transform:
                row = transform(row)
            values = [row.get(col) or None for col in columns]
            placeholders = ", ".join(["%s"] * len(columns))
            cols = ", ".join(columns)
            cursor.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", values)
    conn.commit()
    cursor.close()
    print(f"Loaded {filepath} into {table}")

def run():
    conn = get_connection()

    # Load teams
    load_csv(conn, f"{DATA_DIR}/teams.csv", "teams",
             ["team_id", "team_name", "team_email", "created_at"])

    # Load pipelines
    load_csv(conn, f"{DATA_DIR}/pipelines.csv", "pipelines",
             ["pipeline_id", "pipeline_name", "team_id", "schedule_type", "criticality", "created_at"])

    # Load tasks
    load_csv(conn, f"{DATA_DIR}/tasks.csv", "tasks",
             ["task_id", "pipeline_id", "task_name", "task_type", "task_order", "created_at"])

    # Load data assets
    load_csv(conn, f"{DATA_DIR}/data_assets.csv", "data_assets",
             ["asset_id", "asset_name", "pipeline_id", "asset_type", "created_at"])

    # Load slas
    load_csv(conn, f"{DATA_DIR}/slas.csv", "slas",
             ["sla_id", "pipeline_id", "expected_completion_time", "max_runtime_sec", "freshness_threshold_min", "created_at"])

    # Load schema change events
    load_csv(conn, f"{DATA_DIR}/schema_change_events.csv", "schema_change_events",
             ["change_id", "pipeline_id", "asset_id", "change_type", "old_schema", "new_schema", "initiated_by", "change_ts", "created_at"])

    # Load pipeline events
    load_csv(conn, f"{DATA_DIR}/raw_pipeline_events.csv", "raw_pipeline_events",
             ["event_id", "pipeline_id", "task_id", "event_type", "status", "event_timestamp", "duration_sec", "records_in", "records_out", "error_message", "created_at"])

    conn.close()
    print("All data loaded successfully")

if __name__ == "__main__":
    run()