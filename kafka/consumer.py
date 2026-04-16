import json
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime
import os

# --- Config ---
KAFKA_BROKER = "localhost:9092"
TOPIC = "pipeline-events"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": os.getenv("POSTGRES_DB", "dataops"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres")
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def insert_event(conn, event):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO public.raw_pipeline_events (
                pipeline_id,
                task_id,
                event_type,
                status,
                event_timestamp,
                duration_sec,
                records_in,
                records_out,
                error_message,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            event.get("pipeline_id"),
            None,
            event.get("event_type"),
            event.get("status"),
            event.get("event_timestamp"),
            event.get("duration_sec"),
            event.get("records_in"),
            event.get("records_out"),
            event.get("error_message"),
            datetime.utcnow()
        ))
        conn.commit()

def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="latest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )

    conn = get_db_connection()
    print(f"Consumer started. Listening to topic: {TOPIC}")

    for message in consumer:
        event = message.value
        print(f"Consumed: {event['pipeline_name']} | {event['status']} | {event['event_timestamp']}")
        insert_event(conn, event)
        print(f"Inserted into Postgres")

if __name__ == "__main__":
    main()