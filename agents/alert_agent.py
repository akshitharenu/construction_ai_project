"""
agents/alert_agent.py
----------------------
Responsibility: Send WhatsApp alerts via Twilio when severity = critical.
This agent has no knowledge of Supabase, Claude, or the report format.
It receives a severity decision and acts on it — nothing more.

Human-in-the-loop ready: mark send_pm_alert with approval_required=True
in production to require a human to confirm before firing.
"""

from agentspan.agents import Agent, tool
from observability.decorators import trace_agent
from observability.metrics import record_alert_fired
from config import settings


@tool
@trace_agent("alert_agent.notify")
def send_pm_alert(project_id: str, summary: str, severity: str, action_required: str | None) -> dict:
    """
    Evaluate severity and send a WhatsApp alert to the PM if critical.
    Returns: { "alerted": bool, "reason": str }
    """
    if severity != "critical":
        return {"alerted": False, "reason": f"Severity is '{severity}' — no alert needed"}

    message = f"CRITICAL — {project_id}\n\n{summary}"
    if action_required:
        message += f"\n\nAction needed: {action_required}"

    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        client.messages.create(
            from_=settings.twilio_whatsapp_from,
            to=f"whatsapp:{settings.pm_whatsapp_number}",
            body=message,
        )
        record_alert_fired(project_id, severity)
        return {"alerted": True, "reason": "Critical alert sent to PM via WhatsApp"}
    except Exception as exc:
        # Don't let alert failure break the whole pipeline
        return {"alerted": False, "reason": f"Alert failed: {str(exc)}"}


alert_agent = Agent(
    name="alert_agent",
    model="anthropic/claude-sonnet-4-6",
    tools=[send_pm_alert],
    instructions="""
You are the alert agent for a construction site management system.
Your only job is to call send_pm_alert with the severity and summary you receive.
You do not decide whether to alert — the tool logic makes that decision based on severity.
Call the tool and return its result.
""",
)
