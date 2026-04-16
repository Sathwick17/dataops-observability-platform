import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# --- Config ---
KAFKA_BROKER = "localhost:9092"
TOPIC = "pipeline-events"

PIPELINES = [
    {"pipeline_id": 1, "pipeline_name": "fraud_detection_pipeline"},
    {"pipeline_id": 2, "pipeline_name": "payments_pipeline"},
    {"pipeline_id": 3, "pipeline_name": "daily_sales_pipeline"},
    {"pipeline_id": 4, "pipeline_name": "user_activity_pipeline"},
    {"pipeline_id": 5, "pipeline_name": "inventory_pipeline"},
    {"pipeline_id": 6, "pipeline_name": "marketing_pipeline"},
]

EVENT_TYPES = ["task_start", "task_end", "pipeline_start", "pipeline_end"]
STATUSES = ["success", "failed", "running"]
ERROR_MESSAGES = [
    "Connection timeout",
    "Data quality check failed",
    "Out of memory",
    "Schema mismatch",
    None, None, None  # None = no error (weighted towards success
]

def generate_event():
    pipeline = random.choice(PIPELINES)
    status = random.choice(STATUSES)
    return {
        "pipeline_id": pipeline["pipeline_id"],
        "pipeline_name": pipeline["pipeline_name"],
        "event_type": random.choice(EVENT_TYPES),
        "status": status,
        "event_timestamp": datetime.utcnow().isoformat(),
        "duration_sec": random.randint(30, 900),
        "records_in": random.randint(1000, 100000),
        "records_out": random.randint(800, 100000),
        "error_message": random.choice(ERROR_MESSAGES) if status == "failed" else None
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    print(f"Producer started. Publishing to topic: {TOPIC}")

    while True:
        event = generate_event()
        producer.send(TOPIC, value=event)
        producer.flush()
        print(f"Published: {event['pipeline_name']} | {event['status']} | {event['event_timestamp']}")
        time.sleep(5)

if __name__ == "__main__":
    main()