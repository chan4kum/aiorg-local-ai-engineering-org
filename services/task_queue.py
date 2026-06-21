import json
import redis.asyncio as redis
from typing import Dict, Any, Optional
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class TaskQueue:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = "task_queue"

    async def start(self):
        pass

    async def stop(self):
        await self.redis.aclose()

    async def enqueue(self, task_data: Dict[str, Any]) -> str:
        with tracer.start_as_current_span("task_queue.enqueue"):
            task_json = json.dumps(task_data)
            msg_id = await self.redis.xadd(self.queue_name, {"task": task_json})
            logger.info("Enqueued task", msg_id=msg_id)
            return msg_id

    async def dequeue(self, group: str, consumer: str) -> Optional[Dict[str, Any]]:
        with tracer.start_as_current_span("task_queue.dequeue"):
            try:
                await self.redis.xgroup_create(self.queue_name, group, mkstream=True)
            except redis.exceptions.ResponseError:
                pass
            
            messages = await self.redis.xreadgroup(group, consumer, {self.queue_name: ">"}, count=1, block=100)
            if not messages:
                return None
            
            stream, msgs = messages[0]
            msg_id, msg_data = msgs[0]
            task_data = json.loads(msg_data["task"])
            task_data["_msg_id"] = msg_id
            return task_data

    async def acknowledge(self, group: str, msg_id: str):
        with tracer.start_as_current_span("task_queue.acknowledge"):
            await self.redis.xack(self.queue_name, group, msg_id)
            logger.info("Acknowledged task", msg_id=msg_id)
