from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.dependencies import get_db_session
from backend.database.repositories.artifact_repo import ArtifactRepository
from backend.models.responses import ArtifactResponse

router = APIRouter()

@router.get("", response_model=List[ArtifactResponse])
async def list_artifacts(session: AsyncSession = Depends(get_db_session)):
    repo = ArtifactRepository(session)
    return await repo.get_all()

@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = ArtifactRepository(session)
    artifact = await repo.get_by_id(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact

@router.get("/{artifact_id}/versions")
async def get_artifact_versions(artifact_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = ArtifactRepository(session)
    versions = await repo.get_versions(artifact_id)
    return versions

@router.get("/{artifact_id}/content")
async def get_artifact_content(artifact_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = ArtifactRepository(session)
    artifact = await repo.get_by_id(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    # Using a generic getattr for content if the model has it
    return {"content": getattr(artifact, "content", "Empty content")}
