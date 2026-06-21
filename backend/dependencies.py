from typing import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_db_session
from services.event_bus import EventBus
from services.task_queue import TaskQueue
from backend.config import settings

def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus

def get_task_queue(request: Request) -> TaskQueue:
    return request.app.state.task_queue

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session
