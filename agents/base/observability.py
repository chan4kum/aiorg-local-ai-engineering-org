from opentelemetry import trace
import structlog
from typing import Optional
from contextlib import contextmanager

class AgentObservabilityMixin:
    def __init__(self):
        self.tracer = trace.get_tracer(self.__class__.__name__)
        self.logger = structlog.get_logger(self.__class__.__name__)

    @contextmanager
    def start_span(self, name: str):
        with self.tracer.start_as_current_span(name) as span:
            yield span

    def record_error(self, error: Exception, span: Optional[trace.Span] = None):
        self.logger.error("Agent error occurred", error=str(error), error_type=type(error).__name__)
        current_span = span or trace.get_current_span()
        if current_span:
            current_span.set_attribute("error", True)
            current_span.record_exception(error)
