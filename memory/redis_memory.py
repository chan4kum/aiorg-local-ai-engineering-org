import json
import redis.asyncio as redis
from typing import Dict, Any, Optional
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class RedisMemory:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def set_working_memory(self, session_id: str, key: str, value: Any, ttl: int = 3600):
        with tracer.start_as_current_span("redis_memory.set"):
            redis_key = f"session:{session_id}:memory:{key}"
            await self.redis.set(redis_key, json.dumps(value), ex=ttl)
            logger.info("Set working memory", key=redis_key)

    async def get_working_memory(self, session_id: str, key: str) -> Optional[Any]:
        with tracer.start_as_current_span("redis_memory.get"):
            redis_key = f"session:{session_id}:memory:{key}"
            data = await self.redis.get(redis_key)
            if data:
                return json.loads(data)
            return None

    async def set_task_state(self, task_id: str, state: Dict[str, Any], ttl: int = 86400):
        with tracer.start_as_current_span("redis_memory.set_state"):
            redis_key = f"task:{task_id}:state"
            await self.redis.set(redis_key, json.dumps(state), ex=ttl)

    async def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        with tracer.start_as_current_span("redis_memory.get_state"):
            redis_key = f"task:{task_id}:state"
            data = await self.redis.get(redis_key)
            if data:
                return json.loads(data)
            return None

    async def heartbeat(self, agent_id: str, ttl: int = 30):
        with tracer.start_as_current_span("redis_memory.heartbeat"):
            redis_key = f"agent:{agent_id}:heartbeat"
            await self.redis.set(redis_key, "alive", ex=ttl)
