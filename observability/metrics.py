"""
observability/metrics.py
------------------------
Application-level metrics emitted as OTEL span events.
Keeps metrics co-located with traces so a single backend (Jaeger / Tempo)
shows both without a separate Prometheus scrape.
"""

from opentelemetry import trace


def _current_span():
    return trace.get_current_span()


def record_update_received(source: str, project_id: str) -> None:
    """Called each time a site update arrives."""
    _current_span().add_event(
        "update.received",
        attributes={"source": source, "project_id": project_id},
    )


def record_severity(severity: str, project_id: str) -> None:
    """Called after extraction — records what severity was assigned."""
    _current_span().add_event(
        "update.severity_classified",
        attributes={"severity": severity, "project_id": project_id},
    )


def record_agent_duration(agent_name: str, duration_ms: int) -> None:
    """Called at the end of any agent run."""
    _current_span().add_event(
        "agent.completed",
        attributes={"agent": agent_name, "duration_ms": duration_ms},
    )


def record_alert_fired(project_id: str, severity: str) -> None:
    """Called when an alert is sent to the PM."""
    _current_span().add_event(
        "alert.fired",
        attributes={"project_id": project_id, "severity": severity},
    )


def record_report_generated(project_id: str, update_count: int) -> None:
    """Called when a daily report is generated."""
    _current_span().add_event(
        "report.generated",
        attributes={"project_id": project_id, "update_count": update_count},
    )
