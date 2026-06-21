from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.dependencies import get_db_session, get_task_queue
from backend.database.repositories.task_repo import TaskRepository
from backend.models.responses import TaskResponse
from services.task_queue import TaskQueue

router = APIRouter()

@router.get("", response_model=List[TaskResponse])
async def list_tasks(session: AsyncSession = Depends(get_db_session)):
    repo = TaskRepository(session)
    tasks = await repo.get_all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_task(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
    task_queue: TaskQueue = Depends(get_task_queue)
):
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    await task_queue.enqueue("retry_task", {"task_id": task_id})
    return {"message": "Task retry initiated"}
