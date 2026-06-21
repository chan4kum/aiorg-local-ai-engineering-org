from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.dependencies import get_db_session
from backend.database.repositories.workflow_repo import WorkflowRepository
from backend.database.repositories.task_repo import TaskRepository
from backend.models.responses import WorkflowResponse, TaskResponse

router = APIRouter()

@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(session: AsyncSession = Depends(get_db_session)):
    repo = WorkflowRepository(session)
    workflows = await repo.get_all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = WorkflowRepository(session)
    workflow = await repo.get_by_id(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.get("/{workflow_id}/tasks", response_model=List[TaskResponse])
async def list_workflow_tasks(workflow_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = TaskRepository(session)
    tasks = await repo.get_all(workflow_id=workflow_id)
    return tasks
