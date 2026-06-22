import json
import time
import os

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

def _get_client():
    try:
        import anthropic
        from config import settings
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except ImportError:
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
    client = _get_client()
    prompt = EXTRACT_UPDATE_PROMPT.format(
        content=content, project_id=project_id, source=source, sender=sender
    )
    
    def call():
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
        response = client.messages.create(
            model=MODEL, max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    
    return _call_with_retry(call)


def answer_pm_question(project_id: str, question: str, context: list) -> str:
    if DEMO_MODE:
        print(f"[DEMO] answer_pm_question called (not using Claude)")
        return f"Demo response to: '{question}'. In production, Claude would answer based on {len(context)} context items."
    
    from ai_processor.prompts import PM_CHATBOT_PROMPT
    client = _get_client()
    prompt = PM_CHATBOT_PROMPT.format(
        project_id=project_id, question=question,
        context=json.dumps(context, indent=2),
    )
    
    def call():
        response = client.messages.create(
            model=MODEL, max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    
    return _call_with_retry(call)
