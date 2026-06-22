"""
agents/extraction_agent.py
---------------------------
Responsibility: Call Claude to extract structured information from a site update.
Returns: summary, issues list, severity, delay_risk, action_required.

Agentspan strategy: single agent with one @tool.
OTEL: @trace_agent wraps the tool, @trace_llm_call wraps the Claude call.
"""

import json
import anthropic
from agentspan.agents import Agent, tool
from observability.decorators import trace_agent, trace_llm_call
from observability.metrics import record_severity
from config import settings
from ai_processor.prompts import EXTRACT_UPDATE_PROMPT

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


@trace_llm_call
def _call_claude(prompt: str):
    """Raw Claude API call — wrapped separately so token usage is traced."""
    return _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )


@tool
@trace_agent("extraction_agent.extract")
def extract_site_update(content: str, sender: str, source: str, project_id: str) -> dict:
    """
    Send a normalised site update to Claude and extract:
    summary, issues (list), severity (low/medium/critical),
    delay_risk (bool), action_required (str or null).
    """
    prompt = EXTRACT_UPDATE_PROMPT.format(
        content=content,
        project_id=project_id,
        source=source,
        sender=sender,
    )

    response = _call_claude(prompt)
    raw = response.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw.strip())
    record_severity(result.get("severity", "low"), project_id)
    return result


extraction_agent = Agent(
    name="extraction_agent",
    model="anthropic/claude-sonnet-4-6",
    tools=[extract_site_update],
    instructions="""
You are the extraction agent for a construction site management system.
Your only job is to call extract_site_update with the payload you receive.
Return the structured result exactly as the tool returns it. Do not modify it.
""",
)
