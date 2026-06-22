try:
    from .tracer import get_tracer, init_tracer
    from .decorators import trace_agent, trace_llm_call
    from .metrics import record_update_received, record_severity, record_agent_duration
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

    def init_tracer(service_name="construction-ai"):
        print(f"[OTEL] OpenTelemetry not installed — skipping tracing")

    def get_tracer():
        return None

    def trace_agent(name):
        def decorator(fn):
            return fn
        return decorator

    def trace_llm_call(fn):
        return fn

    def record_update_received(*a, **k): pass
    def record_severity(*a, **k): pass
    def record_agent_duration(*a, **k): pass

__all__ = [
    "get_tracer", "init_tracer",
    "trace_agent", "trace_llm_call",
    "record_update_received", "record_severity", "record_agent_duration",
]
