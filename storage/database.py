from supabase import create_client, Client
from config import settings

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _client


def insert_update(project_id: str, source: str, raw_content: str, sender: str) -> dict:
    sb = get_supabase()
    result = sb.table("site_updates").insert({
        "project_id": project_id,
        "source": source,
        "raw_content": raw_content,
        "sender": sender,
    }).execute()
    return result.data[0]


def insert_processed(update_id: str, project_id: str, summary: str,
                     issues: list, severity: str, delay_risk: bool,
                     action_required) -> dict:
    sb = get_supabase()
    result = sb.table("processed_updates").insert({
        "update_id": update_id,
        "project_id": project_id,
        "summary": summary,
        "issues": issues,
        "severity": severity,
        "delay_risk": delay_risk,
        "action_required": action_required,
    }).execute()
    return result.data[0]


def get_todays_updates(project_id: str) -> list[dict]:
    """
    Returns today's updates. If none exist today (e.g. demo/seed data),
    falls back to the most recent 21 updates so the demo always works.
    """
    sb = get_supabase()
    from datetime import date
    today = date.today().isoformat()

    result = (
        sb.table("processed_updates")
        .select("*")
        .eq("project_id", project_id)
        .gte("processed_at", today)
        .execute()
    )

    if result.data:
        return result.data

    # Fallback: return latest 21 updates (for demo with seeded data)
    fallback = (
        sb.table("processed_updates")
        .select("*")
        .eq("project_id", project_id)
        .order("processed_at", desc=True)
        .limit(21)
        .execute()
    )
    return fallback.data


def get_all_updates(project_id: str, limit: int = 50) -> list[dict]:
    sb = get_supabase()
    result = (
        sb.table("processed_updates")
        .select("*, site_updates(source, sender, received_at, raw_content)")
        .eq("project_id", project_id)
        .order("processed_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


def insert_daily_report(project_id: str, report_date: str,
                        content: str, rag_status: str) -> dict:
    sb = get_supabase()
    result = sb.table("daily_reports").insert({
        "project_id": project_id,
        "report_date": report_date,
        "content": content,
        "rag_status": rag_status,
    }).execute()
    return result.data[0]
