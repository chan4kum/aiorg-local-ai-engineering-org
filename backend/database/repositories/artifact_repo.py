from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Artifact

class ArtifactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Artifact:
        db_item = Artifact(**data)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def get_by_id(self, item_id: str) -> Optional[Artifact]:
        result = await self.session.execute(
            select(Artifact).where(Artifact.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Artifact]:
        result = await self.session.execute(select(Artifact))
        return list(result.scalars().all())

    async def get_versions(self, item_id: str) -> List[dict]:
        # This assumes versions might be stored in a separate table or serialized
        # Here we just return mock or base data for demonstration
        item = await self.get_by_id(item_id)
        if not item:
            return []
        # Return versions based on item data or related version model
        return [{"version": 1, "created_at": item.created_at, "content": "base"}]

    async def update(self, item_id: str, data: dict) -> Optional[Artifact]:
        result = await self.session.execute(
            update(Artifact)
            .where(Artifact.id == item_id)
            .values(**data)
            .returning(Artifact)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, item_id: str) -> bool:
        result = await self.session.execute(
            delete(Artifact).where(Artifact.id == item_id)
        )
        await self.session.commit()
        return result.rowcount > 0
