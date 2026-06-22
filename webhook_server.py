"""
webhook_server.py
-----------------
FastAPI entry point. Receives webhooks and API calls,
runs them through Agentspan pipelines, returns results.

Startup:
  - Initialises OpenTelemetry tracer
  - Connects the Agentspan runtime
  - Serves the dashboard UI at /
"""

import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from agentspan.agents import AgentRuntime

from observability import init_tracer
from config import settings

app = FastAPI(title="ConstructAI — Multi-Agent Site Intelligence")
TEMPLATES = Path(__file__).parent / "templates"

# Agentspan runtime — shared across all requests
_runtime = AgentRuntime()


@app.on_event("startup")
def on_startup():
    init_tracer("construction-ai")
    print("[STARTUP] OpenTelemetry tracer initialised")
    print("[STARTUP] Agentspan runtime ready")


@app.on_event("shutdown")
def on_shutdown():
    _runtime.__exit__(None, None, None)


# ── Dashboard UI ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse((TEMPLATES / "dashboard.html").read_text())


@app.get("/health")
def health():
    return {"status": "ok", "service": "ConstructAI", "agents": 6}


# ── Site update (WhatsApp / email / form) ────────────────────────────────────

@app.post("/update")
async def submit_update(request: Request):
    """
    Receives a site update from any source.
    Runs it through: ingestion_agent >> extraction_agent >> storage_agent
    then fires alert_agent in parallel if needed.
    """
    from agents.pipeline import update_pipeline

    body = await request.json()
    content    = body.get("content", "").strip()
    sender     = body.get("sender", "api")
    source     = body.get("source", "form")
    project_id = body.get("project_id", settings.default_project_id)

    if not content:
        return {"status": "error", "reason": "content is required"}

    prompt = json.dumps({
        "content": content,
        "sender": sender,
        "source": source,
        "project_id": project_id,
    })

    result = _runtime.run(update_pipeline, prompt)
    return {"status": "ok", "result": result.output if hasattr(result, "output") else str(result)}


@app.post("/webhook/whatsapp")
async def receive_whatsapp(request: Request):
    """Twilio WhatsApp inbound webhook."""
    from agents.pipeline import update_pipeline

    data = await request.form()
    content = data.get("Body", "").strip()
    sender  = data.get("From", "unknown")

    if not content:
        return {"status": "ignored"}

    prompt = json.dumps({
        "content": content,
        "sender": sender,
        "source": "whatsapp",
        "project_id": settings.default_project_id,
    })

    result = _runtime.run(update_pipeline, prompt)
    return {"status": "ok"}


@app.post("/webhook/email")
async def receive_email(request: Request):
    """SendGrid Inbound Parse webhook."""
    from agents.pipeline import update_pipeline

    data = await request.form()
    content = (data.get("text") or data.get("html") or "").strip()
    sender  = data.get("from", "unknown")

    if not content:
        return {"status": "ignored"}

    prompt = json.dumps({
        "content": content,
        "sender": sender,
        "source": "email",
        "project_id": settings.default_project_id,
    })

    result = _runtime.run(update_pipeline, prompt)
    return {"status": "ok"}


# ── Daily report ─────────────────────────────────────────────────────────────

@app.post("/report/generate")
async def generate_report(request: Request):
    """Trigger report generation on demand (also called by scheduler)."""
    from agents.pipeline import report_pipeline

    body       = await request.json()
    project_id = body.get("project_id", settings.default_project_id)
    today      = date.today().isoformat()

    result = _runtime.run(
        report_pipeline,
        json.dumps({"project_id": project_id, "report_date": today}),
    )
    return {"status": "ok", "result": result.output if hasattr(result, "output") else str(result)}


# ── PM Chatbot ───────────────────────────────────────────────────────────────

@app.post("/ask")
async def ask_question(request: Request):
    """PM asks a natural-language question about today's site activity."""
    from agents.pipeline import chatbot_pipeline

    body       = await request.json()
    question   = body.get("question", "").strip()
    project_id = body.get("project_id", settings.default_project_id)

    if not question:
        return {"answer": "Please ask a question."}

    result = _runtime.run(
        chatbot_pipeline,
        json.dumps({"project_id": project_id, "question": question}),
    )
    return {"answer": result.output if hasattr(result, "output") else str(result)}
