"""
observability/tracer.py
-----------------------
Initialises the OpenTelemetry SDK once at startup.
Every agent, tool call, and LLM call gets a span automatically
via the @trace_agent / @trace_llm_call decorators.

Export target:
  - Local dev  → OTEL collector on localhost:4317 (docker-compose)
  - Production → set OTEL_EXPORTER_OTLP_ENDPOINT in .env
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

_tracer: trace.Tracer | None = None


def init_tracer(service_name: str = "construction-ai") -> None:
    global _tracer

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

    if endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        print(f"[OTEL] Exporting spans to {endpoint}")
    else:
        exporter = ConsoleSpanExporter()
        print("[OTEL] No OTEL_EXPORTER_OTLP_ENDPOINT set — printing spans to console")

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name)
    print(f"[OTEL] Tracer initialised for '{service_name}'")


def get_tracer() -> trace.Tracer:
    global _tracer
    if _tracer is None:
        init_tracer()
    return _tracer
