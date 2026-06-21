from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.models import MemoryRecord
from opentelemetry import trace
import structlog
import uuid

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
