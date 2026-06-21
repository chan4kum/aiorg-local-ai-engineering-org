from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Project

class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_data: dict) -> Project:
        db_project = Project(**project_data)
        self.session.add(db_project)
        await self.session.commit()
        await self.session.refresh(db_project)
        return db_project

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Project]:
        result = await self.session.execute(select(Project))
        return list(result.scalars().all())

    async def update(self, project_id: str, project_data: dict) -> Optional[Project]:
        await self.session.execute(
            update(Project).where(Project.id == project_id).values(**project_data)
        )
        await self.session.commit()
        return await self.get_by_id(project_id)

    async def delete(self, project_id: str) -> bool:
        result = await self.session.execute(
            delete(Project).where(Project.id == project_id)
        )
        await self.session.commit()
        return result.rowcount > 0
