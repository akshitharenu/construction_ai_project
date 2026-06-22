"""
agents/ingestion_agent.py
--------------------------
Responsibility: Accept raw input from any source (WhatsApp, email, form),
normalise it into a single structured SiteUpdatePayload, and return it.

Agentspan strategy: single agent with one @tool.
OTEL: span per run via @trace_agent decorator.
"""

from agentspan.agents import Agent, tool
from observability.decorators import trace_agent
from observability.metrics import record_update_received


class SiteUpdatePayload:
    def __init__(self, content: str, sender: str, source: str, project_id: str):
        self.content = content
        self.sender = sender
        self.source = source      # "whatsapp" | "email" | "form"
        self.project_id = project_id

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "sender": self.sender,
            "source": self.source,
            "project_id": self.project_id,
        }


@tool
@trace_agent("ingestion_agent.normalise")
def normalise_update(content: str, sender: str, source: str, project_id: str) -> dict:
    """
    Normalise an incoming site update from any source into a standard payload.
    Validates that content is non-empty and source is a known type.
    Returns a dict with keys: content, sender, source, project_id.
    """
    # Validate source
    valid_sources = {"whatsapp", "email", "form"}
    source = source.lower().strip()
    if source not in valid_sources:
        source = "form"  # default fallback

    # Strip and validate content
    content = content.strip()
    if not content:
        raise ValueError("Update content cannot be empty")

    record_update_received(source, project_id)

    return SiteUpdatePayload(
        content=content,
        sender=sender or "unknown",
        source=source,
        project_id=project_id,
    ).to_dict()


ingestion_agent = Agent(
    name="ingestion_agent",
    model="anthropic/claude-sonnet-4-6",
    tools=[normalise_update],
    instructions="""
You are the ingestion agent for a construction site management system.
Your only job is to call the normalise_update tool with the inputs you receive.
Do not add commentary. Do not interpret the content. Just normalise and return.
""",
)
