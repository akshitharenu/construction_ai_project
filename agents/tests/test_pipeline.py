"""
agents/tests/test_pipeline.py
------------------------------
Agentspan mock_run tests — no LLM, no server, runs in milliseconds.
Run: pytest agents/tests/
"""

from agentspan.agents.testing import mock_run, MockEvent, expect
from agents.ingestion_agent import ingestion_agent
from agents.alert_agent import alert_agent


def test_ingestion_normalises_whatsapp():
    result = mock_run(
        ingestion_agent,
        '{"content": "Scaffolding failed", "sender": "+971501234567", "source": "whatsapp", "project_id": "PROJ-001"}',
        events=[
            MockEvent.tool_call("normalise_update", {
                "content": "Scaffolding failed",
                "sender": "+971501234567",
                "source": "whatsapp",
                "project_id": "PROJ-001",
            }),
            MockEvent.tool_result("normalise_update", {
                "content": "Scaffolding failed",
                "sender": "+971501234567",
                "source": "whatsapp",
                "project_id": "PROJ-001",
            }),
            MockEvent.done("Normalised"),
        ]
    )
    expect(result).completed().used_tool("normalise_update")


def test_alert_fires_on_critical():
    result = mock_run(
        alert_agent,
        '{"project_id": "PROJ-001", "summary": "Crane failure", "severity": "critical", "action_required": "Stop work"}',
        events=[
            MockEvent.tool_call("send_pm_alert", {
                "project_id": "PROJ-001",
                "summary": "Crane failure",
                "severity": "critical",
                "action_required": "Stop work",
            }),
            MockEvent.tool_result("send_pm_alert", {"alerted": True, "reason": "Alert sent"}),
            MockEvent.done("Alert sent"),
        ]
    )
    expect(result).completed().used_tool("send_pm_alert")


def test_alert_skips_low():
    result = mock_run(
        alert_agent,
        '{"project_id": "PROJ-001", "summary": "Normal progress", "severity": "low", "action_required": null}',
        events=[
            MockEvent.tool_call("send_pm_alert", {
                "project_id": "PROJ-001",
                "summary": "Normal progress",
                "severity": "low",
                "action_required": None,
            }),
            MockEvent.tool_result("send_pm_alert", {"alerted": False, "reason": "low severity"}),
            MockEvent.done("No alert"),
        ]
    )
    expect(result).completed().used_tool("send_pm_alert")
