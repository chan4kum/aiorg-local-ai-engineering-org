import litellm
from typing import List, Dict, Any, Optional
from opentelemetry import trace
import structlog
from .retry_strategy import with_retry

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class LLMService:
    def __init__(self, default_model: str = "gpt-4"):
        self.default_model = default_model

    @with_retry(max_retries=3, base_delay=1.0)
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        with tracer.start_as_current_span("llm_service.generate"):
            model_to_use = model or self.default_model
            logger.info("Calling LLM", model=model_to_use)
            
            try:
                response = await litellm.acompletion(
                    model=model_to_use,
                    messages=messages,
                    temperature=temperature
                )
                
                content = response.choices[0].message.content
                usage = response.usage.dict() if response.usage else {}
                cost = litellm.completion_cost(completion_response=response) or 0.0
                
                logger.info("LLM call successful", cost=cost, tokens=usage.get("total_tokens"))
                
                return {
                    "content": content,
                    "usage": usage,
                    "cost": cost
                }
            except Exception as e:
                logger.error("LLM call failed", error=str(e))
                raise
