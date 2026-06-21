import litellm
from typing import List
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class EmbeddingService:
    def __init__(self, default_model: str = "text-embedding-ada-002"):
        self.default_model = default_model

    async def get_embedding(self, text: str) -> List[float]:
        with tracer.start_as_current_span("embedding_service.get"):
            try:
                response = await litellm.aembedding(
                    model=self.default_model,
                    input=text
                )
                embedding = response.data[0]["embedding"]
                return embedding
            except Exception as e:
                logger.error("Primary embedding failed, falling back to Ollama", error=str(e))
                # Fallback to local Ollama
                try:
                    response = await litellm.aembedding(
                        model="ollama/nomic-embed-text",
                        input=text
                    )
                    embedding = response.data[0]["embedding"]
                    return embedding
                except Exception as fallback_e:
                    logger.error("Fallback embedding failed", error=str(fallback_e))
                    raise
