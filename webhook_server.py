import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="ConstructAI — Site Intelligence")
TEMPLATES = Path(__file__).parent / "templates"


@app.on_event("startup")
def on_startup():
    try:
        from observability import init_tracer
        init_tracer("construction-ai")
    except Exception as e:
        print(f"[STARTUP] OTEL skipped: {e}")
    print("[STARTUP] ConstructAI ready at http://localhost:8000")


def get_settings():
    from config import settings
    return settings

def get_db():
    from storage.database import get_supabase
    return get_supabase()


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    try:
        html = (TEMPLATES / "dashboard.html").read_text(encoding="utf-8")
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><pre>{e}</pre>", status_code=500)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ConstructAI", "agents": 6}


@app.get("/debug")
def debug():
    try:
        s = get_settings()
        return {
            "anthropic_key_set": bool(s.anthropic_api_key),
            "supabase_url_set":  bool(s.supabase_url),
            "supabase_key_set":  bool(s.supabase_anon_key),
            "project_id":        s.default_project_id,
        }
    except Exception as e:
        return {"error": str(e)}


# ── Stats — uses ALL data for demo ────────────────────────────────────────────

@app.get("/stats/{project_id}")
async def get_stats(project_id: str):
    try:
        sb   = get_db()
        rows = sb.table("processed_updates").select("severity").eq("project_id", project_id).execute().data
        total    = len(rows)
        critical = sum(1 for r in rows if r["severity"] == "critical")
        medium   = sum(1 for r in rows if r["severity"] == "medium")
        low      = sum(1 for r in rows if r["severity"] == "low")
        return {"total": total, "critical": critical, "medium": medium, "low": low}
    except Exception as e:
        print(f"[ERROR] /stats: {e}")
        return JSONResponse({"total": 0, "critical": 0, "medium": 0, "low": 0, "error": str(e)})


# ── Updates ───────────────────────────────────────────────────────────────────

@app.get("/updates/{project_id}")
async def get_updates(project_id: str):
    try:
        sb = get_db()
        result = (
            sb.table("processed_updates")
            .select("*, site_updates(source, sender, received_at, raw_content)")
            .eq("project_id", project_id)
            .order("processed_at", desc=True)
            .limit(50)
            .execute()
        )
        return {"updates": result.data}
    except Exception as e:
        print(f"[ERROR] /updates: {e}")
        return JSONResponse({"updates": [], "error": str(e)})


# ── Reports ───────────────────────────────────────────────────────────────────

@app.get("/reports/{project_id}")
async def get_reports(project_id: str):
    try:
        sb = get_db()
        result = (
            sb.table("daily_reports")
            .select("*")
            .eq("project_id", project_id)
            .order("report_date", desc=True)
            .limit(10)
            .execute()
        )
        return {"reports": result.data}
    except Exception as e:
        print(f"[ERROR] /reports: {e}")
        return JSONResponse({"reports": [], "error": str(e)})


# ── Generate report ───────────────────────────────────────────────────────────

@app.post("/report/generate")
async def generate_report(request: Request):
    try:
        from ai_processor.claude_client import generate_daily_report
        from storage.database import get_todays_updates, insert_daily_report

        s          = get_settings()
        body       = await request.json()
        project_id = body.get("project_id", s.default_project_id)
        today      = date.today().isoformat()

        updates = get_todays_updates(project_id)
        print(f"[REPORT] Found {len(updates)} updates for {project_id}")

        if not updates:
            return {"report": "No updates found for this project.", "rag_status": "Green"}

        report = generate_daily_report(project_id, today, updates)
        rag    = "Red" if "Red" in report else "Amber" if "Amber" in report else "Green"
        insert_daily_report(project_id, today, report, rag)
        return {"report": report, "rag_status": rag}

    except Exception as e:
        print(f"[ERROR] /report/generate: {e}")
        import traceback; traceback.print_exc()
        return JSONResponse({"status": "error", "reason": str(e)}, status_code=500)


# ── Submit update ─────────────────────────────────────────────────────────────

@app.post("/update")
async def submit_update(request: Request):
    try:
        from ai_processor.claude_client import extract_update
        from storage.database import insert_update, insert_processed

        s          = get_settings()
        body       = await request.json()
        content    = body.get("content", "").strip()
        sender     = body.get("sender", "api")
        source     = body.get("source", "form")
        project_id = body.get("project_id", s.default_project_id)

        if not content:
            return {"status": "error", "reason": "content is required"}

        raw    = insert_update(project_id, source, content, sender)
        result = extract_update(content, project_id, source, sender)
        insert_processed(
            update_id=raw["id"], project_id=project_id,
            summary=result["summary"], issues=result.get("issues", []),
            severity=result["severity"], delay_risk=result.get("delay_risk", False),
            action_required=result.get("action_required"),
        )
        if result["severity"] == "critical":
            try:
                from outputs.alerts import send_critical_alert
                send_critical_alert(project_id, result["summary"], result.get("action_required"))
            except Exception as ae:
                print(f"[ALERT] skipped: {ae}")

        return {"status": "ok", "extracted": result}

    except Exception as e:
        print(f"[ERROR] /update: {e}")
        import traceback; traceback.print_exc()
        return JSONResponse({"status": "error", "reason": str(e)}, status_code=500)


# ── WhatsApp webhook ──────────────────────────────────────────────────────────

@app.post("/webhook/whatsapp")
async def receive_whatsapp(request: Request):
    try:
        from ai_processor.claude_client import extract_update
        from storage.database import insert_update, insert_processed
        s       = get_settings()
        data    = await request.form()
        content = data.get("Body", "").strip()
        sender  = data.get("From", "unknown")
        if not content:
            return {"status": "ignored"}
        raw    = insert_update(s.default_project_id, "whatsapp", content, sender)
        result = extract_update(content, s.default_project_id, "whatsapp", sender)
        insert_processed(update_id=raw["id"], project_id=s.default_project_id,
                         summary=result["summary"], issues=result.get("issues", []),
                         severity=result["severity"], delay_risk=result.get("delay_risk", False),
                         action_required=result.get("action_required"))
        return {"status": "ok"}
    except Exception as e:
        print(f"[ERROR] /webhook/whatsapp: {e}")
        return JSONResponse({"status": "error"}, status_code=500)


# ── PM chatbot ────────────────────────────────────────────────────────────────

@app.post("/ask")
async def ask_question(request: Request):
    try:
        from ai_processor.claude_client import answer_pm_question
        from storage.database import get_todays_updates

        s          = get_settings()
        body       = await request.json()
        question   = body.get("question", "").strip()
        project_id = body.get("project_id", s.default_project_id)

        if not question:
            return {"answer": "Please ask a question."}

        updates = get_todays_updates(project_id)
        print(f"[CHAT] {len(updates)} updates as context for: {question}")
        answer  = answer_pm_question(project_id, question, updates)
        return {"answer": answer}

    except Exception as e:
        print(f"[ERROR] /ask: {e}")
        import traceback; traceback.print_exc()
        return JSONResponse({"answer": f"Error: {str(e)}"}, status_code=500)
