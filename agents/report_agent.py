"""
agents/report_agent.py
-----------------------
Responsibility: Generate the daily AI report from today's site updates.
Runs on a schedule (5PM daily) via scheduler.py.
Calls storage_agent tools to read data, then calls Claude to write the report.
"""

import json
import anthropic
from agentspan.agents import Agent, tool
from observability.decorators import trace_agent, trace_llm_call
from observability.metrics import record_report_generated
from config import settings
from ai_processor.prompts import DAILY_REPORT_PROMPT
from storage.database import get_todays_updates, insert_daily_report

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


@trace_llm_call
def _call_claude(prompt: str):
    return _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )


@tool
@trace_agent("report_agent.generate")
def generate_daily_report(project_id: str, report_date: str) -> dict:
    """
    Fetch today's processed updates for a project, generate an AI daily report,
    save it to Supabase, and return the report content and RAG status.
    """
    updates = get_todays_updates(project_id)

    if not updates:
        return {
            "report": "No updates received today.",
            "rag_status": "Green",
            "update_count": 0,
        }

    prompt = DAILY_REPORT_PROMPT.format(
        project_id=project_id,
        date=report_date,
        update_count=len(updates),
        updates_json=json.dumps(updates, indent=2),
    )

    response = _call_claude(prompt)
    report_content = response.content[0].text.strip()

    # Derive RAG status from report text
    rag_status = "Green"
    if "Red" in report_content or "🔴" in report_content:
        rag_status = "Red"
    elif "Amber" in report_content or "🟡" in report_content:
        rag_status = "Amber"

    # Persist to Supabase
    insert_daily_report(project_id, report_date, report_content, rag_status)
    record_report_generated(project_id, len(updates))

    return {
        "report": report_content,
        "rag_status": rag_status,
        "update_count": len(updates),
    }


report_agent = Agent(
    name="report_agent",
    model="anthropic/claude-sonnet-4-6",
    tools=[generate_daily_report],
    instructions="""
You are the report agent for a construction site management system.
Your job is to call generate_daily_report with the project_id and today's date.
Return the full result exactly as the tool returns it. Do not summarise or modify.
""",
)
