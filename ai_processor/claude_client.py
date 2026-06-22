import json
import anthropic
from config import settings
from ai_processor.prompts import EXTRACT_UPDATE_PROMPT, DAILY_REPORT_PROMPT, PM_CHATBOT_PROMPT

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-sonnet-4-6"


def extract_update(content: str, project_id: str, source: str, sender: str = "unknown") -> dict:
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
    return json.loads(raw)


def generate_daily_report(project_id: str, date: str, updates: list[dict]) -> str:
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


def answer_pm_question(project_id: str, question: str, context: list[dict]) -> str:
    prompt = PM_CHATBOT_PROMPT.format(
        project_id=project_id, question=question,
        context=json.dumps(context, indent=2),
    )
    response = client.messages.create(
        model=MODEL, max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
