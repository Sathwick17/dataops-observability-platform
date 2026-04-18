import psycopg2
import os
from datetime import datetime


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "dataops"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )


def get_recent_schema_changes(conn, hours_back=24):
    query = """
        SELECT
            sce.change_id,
            sce.asset_id,
            sce.pipeline_id,
            sce.change_type,
            sce.change_ts,
            da.asset_name,
            p.pipeline_name,
            p.criticality
        FROM schema_change_events sce
        JOIN data_assets da   ON sce.asset_id    = da.asset_id
        JOIN pipelines p      ON sce.pipeline_id  = p.pipeline_id
        LEFT JOIN change_impact_assessments cia ON sce.change_id = cia.change_id
        WHERE sce.change_ts >= NOW() - INTERVAL '{hours} hours'
          AND cia.assessment_id IS NULL
        ORDER BY sce.change_ts DESC
    """.format(hours=int(hours_back))

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    columns = [
        "change_id", "asset_id", "pipeline_id", "change_type",
        "change_ts", "asset_name", "pipeline_name", "criticality"
    ]
    return [dict(zip(columns, row)) for row in rows]


def get_downstream_impact(conn, asset_id, source_pipeline_id):
    query = """
        SELECT DISTINCT
            p.pipeline_id,
            p.pipeline_name,
            p.criticality,
            da.asset_id,
            da.asset_name
        FROM data_assets da
        JOIN pipelines p ON da.pipeline_id = p.pipeline_id
        WHERE da.asset_name = (
            SELECT asset_name FROM data_assets WHERE asset_id = %s
        )
          AND p.pipeline_id != %s
    """
    with conn.cursor() as cur:
        cur.execute(query, (asset_id, source_pipeline_id))
        rows = cur.fetchall()

    columns = ["pipeline_id", "pipeline_name", "criticality", "asset_id", "asset_name"]
    return [dict(zip(columns, row)) for row in rows]


def calculate_impact_score(change_type, downstream_pipelines, source_criticality):
    change_type_scores = {
        "column_drop":     40,
        "type_change":     30,
        "rename":          25,
        "nullable_change": 15,
        "column_add":      10,
    }
    base_score = change_type_scores.get(change_type, 20)
    criticality_bonus = 20 if source_criticality == "CRITICAL" else 0
    downstream_multiplier = min(len(downstream_pipelines) * 10, 40)
    return float(min(base_score + criticality_bonus + downstream_multiplier, 100))


def get_severity_label(score):
    if score >= 75:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 25:
        return "MEDIUM"
    else:
        return "LOW"


def build_summary_text(change, downstream_pipelines, score, severity):
    pipeline_names = [p["pipeline_name"] for p in downstream_pipelines]
    critical_ones  = [p["pipeline_name"] for p in downstream_pipelines
                      if p["criticality"] == "CRITICAL"]

    summary = (
        f"Schema change of type '{change['change_type']}' detected on asset "
        f"'{change['asset_name']}' (source pipeline: '{change['pipeline_name']}') "
        f"at {change['change_ts']}. "
        f"Impact score: {score:.1f}/100 — severity: {severity}. "
        f"Identified {len(downstream_pipelines)} downstream pipeline(s)"
    )

    if pipeline_names:
        summary += f": {', '.join(pipeline_names)}."
    else:
        summary += ". No downstream dependencies identified."

    if critical_ones:
        summary += f" CRITICAL pipelines at risk: {', '.join(critical_ones)}."

    return summary


def write_assessment(conn, change, downstream_pipelines, score, severity, summary):
    critical_names = ",".join(
        p["pipeline_name"] for p in downstream_pipelines
        if p["criticality"] == "CRITICAL"
    )

    query = """
        INSERT INTO change_impact_assessments (
            change_id,
            changed_asset_id,
            change_type,
            impacted_pipeline_count,
            impacted_asset_count,
            critical_pipelines,
            impact_score,
            severity_label,
            summary_text
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        change["change_id"],
        change["asset_id"],
        change["change_type"],
        len(downstream_pipelines),
        len(set(p["asset_id"] for p in downstream_pipelines)),
        critical_names or None,
        score,
        severity,
        summary
    )

    with conn.cursor() as cur:
        cur.execute(query, values)

    conn.commit()
    print(f"    ✓ Assessment written for change_id={change['change_id']}")


def run_impact_analysis(hours_back=24):
    print(f"\n[{datetime.now()}] ── Starting change impact analysis ──")
    conn = get_connection()

    try:
        changes = get_recent_schema_changes(conn, hours_back=hours_back)
        print(f"  Found {len(changes)} unprocessed schema change(s).")

        if not changes:
            print("  Nothing to process. Exiting cleanly.")
            return

        for change in changes:
            print(f"\n  → Processing change_id={change['change_id']} | "
                  f"type={change['change_type']} | asset={change['asset_name']}")

            downstream = get_downstream_impact(
                conn,
                asset_id=change["asset_id"],
                source_pipeline_id=change["pipeline_id"]
            )

            score    = calculate_impact_score(
                           change_type=change["change_type"],
                           downstream_pipelines=downstream,
                           source_criticality=change["criticality"]
                       )
            severity = get_severity_label(score)
            summary  = build_summary_text(change, downstream, score, severity)

            write_assessment(conn, change, downstream, score, severity, summary)

            print(f"    Score={score:.1f} | Severity={severity} | "
                  f"Downstream pipelines={len(downstream)}")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Analysis failed — rolled back. Reason: {e}")
        raise

    finally:
        conn.close()
        print(f"\n[{datetime.now()}] ── Analysis complete ──\n")


if __name__ == "__main__":
    run_impact_analysis(hours_back=99999)