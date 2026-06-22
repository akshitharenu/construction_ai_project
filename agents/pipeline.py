"""
agents/pipeline.py
-------------------
Wires individual agents into Agentspan pipelines using the >> operator
and Strategy patterns from agentspan.agents.

Three pipelines:

  update_pipeline   — ingestion >> extraction >> storage (sequential)
                      then alert_agent in parallel after storage
                      used for every incoming site update

  report_pipeline   — report_agent standalone, called by scheduler

  chatbot_pipeline  — chatbot_agent standalone, called by /ask endpoint

Why sequential for the update pipeline:
  Each step depends on the previous output. Ingestion must normalise before
  extraction can parse, and extraction must complete before storage can persist.
  Alert runs after storage independently — it only needs the severity from extraction.
"""

from agentspan.agents import Agent, Strategy
from .ingestion_agent import ingestion_agent
from .extraction_agent import extraction_agent
from .storage_agent import storage_agent
from .alert_agent import alert_agent
from .report_agent import report_agent
from .chatbot_agent import chatbot_agent


# ── Core update pipeline: ingestion → extraction → storage (sequential) ──────
#
#  Agentspan's >> compiles this into a durable Conductor workflow.
#  If the process dies mid-step, Agentspan resumes from the last completed step.
#
_ingest_extract_store = ingestion_agent >> extraction_agent >> storage_agent

# ── Alert runs in parallel with the storage result ────────────────────────────
#
#  After storage completes, alert_agent gets the extraction result.
#  Using PARALLEL so the alert fires without blocking the response to the caller.
#
update_pipeline = Agent(
    name="construction_update_pipeline",
    model="anthropic/claude-sonnet-4-6",
    agents=[_ingest_extract_store, alert_agent],
    strategy=Strategy.PARALLEL,
    instructions="""
You coordinate the full site update pipeline.
Stage 1: run ingestion → extraction → storage in sequence.
Stage 2: run the alert agent in parallel with the result.
Return the combined result once both complete.
""",
)

# ── Daily report pipeline (runs standalone at 5PM) ────────────────────────────
report_pipeline = report_agent

# ── PM chatbot pipeline (stateless, per-request) ─────────────────────────────
chatbot_pipeline = chatbot_agent
