from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import AgentRun

class AgentRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> AgentRun:
        db_item = AgentRun(**data)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def get_by_id(self, item_id: str) -> Optional[AgentRun]:
        result = await self.session.execute(
            select(AgentRun).where(AgentRun.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, agent_id: Optional[str] = None) -> List[AgentRun]:
        query = select(AgentRun)
        if agent_id:
            query = query.where(AgentRun.agent_id == agent_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_stats(self, agent_id: str) -> Dict[str, Any]:
        result = await self.session.execute(
            select(
                func.count().label("total_runs"),
                func.avg(AgentRun.duration).label("avg_duration")
            ).where(AgentRun.agent_id == agent_id)
        )
        row = result.first()
        if row:
            return {
                "total_runs": row.total_runs,
                "avg_duration": float(row.avg_duration) if row.avg_duration else 0.0
            }
        return {"total_runs": 0, "avg_duration": 0.0}

    async def update(self, item_id: str, data: dict) -> Optional[AgentRun]:
        result = await self.session.execute(
            update(AgentRun)
            .where(AgentRun.id == item_id)
            .values(**data)
            .returning(AgentRun)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, item_id: str) -> bool:
        result = await self.session.execute(
            delete(AgentRun).where(AgentRun.id == item_id)
        )
        await self.session.commit()
        return result.rowcount > 0
