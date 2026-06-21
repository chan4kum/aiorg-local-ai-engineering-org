from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.dependencies import get_db_session, get_task_queue, get_event_bus
from backend.database.repositories.project_repo import ProjectRepository
from backend.models.requests import CreateProjectRequest
from backend.models.responses import ProjectResponse
from services.task_queue import TaskQueue
from services.event_bus import EventBus

router = APIRouter()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    session: AsyncSession = Depends(get_db_session),
    event_bus: EventBus = Depends(get_event_bus)
):
    repo = ProjectRepository(session)
    project = await repo.create(request.model_dump())
    
    # Map model to response dict if necessary, or just rely on ORM mode
    await event_bus.publish("project.created", {"project_id": project.id})
    return project

@router.get("", response_model=List[ProjectResponse])
async def list_projects(session: AsyncSession = Depends(get_db_session)):
    repo = ProjectRepository(session)
    projects = await repo.get_all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = ProjectRepository(session)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: CreateProjectRequest,
    session: AsyncSession = Depends(get_db_session)
):
    repo = ProjectRepository(session)
    project = await repo.update(project_id, request.model_dump(exclude_unset=True))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = ProjectRepository(session)
    success = await repo.delete(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
        
@router.post("/{project_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_project(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
    task_queue: TaskQueue = Depends(get_task_queue)
):
    repo = ProjectRepository(session)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await task_queue.enqueue("start_project_workflow", {"project_id": project_id})
    return {"message": "Project start initiated"}
