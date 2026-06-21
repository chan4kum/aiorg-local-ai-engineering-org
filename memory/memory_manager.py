from typing import List, Dict, Any, Optional
from opentelemetry import trace
import structlog
from .redis_memory import RedisMemory
from .postgres_memory import PostgresMemory
from .qdrant_memory import QdrantMemory

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class MemoryManager:
    def __init__(self, redis_memory: RedisMemory, postgres_memory: PostgresMemory, qdrant_memory: QdrantMemory):
        self.redis = redis_memory
        self.postgres = postgres_memory
        self.qdrant = qdrant_memory

    async def initialize(self):
        await self.qdrant.initialize()

    async def save_interaction(self, session_id: str, run_id: str, text: str, metadata: Dict[str, Any] = None):
        with tracer.start_as_current_span("memory_manager.save_interaction"):
            metadata = metadata or {}
            
            # Save to PG
            await self.postgres.save_record(run_id, text, metadata)
            
            # Save to Qdrant for semantic search
            metadata["run_id"] = run_id
            metadata["session_id"] = session_id
            await self.qdrant.add_memory(text, metadata)
            
            # Update working memory in Redis
            history = await self.redis.get_working_memory(session_id, "history") or []
            history.append({"text": text, "metadata": metadata})
            # Keep only last 10 messages in fast memory
            await self.redis.set_working_memory(session_id, "history", history[-10:])
            logger.info("Saved interaction to unified memory", session_id=session_id)

    async def retrieve_context(self, session_id: str, run_id: str, query: str) -> Dict[str, Any]:
        with tracer.start_as_current_span("memory_manager.retrieve_context"):
            working_memory = await self.redis.get_working_memory(session_id, "history") or []
            semantic_results = await self.qdrant.search_memory(query)
            
            return {
                "recent_history": working_memory,
                "semantic_context": semantic_results
            }
