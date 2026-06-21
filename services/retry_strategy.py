import asyncio
import functools
from typing import Callable, Any
import structlog
from opentelemetry import trace

logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

def with_retry(max_retries: int = 3, base_delay: float = 1.0, escalation_factor: float = 2.0):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span("retry_strategy") as span:
                delay = base_delay
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        logger.warning(
                            "Attempt failed, retrying...",
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            error=str(e),
                            delay=delay
                        )
                        span.add_event(f"Attempt {attempt + 1} failed: {str(e)}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(delay)
                            delay *= escalation_factor
                
                logger.error("All retries exhausted", max_retries=max_retries, error=str(last_exception))
                span.set_attribute("error", True)
                span.set_attribute("error_message", str(last_exception))
                raise last_exception
        return wrapper
    return decorator
