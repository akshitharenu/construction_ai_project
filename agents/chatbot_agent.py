"""
agents/chatbot_agent.py
------------------------
Responsibility: Answer PM natural-language questions about today's site data.
Stateless per request — fetches fresh context from Supabase each time.
"""

import json
import anthropic
from agentspan.agents import Agent, tool
from observability.decorators import trace_agent, trace_llm_call
from config import settings
from ai_processor.prompts import PM_CHATBOT_PROMPT
from storage.database import get_todays_updates

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


@trace_llm_call
def _call_claude(prompt: str):
    return _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )


@tool
@trace_agent("chatbot_agent.answer")
def answer_pm_question(project_id: str, question: str) -> dict:
    """
    Answer a PM's natural-language question about today's construction site activity.
    Fetches today's updates from Supabase and uses them as context for Claude.
    Returns: { "answer": str, "context_updates": int }
    """
    updates = get_todays_updates(project_id)

    if not updates:
        return {
            "answer": "No site updates have been received today yet. Submit a site update first.",
            "context_updates": 0,
        }

    prompt = PM_CHATBOT_PROMPT.format(
        project_id=project_id,
        question=question,
        context=json.dumps(updates, indent=2),
    )

    response = _call_claude(prompt)
    return {
        "answer": response.content[0].text.strip(),
        "context_updates": len(updates),
    }


chatbot_agent = Agent(
    name="chatbot_agent",
    model="anthropic/claude-sonnet-4-6",
    tools=[answer_pm_question],
    instructions="""
You are the PM assistant agent for a construction site management system.
When given a project_id and question, call answer_pm_question and return the result.
Do not answer from your own knowledge — always use the tool to get site-specific context.
""",
)
