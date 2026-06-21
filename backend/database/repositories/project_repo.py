from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import ProjectModel

class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_data: dict) -> ProjectModel:
        db_project = ProjectModel(**project_data)
        self.session.add(db_project)
        await self.session.commit()
        await self.session.refresh(db_project)
        return db_project

    async def get_by_id(self, project_id: str) -> Optional[ProjectModel]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ProjectModel]:
        result = await self.session.execute(select(ProjectModel))
        return list(result.scalars().all())

    async def update(self, project_id: str, data: dict) -> Optional[ProjectModel]:
        result = await self.session.execute(
            update(ProjectModel)
            .where(ProjectModel.id == project_id)
            .values(**data)
            .returning(ProjectModel)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, project_id: str) -> bool:
        result = await self.session.execute(
            delete(ProjectModel).where(ProjectModel.id == project_id)
        )
        await self.session.commit()
        return result.rowcount > 0
