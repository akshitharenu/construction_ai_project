# ConstructAI — Multi-Agent Site Intelligence

> A production-grade multi-agent construction automation system.
> Built with **Agentspan** for durable execution, **OpenTelemetry** for full observability,
> and **Claude** for AI reasoning.

![Python](https://img.shields.io/badge/Python-3.11+-orange?style=flat-square)
![Agentspan](https://img.shields.io/badge/Agentspan-durable_agents-black?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4.6-blueviolet?style=flat-square)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-traced-blue?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?style=flat-square)

---

## Architecture

Six specialist agents, each owning exactly one responsibility,
coordinated by Agentspan's durable execution engine.

```
WhatsApp / Email / Form
        │
        ▼
  ingestion_agent      normalise source → standard payload
        │
        ▼
  extraction_agent     call Claude → extract issues, severity, action
        │
        ▼
  storage_agent        write to Supabase (raw + processed)
        │
   ┌────┘
   ▼
  alert_agent          send WhatsApp if severity = critical   [parallel]
        │
        ▼
  report_agent         generate daily AI report at 5PM        [scheduled]
        │
  chatbot_agent        answer PM questions on demand          [per-request]
```

If the process crashes mid-pipeline, **Agentspan resumes from the last completed step**.
Every agent emits OpenTelemetry spans — visible in Jaeger at `http://localhost:16686`.

---

## Agent pipeline (Agentspan)

```python
# Sequential: each output feeds the next
_ingest_extract_store = ingestion_agent >> extraction_agent >> storage_agent

# Parallel: alert fires alongside storage result
update_pipeline = Agent(
    name="construction_update_pipeline",
    agents=[_ingest_extract_store, alert_agent],
    strategy=Strategy.PARALLEL,
)
```

---

## Observability stack

| Layer | Tool | What it shows |
|-------|------|---------------|
| Traces | OpenTelemetry + Jaeger | Every agent span, LLM call, DB write |
| Agent runs | Agentspan UI (`:6767`) | Full agent decision chain, step-by-step |
| Metrics | OTEL span events | Severity distribution, alert rate, token usage |
| Tests | Agentspan `mock_run` | Deterministic agent tests, no LLM needed |

---

## Project structure

```
construction_ai_project/
├── agents/
│   ├── ingestion_agent.py     # Normalise incoming updates
│   ├── extraction_agent.py    # Claude AI extraction
│   ├── storage_agent.py       # All Supabase operations
│   ├── alert_agent.py         # Twilio WhatsApp alerts
│   ├── report_agent.py        # Daily report generation
│   ├── chatbot_agent.py       # PM question answering
│   ├── pipeline.py            # Agentspan pipeline composition
│   └── tests/
│       └── test_pipeline.py   # mock_run tests (no LLM needed)
├── observability/
│   ├── tracer.py              # OTEL SDK init
│   ├── decorators.py          # @trace_agent, @trace_llm_call
│   └── metrics.py             # Span event helpers
├── ai_processor/
│   ├── prompts.py             # Prompt templates
│   └── claude_client.py       # Direct Claude calls (used by agents)
├── storage/
│   ├── database.py            # Supabase client
│   └── schema.sql             # Run in Supabase SQL editor
├── outputs/
│   ├── alerts.py              # Twilio helpers
│   └── report.py              # Email / file helpers
├── templates/
│   └── dashboard.html         # Construction-themed web UI
├── webhook_server.py          # FastAPI — all endpoints
├── scheduler.py               # APScheduler — 5PM daily report
├── config.py                  # Pydantic settings
├── docker-compose.yml         # App + Agentspan + OTEL + Jaeger
├── otel-collector-config.yaml # OTEL collector routing
└── Dockerfile
```

---

## Quick start

### 1. Clone & install

```bash
git clone https://github.com/akshitharenu/construction_ai_project.git
cd construction_ai_project
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up Supabase

Run `storage/schema.sql` in your Supabase SQL editor.

### 3. Configure environment

```bash
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY
```

### 4. Start Agentspan server

```bash
agentspan server start
# UI available at http://localhost:6767
```

### 5. Run with full observability (Docker)

```bash
docker-compose up
# App:          http://localhost:8000
# Agentspan UI: http://localhost:6767
# Jaeger traces: http://localhost:16686
```

### 6. Run locally (no Docker)

```bash
uvicorn webhook_server:app --reload --port 8000
```

---

## Testing (no LLM, no server)

```bash
pytest agents/tests/
```

Agentspan's `mock_run` lets you test exact tool call sequences deterministically.

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Dashboard UI |
| `POST` | `/update` | Submit site update (JSON) |
| `POST` | `/webhook/whatsapp` | Twilio webhook |
| `POST` | `/webhook/email` | SendGrid inbound parse |
| `POST` | `/report/generate` | Generate today's AI report |
| `POST` | `/ask` | PM chatbot |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Agent orchestration | Agentspan (durable execution via Conductor) |
| AI | Anthropic Claude (claude-sonnet-4-6) |
| Observability | OpenTelemetry + Jaeger |
| API | FastAPI + Uvicorn |
| Database | Supabase (PostgreSQL) |
| Scheduler | APScheduler |
| Alerts | Twilio WhatsApp |
| Email | SendGrid |
| Frontend | Vanilla HTML/CSS/JS |

---

Built as a demo project showing AI automation in construction workflows
using production-grade multi-agent patterns.
