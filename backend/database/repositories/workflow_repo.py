from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import WorkflowModel

class WorkflowRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> WorkflowModel:
        db_item = WorkflowModel(**data)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def get_by_id(self, item_id: str) -> Optional[WorkflowModel]:
        result = await self.session.execute(
            select(WorkflowModel).where(WorkflowModel.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[WorkflowModel]:
        result = await self.session.execute(select(WorkflowModel))
        return list(result.scalars().all())

    async def update(self, item_id: str, data: dict) -> Optional[WorkflowModel]:
        result = await self.session.execute(
            update(WorkflowModel)
            .where(WorkflowModel.id == item_id)
            .values(**data)
            .returning(WorkflowModel)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, item_id: str) -> bool:
        result = await self.session.execute(
            delete(WorkflowModel).where(WorkflowModel.id == item_id)
        )
        await self.session.commit()
        return result.rowcount > 0
