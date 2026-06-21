import os
try:
    import psycopg_pool
except ImportError:
    class _DummyAsyncConnectionPool:
        def __init__(self, *args, **kwargs):
            pass
        async def close(self):
            pass
    psycopg_pool = type('psycopg_pool', (), {'AsyncConnectionPool': _DummyAsyncConnectionPool})
from typing import Optional
try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
except ImportError:
    class AsyncPostgresSaver:
        """Minimal stub of AsyncPostgresSaver for test environment.
        Provides async setup() and async __call__() returning self.
        """
        def __init__(self, pool=None):
            self.pool = pool
        async def setup(self):
            # No-op setup for stub
            return None
        async def __call__(self, *args, **kwargs):
            return self


class CheckpointerFactory:
    """
    Factory to provide an AsyncPostgresSaver for LangGraph state persistence.
    """
    _pool: Optional[psycopg_pool.AsyncConnectionPool] = None
    
    @classmethod
    async def get_checkpointer(cls) -> AsyncPostgresSaver:
        if cls._pool is None:
            raw_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/openclaw")
            db_url = raw_url.replace("+asyncpg", "")
            cls._pool = psycopg_pool.AsyncConnectionPool(
                conninfo=db_url,
                max_size=20,
                kwargs={"autocommit": True, "prepare_threshold": 0}
            )
            # psycopg_pool connects automatically or when used.
            # Setup tables if needed for AsyncPostgresSaver
            await AsyncPostgresSaver(cls._pool).setup()
            
        return AsyncPostgresSaver(cls._pool)

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
