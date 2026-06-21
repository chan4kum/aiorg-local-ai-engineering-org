from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from typing import Optional, List, Dict, Any
import hashlib
from opentelemetry import trace
import structlog
import uuid

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class SemanticCache:
    def __init__(self, qdrant_url: str = "http://localhost:6333", collection_name: str = "llm_cache"):
        self.client = AsyncQdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.dimension = 1536 # OpenAI embeddings dimension

    async def initialize(self):
        collections = await self.client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )

    def _hash_prompt(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()

    async def get_cached_response(self, prompt_embedding: List[float], threshold: float = 0.95) -> Optional[str]:
        with tracer.start_as_current_span("semantic_cache.get"):
            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=prompt_embedding,
                limit=1,
                score_threshold=threshold
            )
            
            if search_result:
                logger.info("Cache hit", score=search_result[0].score)
                return search_result[0].payload.get("response")
            return None

    async def set_cached_response(self, prompt: str, prompt_embedding: List[float], response: str):
        with tracer.start_as_current_span("semantic_cache.set"):
            point_id = str(uuid.uuid4())
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=prompt_embedding,
                        payload={
                            "prompt_hash": self._hash_prompt(prompt),
                            "response": response
                        }
                    )
                ]
            )
            logger.info("Cached response", point_id=point_id)
