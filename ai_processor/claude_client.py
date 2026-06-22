import json

MODEL = "claude-3-5-sonnet-20241022"  # stable API model string


def _get_client():
    try:
        import anthropic
        from config import settings
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set in .env")
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except ImportError:
        raise RuntimeError("Run: pip install anthropic")


def extract_update(content: str, project_id: str, source: str, sender: str = "unknown") -> dict:
    from ai_processor.prompts import EXTRACT_UPDATE_PROMPT
    try:
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
        response = client.messages.create(
            model=MODEL, max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[CLAUDE] generate_daily_report failed: {e}")
        raise RuntimeError(f"Claude API error: {e}")


def answer_pm_question(project_id: str, question: str, context: list) -> str:
    from ai_processor.prompts import PM_CHATBOT_PROMPT
    try:
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
    except Exception as e:
        print(f"[CLAUDE] answer_pm_question failed: {e}")
        raise RuntimeError(f"Claude API error: {e}")
