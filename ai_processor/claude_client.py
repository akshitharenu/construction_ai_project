import json

def _get_client():
    try:
        import anthropic
        from config import settings
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

MODEL = "claude-sonnet-4-6"


def extract_update(content: str, project_id: str, source: str, sender: str = "unknown") -> dict:
    from ai_processor.prompts import EXTRACT_UPDATE_PROMPT
    client = _get_client()
    prompt = EXTRACT_UPDATE_PROMPT.format(
        content=content, project_id=project_id, source=source, sender=sender
    )
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


def generate_daily_report(project_id: str, date: str, updates: list) -> str:
    from ai_processor.prompts import DAILY_REPORT_PROMPT
    client = _get_client()
    prompt = DAILY_REPORT_PROMPT.format(
        project_id=project_id, date=date,
        update_count=len(updates),
        updates_json=json.dumps(updates, indent=2),
    )
    response = client.messages.create(
        model=MODEL, max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def answer_pm_question(project_id: str, question: str, context: list) -> str:
    from ai_processor.prompts import PM_CHATBOT_PROMPT
    client = _get_client()
    prompt = PM_CHATBOT_PROMPT.format(
        project_id=project_id, question=question,
        context=json.dumps(context, indent=2),
    )
    response = client.messages.create(
        model=MODEL, max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
