"""
scheduler.py
-------------
Runs the report_agent daily at 5PM Dubai time via APScheduler.
Uses the Agentspan runtime — the report job is a durable workflow,
so if this process crashes mid-report, Agentspan resumes it automatically.
"""

import json
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
from agentspan.agents import AgentRuntime

from observability import init_tracer
from config import settings

scheduler = BlockingScheduler(timezone="Asia/Dubai")
_runtime  = AgentRuntime()


def run_daily_report(project_id: str = None):
    from agents.pipeline import report_pipeline

    project_id = project_id or settings.default_project_id
    today = date.today().isoformat()
    print(f"[SCHEDULER] Running daily report for {project_id} on {today}")

    result = _runtime.run(
        report_pipeline,
        json.dumps({"project_id": project_id, "report_date": today}),
    )
    print(f"[SCHEDULER] Report complete: {result}")


@scheduler.scheduled_job("cron", hour=17, minute=0)
def scheduled_job():
    run_daily_report()


if __name__ == "__main__":
    init_tracer("construction-ai-scheduler")
    print("Scheduler running — daily report at 17:00 Dubai time. Ctrl+C to stop.")
    scheduler.start()
