"""
observability/decorators.py
---------------------------
Two decorators used across the entire agent layer:

  @trace_agent    — wraps any agent.run() with a span, records input/output/error
  @trace_llm_call — wraps Claude API calls, records model, token usage, latency
"""

import time
import functools
from opentelemetry import trace
from opentelemetry.trace import StatusCode
from .tracer import get_tracer


def trace_agent(agent_name: str):
    """
    Decorator factory for agent methods.

    Usage:
        @trace_agent("ingestion_agent")
        def run(self, payload): ...

    Records:
        agent.name, agent.input (truncated), agent.output (truncated),
        agent.success, agent.error, agent.duration_ms
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(f"agent.{agent_name}") as span:
                span.set_attribute("agent.name", agent_name)

                # Record input (truncate large payloads)
                if args and len(args) > 1:
                    raw = str(args[1])
                    span.set_attribute("agent.input", raw[:500])

                t0 = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = int((time.perf_counter() - t0) * 1000)
                    span.set_attribute("agent.duration_ms", duration_ms)
                    span.set_attribute("agent.success", True)
                    if result:
                        span.set_attribute("agent.output", str(result)[:500])
                    span.set_status(StatusCode.OK)
                    return result
                except Exception as exc:
                    duration_ms = int((time.perf_counter() - t0) * 1000)
                    span.set_attribute("agent.duration_ms", duration_ms)
                    span.set_attribute("agent.success", False)
                    span.set_attribute("agent.error", str(exc))
                    span.set_status(StatusCode.ERROR, str(exc))
                    raise
        return wrapper
    return decorator


def trace_llm_call(func):
    """
    Decorator for functions that call the Claude (or any LLM) API.

    Records:
        llm.model, llm.prompt_tokens, llm.completion_tokens,
        llm.total_tokens, llm.duration_ms
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracer = get_tracer()
        with tracer.start_as_current_span("llm.claude_call") as span:
            span.set_attribute("llm.provider", "anthropic")
            span.set_attribute("llm.model", "claude-sonnet-4-6")

            t0 = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.perf_counter() - t0) * 1000)
                span.set_attribute("llm.duration_ms", duration_ms)

                # If result has usage info (anthropic response object)
                if hasattr(result, "usage"):
                    span.set_attribute("llm.input_tokens", result.usage.input_tokens)
                    span.set_attribute("llm.output_tokens", result.usage.output_tokens)

                span.set_status(StatusCode.OK)
                return result
            except Exception as exc:
                span.set_attribute("llm.error", str(exc))
                span.set_status(StatusCode.ERROR, str(exc))
                raise
    return wrapper
