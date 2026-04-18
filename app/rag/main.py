# app/rag/main.py
#
# The RAG layer. Accepts a question via HTTP, fetches relevant
# context from PostgreSQL, builds a prompt, sends it to Ollama,
# and returns the LLM's answer.

import os
import httpx
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="DataOps Failure Intelligence API",
    description="Ask natural language questions about your pipeline health",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# These are read from environment variables set in docker-compose.yml
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = "llama3.2"

DB_CONFIG = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     os.getenv("POSTGRES_PORT", 5432),
    "dbname":   os.getenv("POSTGRES_DB", "dataops"),
    "user":     os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
}


# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class QuestionRequest(BaseModel):
    """
    What the user sends in the request body.
    Example: {"question": "Which pipeline failed the most?"}
    """
    question: str


class AnswerResponse(BaseModel):
    """
    What we send back.
    question — echoes back what was asked
    answer   — the LLM's response
    context  — the raw data we fed to the LLM (useful for debugging)
    """
    question: str
    answer: str
    context: str


# ─────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def fetch_impact_assessments():
    """
    Fetches the most recent impact assessments.
    These are the plain-English summaries we built in Phase 7.
    The LLM reads these to answer questions about schema changes.
    """
    query = """
        SELECT
            cia.severity_label,
            cia.impact_score,
            cia.change_type,
            cia.impacted_pipeline_count,
            cia.summary_text,
            cia.assessed_at
        FROM change_impact_assessments cia
        ORDER BY cia.impact_score DESC
        LIMIT 10
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    conn.close()

    # Format each row as a readable string
    # This is what goes into the LLM prompt
    results = []
    for row in rows:
        results.append(
            f"[{row[0]} | Score: {row[1]} | Type: {row[2]} | "
            f"Pipelines affected: {row[3]}]\n{row[4]}"
        )
    return "\n\n".join(results)


def fetch_pipeline_failures():
    """
    Fetches recent pipeline failure counts per pipeline.
    Joins raw_pipeline_events to pipelines to get the pipeline name
    since raw_pipeline_events only stores pipeline_id.
    """
    query = """
        SELECT
            p.pipeline_name,
            COUNT(*) as failure_count,
            MAX(rpe.event_timestamp) as last_failure
        FROM raw_pipeline_events rpe
        JOIN pipelines p ON rpe.pipeline_id = p.pipeline_id
        WHERE rpe.status = 'failed'
        GROUP BY p.pipeline_name
        ORDER BY failure_count DESC
        LIMIT 10
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append(
            f"Pipeline: {row[0]} | Failures: {row[1]} | Last failure: {row[2]}"
        )
    return "\n".join(results)


def fetch_sla_breaches():
    """
    Fetches SLA breach summary.
    Used to answer questions about SLA performance.
    """
    query = """
        SELECT
            pipeline_name,
            COUNT(*) as breach_count,
            MAX(event_date) as last_breach
        FROM fct_sla_breaches
        WHERE sla_status = 'breached'
        GROUP BY pipeline_name
        ORDER BY breach_count DESC
        LIMIT 10
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append(
            f"Pipeline: {row[0]} | SLA Breaches: {row[1]} | Last breach: {row[2]}"
        )
    return "\n".join(results)


# ─────────────────────────────────────────────
# CONTEXT BUILDER
# ─────────────────────────────────────────────

def build_context():
    """
    Fetches all three data sources and combines them into
    one block of text that gets sent to the LLM as context.

    This is the R in RAG — Retrieval.
    We retrieve relevant data before generation.
    """
    impact    = fetch_impact_assessments()
    failures  = fetch_pipeline_failures()
    breaches  = fetch_sla_breaches()

    return f"""
=== SCHEMA CHANGE IMPACT ASSESSMENTS ===
{impact}

=== PIPELINE FAILURE COUNTS ===
{failures}

=== SLA BREACH SUMMARY ===
{breaches}
""".strip()


# ─────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────

def build_prompt(question: str, context: str) -> str:
    """
    Combines the context and the question into a single prompt.

    The system instruction tells the LLM how to behave.
    The context is the data we retrieved.
    The question is what the user asked.

    This is the A in RAG — Augmented Generation.
    We augment the prompt with real data before asking the LLM to generate.
    """
    return f"""You are a DataOps pipeline monitoring assistant.
You have access to real data from a pipeline observability platform.
Answer the user's question using ONLY the data provided below.
Be concise, specific, and refer to actual pipeline names and numbers.
If the data doesn't contain enough information to answer, say so clearly.

=== PLATFORM DATA ===
{context}

=== USER QUESTION ===
{question}

=== YOUR ANSWER ==="""


# ─────────────────────────────────────────────
# OLLAMA CALLER
# ─────────────────────────────────────────────

async def call_ollama(prompt: str) -> str:
    """
    Sends the prompt to Ollama's HTTP API and returns the response.

    Ollama runs locally inside Docker on port 11434.
    We call the /api/generate endpoint with our model and prompt.

    stream=False means we wait for the full response before returning.
    For a production system you'd use streaming, but this is cleaner
    for our use case.

    timeout=120 seconds — LLaMA can be slow on CPU, give it time.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama error: {response.text}"
            )

        return response.json()["response"]


# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/")
def root():
    """Health check endpoint — confirms the API is running."""
    return {"status": "ok", "message": "DataOps RAG API is running"}


@app.get("/health")
def health():
    """Checks database connectivity."""
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest):
    """
    Main endpoint. Accepts a question, runs the full RAG pipeline,
    returns an answer.

    POST /ask
    Body: {"question": "Which pipeline failed the most?"}
    """
    try:
        # Step 1: Retrieve context from database
        context = build_context()

        # Step 2: Build the prompt
        prompt = build_prompt(request.question, context)

        # Step 3: Send to LLaMA via Ollama
        answer = await call_ollama(prompt)

        return AnswerResponse(
            question=request.question,
            answer=answer.strip(),
            context=context
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))