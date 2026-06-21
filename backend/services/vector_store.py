"""
Vector Store Service - pgvector-based vector storage for semantic search and memory.
"""

import json
import logging
from typing import Any, Optional
from uuid import uuid4

import asyncpg
from backend.config import get_config

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Vector store service using pgvector for semantic search."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url
        self._pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Lazy-initialize the asyncpg connection pool."""
        if self._pool is None:
            # If not provided, fetch from config or environment
            if not self.database_url:
                import os
                # Replace +asyncpg if present, as asyncpg.create_pool needs postgresql://
                raw_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/openclaw")
                self.database_url = raw_url.replace("+asyncpg", "")
            
            try:
                self._pool = await asyncpg.create_pool(self.database_url)
                async with self._pool.acquire() as conn:
                    # Ensure pgvector extension exists
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            except Exception as e:
                logger.error(f"Failed to initialize pgvector connection pool: {e}")
                raise
        return self._pool

    async def ensure_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,
        distance: str = "Cosine",
    ) -> None:
        """Create table for collection if it doesn't exist."""
        pool = await self._get_pool()
        
        # In pgvector, we can create a table per collection or a unified table.
        # We'll create a table per collection for isolation, similar to Qdrant.
        # Sanitize collection_name for safety.
        safe_name = "".join([c if c.isalnum() else "_" for c in collection_name])
        table_name = f"collection_{safe_name}"
        
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id UUID PRIMARY KEY,
            embedding vector({vector_size}),
            payload JSONB
        );
        """
        async with pool.acquire() as conn:
            await conn.execute(create_table_query)
            # Create an index for vector similarity search
            # Using IVFFlat or HNSW (HNSW is better for pgvector >= 0.5.0)
            opclass = "vector_cosine_ops"
            if distance == "Euclid":
                opclass = "vector_l2_ops"
            elif distance == "Dot":
                opclass = "vector_ip_ops"
                
            index_query = f"""
            CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
            ON {table_name} USING hnsw (embedding {opclass});
            """
            try:
                await conn.execute(index_query)
            except Exception as e:
                logger.warning(f"Failed to create HNSW index (maybe pgvector version < 0.5.0): {e}")

        logger.info(f"Ensured pgvector collection table: {table_name}")

    async def upsert(
        self,
        collection_name: str,
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        """Insert or update vectors with metadata payloads."""
        pool = await self._get_pool()
        safe_name = "".join([c if c.isalnum() else "_" for c in collection_name])
        table_name = f"collection_{safe_name}"

        if ids is None:
            ids = [str(uuid4()) for _ in vectors]

        # Convert vectors to strings formatted for pgvector '[1.0, 2.0, ...]'
        records = []
        for pid, vec, payload in zip(ids, vectors, payloads):
            vec_str = "[" + ",".join(map(str, vec)) + "]"
            records.append((pid, vec_str, json.dumps(payload)))

        query = f"""
        INSERT INTO {table_name} (id, embedding, payload)
        VALUES ($1::uuid, $2::vector, $3::jsonb)
        ON CONFLICT (id) DO UPDATE 
        SET embedding = EXCLUDED.embedding,
            payload = EXCLUDED.payload;
        """

        async with pool.acquire() as conn:
            async with conn.transaction():
                # asyncpg executemany
                await conn.executemany(query, records)
        return ids

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[dict] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        pool = await self._get_pool()
        safe_name = "".join([c if c.isalnum() else "_" for c in collection_name])
        table_name = f"collection_{safe_name}"

        vec_str = "[" + ",".join(map(str, query_vector)) + "]"
        
        # Distance operator <=> for Cosine distance
        # 1 - (embedding <=> query) gives similarity score for Cosine
        query = f"""
        SELECT 
            id, 
            payload, 
            1 - (embedding <=> $1::vector) AS score
        FROM {table_name}
        """
        
        args = [vec_str]
        
        if filter_conditions:
            # Simple implementation of metadata filtering
            # Expecting filter_conditions to be simple key=value exact matches
            conditions = []
            for key, value in filter_conditions.items():
                arg_idx = len(args) + 1
                conditions.append(f"payload->>'{key}' = ${arg_idx}")
                args.append(str(value))
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        query += f"\nORDER BY embedding <=> $1::vector\nLIMIT {limit};"

        async with pool.acquire() as conn:
            try:
                rows = await conn.fetch(query, *args)
            except asyncpg.exceptions.UndefinedTableError:
                logger.warning(f"Collection {collection_name} does not exist.")
                return []

        results = []
        for row in rows:
            if score_threshold is not None and row['score'] < score_threshold:
                continue
            results.append({
                "id": str(row['id']),
                "score": row['score'],
                "payload": json.loads(row['payload']) if row['payload'] else {},
            })
            
        return results

    async def delete(
        self,
        collection_name: str,
        ids: list[str],
    ) -> None:
        """Delete points by IDs."""
        pool = await self._get_pool()
        safe_name = "".join([c if c.isalnum() else "_" for c in collection_name])
        table_name = f"collection_{safe_name}"

        query = f"DELETE FROM {table_name} WHERE id = ANY($1::uuid[]);"
        
        async with pool.acquire() as conn:
            await conn.execute(query, ids)

    async def close(self):
        """Close the pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

_vector_store: Optional[VectorStoreService] = None

def get_vector_store() -> VectorStoreService:
    """Get or create singleton vector store service."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store
