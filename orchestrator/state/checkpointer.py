import os
import asyncpg
from typing import Optional
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

class CheckpointerFactory:
    """
    Factory to provide an AsyncPostgresSaver for LangGraph state persistence.
    """
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def get_checkpointer(cls) -> AsyncPostgresSaver:
        if cls._pool is None:
            raw_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/openclaw")
            db_url = raw_url.replace("+asyncpg", "")
            cls._pool = await asyncpg.create_pool(db_url)
            
            # Setup tables if needed for AsyncPostgresSaver
            await AsyncPostgresSaver(cls._pool).setup()
            
        return AsyncPostgresSaver(cls._pool)

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
