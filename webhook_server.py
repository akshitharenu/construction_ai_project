import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from config import settings

app = FastAPI(title="ConstructAI — Multi-Agent Site Intelligence")
TEMPLATES = Path(__file__).parent / "templates"


@app.on_event("startup")
def on_startup():
    try:
        from observability import init_tracer
        init_tracer("construction-ai")
        print("[STARTUP] OpenTelemetry tracer initialised")
    except Exception as e:
        print(f"[STARTUP] OTEL skipped: {e}")
    print("[STARTUP] ConstructAI ready")


# ── Dashboard UI ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse((TEMPLATES / "dashboard.html").read_text())


@app.get("/health")
def health():
    return {"status": "ok", "service": "ConstructAI", "agents": 6}


# ── Site update ───────────────────────────────────────────────────────────────

@app.post("/update")
async def submit_update(request: Request):
    from ai_processor.claude_client import extract_update
    from storage.database import insert_update, insert_processed
    from outputs.alerts import send_critical_alert

    body       = await request.json()
    content    = body.get("content", "").strip()
    sender     = body.get("sender", "api")
    source     = body.get("source", "form")
    project_id = body.get("project_id", settings.default_project_id)

    if not content:
        return {"status": "error", "reason": "content is required"}

    try:
        raw = insert_update(project_id, source, content, sender)
        result = extract_update(content, project_id, source, sender)
        insert_processed(
            update_id=raw["id"],
            project_id=project_id,
            summary=result["summary"],
            issues=result.get("issues", []),
            severity=result["severity"],
            delay_risk=result.get("delay_risk", False),
            action_required=result.get("action_required"),
        )
        if result["severity"] == "critical":
            try:
                send_critical_alert(project_id, result["summary"], result.get("action_required"))
            except Exception as e:
                print(f"[ALERT] failed: {e}")
        return {"status": "ok", "extracted": result}
    except Exception as e:
        print(f"[ERROR] /update: {e}")
        return {"status": "error", "reason": str(e)}


# ── WhatsApp webhook ──────────────────────────────────────────────────────────

@app.post("/webhook/whatsapp")
async def receive_whatsapp(request: Request):
    from ai_processor.claude_client import extract_update
    from storage.database import insert_update, insert_processed

    data    = await request.form()
    content = data.get("Body", "").strip()
    sender  = data.get("From", "unknown")
    if not content:
        return {"status": "ignored"}

    raw    = insert_update(settings.default_project_id, "whatsapp", content, sender)
    result = extract_update(content, settings.default_project_id, "whatsapp", sender)
    insert_processed(update_id=raw["id"], project_id=settings.default_project_id,
                     summary=result["summary"], issues=result.get("issues", []),
                     severity=result["severity"], delay_risk=result.get("delay_risk", False),
                     action_required=result.get("action_required"))
    return {"status": "ok", "severity": result["severity"]}


# ── Email webhook ─────────────────────────────────────────────────────────────

@app.post("/webhook/email")
async def receive_email(request: Request):
    from ai_processor.claude_client import extract_update
    from storage.database import insert_update, insert_processed

    data    = await request.form()
    content = (data.get("text") or data.get("html") or "").strip()
    sender  = data.get("from", "unknown")
    if not content:
        return {"status": "ignored"}

    raw    = insert_update(settings.default_project_id, "email", content, sender)
    result = extract_update(content, settings.default_project_id, "email", sender)
    insert_processed(update_id=raw["id"], project_id=settings.default_project_id,
                     summary=result["summary"], issues=result.get("issues", []),
                     severity=result["severity"], delay_risk=result.get("delay_risk", False),
                     action_required=result.get("action_required"))
    return {"status": "ok"}


# ── Generate report ───────────────────────────────────────────────────────────

@app.post("/report/generate")
async def generate_report(request: Request):
    from ai_processor.claude_client import generate_daily_report
    from storage.database import get_todays_updates, insert_daily_report

    body       = await request.json()
    project_id = body.get("project_id", settings.default_project_id)
    today      = date.today().isoformat()

    updates = get_todays_updates(project_id)
    if not updates:
        return {"report": "No updates received today.", "rag_status": "Green"}

    report = generate_daily_report(project_id, today, updates)
    rag    = "Red" if "Red" in report else "Amber" if "Amber" in report else "Green"
    insert_daily_report(project_id, today, report, rag)
    return {"report": report, "rag_status": rag}


# ── PM Chatbot ────────────────────────────────────────────────────────────────

@app.post("/ask")
async def ask_question(request: Request):
    from ai_processor.claude_client import answer_pm_question
    from storage.database import get_todays_updates

    body       = await request.json()
    question   = body.get("question", "").strip()
    project_id = body.get("project_id", settings.default_project_id)

    if not question:
        return {"answer": "Please ask a question."}

    updates = get_todays_updates(project_id)
    answer  = answer_pm_question(project_id, question, updates)
    return {"answer": answer}


# ── Fetch all updates for dashboard ──────────────────────────────────────────

@app.get("/updates/{project_id}")
async def get_updates(project_id: str):
    from storage.database import get_supabase
    sb = get_supabase()
    result = (
        sb.table("processed_updates")
        .select("*, site_updates(source, sender, received_at, raw_content)")
        .eq("project_id", project_id)
        .order("processed_at", desc=True)
        .limit(50)
        .execute()
    )
    return {"updates": result.data}


# ── Fetch reports for dashboard ───────────────────────────────────────────────

@app.get("/reports/{project_id}")
async def get_reports(project_id: str):
    from storage.database import get_supabase
    sb = get_supabase()
    result = (
        sb.table("daily_reports")
        .select("*")
        .eq("project_id", project_id)
        .order("report_date", desc=True)
        .limit(10)
        .execute()
    )
    return {"reports": result.data}


# ── Fetch stats for dashboard ─────────────────────────────────────────────────

@app.get("/stats/{project_id}")
async def get_stats(project_id: str):
    from storage.database import get_supabase
    from datetime import datetime
    sb    = get_supabase()
    today = datetime.utcnow().date().isoformat()

    all_updates = sb.table("processed_updates").select("severity, delay_risk").eq("project_id", project_id).gte("processed_at", today).execute().data
    total    = len(all_updates)
    critical = sum(1 for u in all_updates if u["severity"] == "critical")
    medium   = sum(1 for u in all_updates if u["severity"] == "medium")
    low      = sum(1 for u in all_updates if u["severity"] == "low")

    return {"total": total, "critical": critical, "medium": medium, "low": low}


# ── Debug endpoint — shows what env vars are loaded ──────────────────────────
@app.get("/debug")
def debug():
    return {
        "anthropic_key_set": bool(settings.anthropic_api_key),
        "supabase_url_set":  bool(settings.supabase_url),
        "supabase_key_set":  bool(settings.supabase_anon_key),
        "project_id":        settings.default_project_id,
        "supabase_url":      settings.supabase_url[:30] + "..." if settings.supabase_url else "NOT SET",
    }
