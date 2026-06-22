"""
agents/storage_agent.py
------------------------
Responsibility: All Supabase reads and writes.
No other agent touches the database directly.

Tools:
  - save_update      — writes a raw + processed update to Supabase
  - get_todays_data  — reads today's processed updates for a project
  - save_report      — writes a daily report to Supabase
"""

from agentspan.agents import Agent, tool
from observability.decorators import trace_agent
from storage.database import (
    insert_update,
    insert_processed,
    get_todays_updates,
    insert_daily_report,
)


@tool
@trace_agent("storage_agent.save_update")
def save_update(
    project_id: str, source: str, content: str, sender: str,
    summary: str, issues: list, severity: str,
    delay_risk: bool, action_required: str | None,
) -> dict:
    """
    Persist a raw site update and its AI-processed result to Supabase.
    Returns the IDs of both created rows.
    """
    raw = insert_update(project_id, source, content, sender)
    processed = insert_processed(
        update_id=raw["id"],
        project_id=project_id,
        summary=summary,
        issues=issues,
        severity=severity,
        delay_risk=delay_risk,
        action_required=action_required,
    )
    return {"raw_id": raw["id"], "processed_id": processed["id"]}


@tool
@trace_agent("storage_agent.get_todays_data")
def get_todays_data(project_id: str) -> list:
    """
    Fetch all processed updates for a project from today.
    Returns a list of dicts with summary, severity, issues, action_required.
    """
    return get_todays_updates(project_id)


@tool
@trace_agent("storage_agent.save_report")
def save_report(project_id: str, report_date: str, content: str, rag_status: str) -> dict:
    """Save a generated daily report to Supabase."""
    return insert_daily_report(project_id, report_date, content, rag_status)


storage_agent = Agent(
    name="storage_agent",
    model="anthropic/claude-sonnet-4-6",
    tools=[save_update, get_todays_data, save_report],
    instructions="""
You are the storage agent for a construction site management system.
You manage all database interactions with Supabase.
Call the appropriate tool based on the operation requested.
Do not interpret data — just persist or retrieve it exactly as instructed.
""",
)
