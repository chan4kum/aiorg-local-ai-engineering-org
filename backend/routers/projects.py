from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.dependencies import get_db, get_task_queue, get_event_bus
from backend.database.repositories.project_repo import ProjectRepository
from backend.models.requests import CreateProjectRequest
from backend.models.responses import ProjectResponse
from services.task_queue import TaskQueue
from services.event_bus import EventBus

router = APIRouter()


def _project_to_dict(project) -> dict:
    """Convert a SQLAlchemy Project model (or dict) to a serializable dict."""
    if isinstance(project, dict):
        return project
    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    session: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    repo = ProjectRepository(session)
    project = await repo.create(request.model_dump())
    project_data = _project_to_dict(project)
    await event_bus.publish("project.created", {"project_id": project_data["id"]})
    return ProjectResponse(success=True, data=project_data)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(session: AsyncSession = Depends(get_db)):
    repo = ProjectRepository(session)
    projects = await repo.get_all()
    return [ProjectResponse(success=True, data=_project_to_dict(p)) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, session: AsyncSession = Depends(get_db)):
    repo = ProjectRepository(session)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(success=True, data=_project_to_dict(project))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: CreateProjectRequest,
    session: AsyncSession = Depends(get_db),
):
    repo = ProjectRepository(session)
    project = await repo.update(project_id, request.model_dump(exclude_unset=True))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(success=True, data=_project_to_dict(project))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, session: AsyncSession = Depends(get_db)):
    repo = ProjectRepository(session)
    success = await repo.delete(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/{project_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_project(
    project_id: str,
    session: AsyncSession = Depends(get_db),
    task_queue: TaskQueue = Depends(get_task_queue),
):
    repo = ProjectRepository(session)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await task_queue.enqueue({"task_type": "start_project_workflow", "project_id": project_id})
    return {"message": "Project start initiated"}
