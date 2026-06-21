import json
import redis.asyncio as redis
from typing import Dict, Any, Callable, Awaitable
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class EventBus:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.callbacks: Dict[str, list[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}

    async def publish(self, stream: str, event: Dict[str, Any]) -> str:
        with tracer.start_as_current_span("event_bus.publish") as span:
            span.set_attribute("stream", stream)
            event_json = json.dumps(event)
            message_id = await self.redis.xadd(stream, {"payload": event_json})
            logger.info("Published event", stream=stream, message_id=message_id)
            return message_id

    def subscribe(self, stream: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        if stream not in self.callbacks:
            self.callbacks[stream] = []
        self.callbacks[stream].append(callback)

    async def listen(self, group: str, consumer: str):
        for stream in self.callbacks.keys():
            try:
                await self.redis.xgroup_create(stream, group, mkstream=True)
            except redis.exceptions.ResponseError:
                pass # Group might already exist
        
        streams = {s: ">" for s in self.callbacks.keys()}
        while True:
            try:
                messages = await self.redis.xreadgroup(group, consumer, streams, block=1000, count=10)
                for stream, msgs in messages:
                    for msg_id, msg_data in msgs:
                        payload = json.loads(msg_data["payload"])
                        for callback in self.callbacks[stream]:
                            with tracer.start_as_current_span("event_bus.consume"):
                                try:
                                    await callback(payload)
                                    await self.redis.xack(stream, group, msg_id)
                                except Exception as e:
                                    logger.error("Error processing message", error=str(e), msg_id=msg_id)
                                    await self.redis.xadd(f"{stream}_dlq", {"payload": msg_data["payload"], "error": str(e)})
                                    await self.redis.xack(stream, group, msg_id)
            except Exception as e:
                logger.error("Redis read error", error=str(e))
