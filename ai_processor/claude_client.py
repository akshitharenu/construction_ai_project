import json
import time
import os

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

MODEL = "claude-3-5-sonnet-20241022"  # stable API model string


def _get_client():
    try:
        import anthropic
        from config import settings
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set in .env")
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except ImportError:
<<<<<<< HEAD
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

MODEL = "claude-3-5-sonnet-20241022"


def _call_with_retry(fn, max_retries=3):
    """Call function with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt)
            print(f"[RETRY] Attempt {attempt + 1} failed: {e}. Waiting {wait}s...")
            time.sleep(wait)
=======
        raise RuntimeError("Run: pip install anthropic")
>>>>>>> 2f50d5b9865ed701a707849d27cf0efeccab3fb4


def extract_update(content: str, project_id: str, source: str, sender: str = "unknown") -> dict:
    if DEMO_MODE:
        print(f"[DEMO] extract_update called (not using Claude)")
        return {
            "summary": f"Update received from {sender} via {source}",
            "issues": ["Foundation work required"],
            "severity": "medium",
            "delay_risk": False,
            "action_required": "Review foundation work"
        }
    
    from ai_processor.prompts import EXTRACT_UPDATE_PROMPT
<<<<<<< HEAD
    client = _get_client()
    prompt = EXTRACT_UPDATE_PROMPT.format(
        content=content, project_id=project_id, source=source, sender=sender
    )
    
    def call():
=======
    try:
        client = _get_client()
        prompt = EXTRACT_UPDATE_PROMPT.format(
            content=content, project_id=project_id, source=source, sender=sender
        )
>>>>>>> 2f50d5b9865ed701a707849d27cf0efeccab3fb4
        response = client.messages.create(
            model=MODEL, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
<<<<<<< HEAD
    
    return _call_with_retry(call)


def generate_daily_report(project_id: str, date: str, updates: list) -> str:
    if DEMO_MODE:
        print(f"[DEMO] generate_daily_report called (not using Claude)")
        return f"""
# Construction AI Report — {date}
**Project:** {project_id}
**Updates:** {len(updates)}

## Summary
Demo report generated. In production, this would be AI-generated from {len(updates)} site updates.

## Key Issues
- Foundation work in progress
- Safety compliance needed
- Material delivery delayed

**Status:** 🟡 Amber (Minor issues)
"""
    
    from ai_processor.prompts import DAILY_REPORT_PROMPT
    client = _get_client()
    prompt = DAILY_REPORT_PROMPT.format(
        project_id=project_id, date=date,
        update_count=len(updates),
        updates_json=json.dumps(updates, indent=2),
    )
    
    def call():
=======
    except Exception as e:
        print(f"[CLAUDE] extract_update failed: {e}")
        # Return a safe fallback so the update still gets saved
        return {
            "summary": content[:200],
            "issues": [],
            "severity": "low",
            "delay_risk": False,
            "action_required": None,
        }


def generate_daily_report(project_id: str, report_date: str, updates: list) -> str:
    from ai_processor.prompts import DAILY_REPORT_PROMPT
    try:
        client = _get_client()
        prompt = DAILY_REPORT_PROMPT.format(
            project_id=project_id, date=report_date,
            update_count=len(updates),
            updates_json=json.dumps(updates, indent=2),
        )
>>>>>>> 2f50d5b9865ed701a707849d27cf0efeccab3fb4
        response = client.messages.create(
            model=MODEL, max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
<<<<<<< HEAD
    
    return _call_with_retry(call)
=======
    except Exception as e:
        print(f"[CLAUDE] generate_daily_report failed: {e}")
        raise RuntimeError(f"Claude API error: {e}")
>>>>>>> 2f50d5b9865ed701a707849d27cf0efeccab3fb4


def answer_pm_question(project_id: str, question: str, context: list) -> str:
    if DEMO_MODE:
        print(f"[DEMO] answer_pm_question called (not using Claude)")
        return f"Demo response to: '{question}'. In production, Claude would answer based on {len(context)} context items."
    
    from ai_processor.prompts import PM_CHATBOT_PROMPT
<<<<<<< HEAD
    client = _get_client()
    prompt = PM_CHATBOT_PROMPT.format(
        project_id=project_id, question=question,
        context=json.dumps(context, indent=2),
    )
    
    def call():
=======
    try:
        client = _get_client()
        prompt = PM_CHATBOT_PROMPT.format(
            project_id=project_id, question=question,
            context=json.dumps(context, indent=2),
        )
>>>>>>> 2f50d5b9865ed701a707849d27cf0efeccab3fb4
        response = client.messages.create(
            model=MODEL, max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
<<<<<<< HEAD
    
    return _call_with_retry(call)
=======
    except Exception as e:
        print(f"[CLAUDE] answer_pm_question failed: {e}")
        raise RuntimeError(f"Claude API error: {e}")
>>>>>>> 2f50d5b9865ed701a707849d27cf0efeccab3fb4
