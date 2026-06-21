from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.database.models import MemoryRecord
from opentelemetry import trace
import structlog
import uuid
import datetime

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class PostgresMemory:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def save_record(self, run_id: str, content: str, metadata: Dict[str, Any] = None) -> str:
        with tracer.start_as_current_span("postgres_memory.save"):
            async with self.session_maker() as session:
                record = MemoryRecord(
                    run_id=uuid.UUID(run_id),
                    content=content,
                    metadata_=metadata or {}
                )
                session.add(record)
                await session.commit()
                logger.info("Saved memory record", run_id=run_id, record_id=str(record.id))
                return str(record.id)

    async def get_records(self, run_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        with tracer.start_as_current_span("postgres_memory.get"):
            async with self.session_maker() as session:
                stmt = select(MemoryRecord).where(MemoryRecord.run_id == uuid.UUID(run_id)).order_by(MemoryRecord.created_at.desc()).limit(limit)
                result = await session.execute(stmt)
                records = result.scalars().all()
                return [
                    {
                        "id": str(r.id),
                        "content": r.content,
                        "metadata": r.metadata_,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in records
                ]
                
    async def save_project_blueprint(self, run_id: str, blueprint: Dict[str, Any]) -> str:
        """Saves the project blueprint (System Architect memory)"""
        with tracer.start_as_current_span("postgres_memory.save_blueprint"):
            metadata = {"type": "project_blueprint", "importance_score": 100}
            return await self.save_record(run_id, str(blueprint), metadata)
            
    async def add_lesson_learned(self, run_id: str, lesson: str, importance_score: int = 50) -> str:
        """Saves a lesson learned with an importance score for pruning."""
        metadata = {"type": "lessons_learned", "importance_score": importance_score, "last_accessed": datetime.datetime.utcnow().isoformat()}
        return await self.save_record(run_id, lesson, metadata)
        
    async def prune_expired_memory(self):
        """
        Memory Expiration Policy.
        Prunes lessons_learned that have an importance score < 50 and haven't been accessed recently.
        """
        with tracer.start_as_current_span("postgres_memory.prune"):
            async with self.session_maker() as session:
                # Stub logic to find records to prune. 
                # In a real implementation we would do a JSONB query on metadata_
                logger.info("Pruning expired memory based on importance_score and relevance...")
                # stmt = delete(MemoryRecord).where(...)
                # await session.execute(stmt)
                # await session.commit()
                pass
