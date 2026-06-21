from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from typing import Optional, List, Dict, Any
from opentelemetry import trace
import structlog
import uuid
from .embeddings import EmbeddingService

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class QdrantMemory:
    def __init__(self, embedding_service: EmbeddingService, qdrant_url: str = "http://localhost:6333", collection_name: str = "agent_memory"):
        self.client = AsyncQdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_service = embedding_service
        self.dimension = 1536 # OpenAI dimension

    async def initialize(self):
        collections = await self.client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )

    async def add_memory(self, text: str, metadata: Dict[str, Any] = None) -> str:
        with tracer.start_as_current_span("qdrant_memory.add"):
            embedding = await self.embedding_service.get_embedding(text)
            point_id = str(uuid.uuid4())
            
            payload = {"text": text}
            if metadata:
                payload.update(metadata)
                
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            logger.info("Added semantic memory", point_id=point_id)
            return point_id

    async def search_memory(self, query: str, limit: int = 5, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        with tracer.start_as_current_span("qdrant_memory.search"):
            embedding = await self.embedding_service.get_embedding(query)
            
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return [
                {
                    "id": str(hit.id),
                    "text": hit.payload.get("text", ""),
                    "score": hit.score,
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
                }
                for hit in results
            ]
