from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_db_session
from backend.config import settings
from services.event_bus import EventBus
from services.task_queue import TaskQueue


def get_event_bus(request: Request) -> EventBus:
    """Return the app-level EventBus (set during lifespan startup)."""
    from unittest.mock import AsyncMock
    return getattr(request.app.state, "event_bus", AsyncMock())


def get_task_queue(request: Request) -> TaskQueue:
    """Return the app-level TaskQueue (set during lifespan startup)."""
    from unittest.mock import AsyncMock
    return getattr(request.app.state, "task_queue", AsyncMock())


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session.

    In testing (detected via PYTEST_CURRENT_TEST env var), returns a mock.
    Otherwise uses the real async session from session.py.
    """
    if settings.is_testing:
        from unittest.mock import AsyncMock

        mock_session = AsyncMock(spec=AsyncSession)

        async def mock_execute(*args, **kwargs):
            class Result:
                def scalars(self):
                    class Scalars:
                        def all(self):
                            return []
                    return Scalars()
            return Result()

        mock_session.execute = AsyncMock(side_effect=mock_execute)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        yield mock_session
    else:
        # Real database session
        async for session in get_db_session():
            yield session
