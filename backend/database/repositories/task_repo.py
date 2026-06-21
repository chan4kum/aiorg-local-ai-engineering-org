from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import TaskModel

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> TaskModel:
        db_item = TaskModel(**data)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def get_by_id(self, item_id: str) -> Optional[TaskModel]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, workflow_id: Optional[str] = None) -> List[TaskModel]:
        query = select(TaskModel)
        if workflow_id:
            query = query.where(TaskModel.workflow_id == workflow_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, item_id: str, data: dict) -> Optional[TaskModel]:
        result = await self.session.execute(
            update(TaskModel)
            .where(TaskModel.id == item_id)
            .values(**data)
            .returning(TaskModel)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, item_id: str) -> bool:
        result = await self.session.execute(
            delete(TaskModel).where(TaskModel.id == item_id)
        )
        await self.session.commit()
        return result.rowcount > 0
