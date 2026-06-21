import contextlib
from fastapi import FastAPI
from backend.config import settings
from backend.routers import (
    projects, workflows, tasks, agents,
    artifacts, evaluations, memory, websocket
)
from backend.middleware.cors import setup_cors
from backend.middleware.auth import AuthMiddleware
from backend.middleware.tracing import setup_tracing
from backend.middleware.rate_limit import RateLimitMiddleware
from services.event_bus import EventBus
from services.task_queue import TaskQueue


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev convenience — use alembic in production)
    from backend.database.models import Base
    from backend.database.session import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Setup background services
    app.state.event_bus = EventBus()
    app.state.task_queue = TaskQueue(settings.redis_url)

    try:
        await app.state.event_bus.start()
    except Exception:
        pass  # Redis may not be available in minimal dev mode

    try:
        await app.state.task_queue.start()
    except Exception:
        pass  # Redis may not be available in minimal dev mode

    yield

    # Teardown
    try:
        await app.state.task_queue.stop()
    except Exception:
        pass
    try:
        await app.state.event_bus.stop()
    except Exception:
        pass

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Middleware
setup_tracing(app)
setup_cors(app)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["artifacts"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["evaluations"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(websocket.router, tags=["websocket"])
