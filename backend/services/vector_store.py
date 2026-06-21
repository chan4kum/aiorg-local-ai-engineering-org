"""
Vector Store Service - Qdrant-based vector storage for semantic search and memory.
"""

import logging
from typing import Any, Optional
from uuid import uuid4

from backend.config import get_config, QdrantConfig

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Vector store service using Qdrant for semantic search."""

    def __init__(self, config: Optional[QdrantConfig] = None):
        self.config = config or get_config().qdrant
        self._client = None

    async def _get_client(self):
        """Lazy-initialize the Qdrant async client."""
        if self._client is None:
            try:
                from qdrant_client import AsyncQdrantClient
                self._client = AsyncQdrantClient(
                    host=self.config.host,
                    port=self.config.port,
                    api_key=self.config.api_key,
                )
            except ImportError:
                logger.warning("qdrant-client not installed, using in-memory fallback")
                from qdrant_client import AsyncQdrantClient
                self._client = AsyncQdrantClient(":memory:")
        return self._client

    async def ensure_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,
        distance: str = "Cosine",
    ) -> None:
        """Create collection if it doesn't exist."""
        from qdrant_client.models import Distance, VectorParams

        client = await self._get_client()
        collections = await client.get_collections()
        existing = [c.name for c in collections.collections]

        if collection_name not in existing:
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclid": Distance.EUCLID,
                "Dot": Distance.DOT,
            }
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, Distance.COSINE),
                ),
            )
            logger.info(f"Created collection: {collection_name}")

    async def upsert(
        self,
        collection_name: str,
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        """Insert or update vectors with metadata payloads.
        
        Args:
            collection_name: Target collection
            vectors: List of embedding vectors
            payloads: List of metadata dicts
            ids: Optional point IDs (generated if not provided)
            
        Returns:
            List of point IDs
        """
        from qdrant_client.models import PointStruct

        client = await self._get_client()
        
        if ids is None:
            ids = [str(uuid4()) for _ in vectors]

        points = [
            PointStruct(id=pid, vector=vec, payload=payload)
            for pid, vec, payload in zip(ids, vectors, payloads)
        ]

        await client.upsert(collection_name=collection_name, points=points)
        return ids

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[dict] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors.
        
        Args:
            collection_name: Collection to search
            query_vector: Query embedding vector
            limit: Max results to return
            score_threshold: Minimum similarity score
            filter_conditions: Qdrant filter conditions
            
        Returns:
            List of dicts with 'id', 'score', and 'payload' keys
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        client = await self._get_client()

        search_filter = None
        if filter_conditions:
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            search_filter = Filter(must=conditions)

        results = await client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=search_filter,
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload or {},
            }
            for hit in results
        ]

    async def delete(
        self,
        collection_name: str,
        ids: list[str],
    ) -> None:
        """Delete points by IDs."""
        from qdrant_client.models import PointIdsList

        client = await self._get_client()
        await client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=ids),
        )

    async def close(self):
        """Close the client connection."""
        if self._client:
            await self._client.close()
            self._client = None


_vector_store: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """Get or create singleton vector store service."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store
