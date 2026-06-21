import json
import asyncio
from typing import Dict, Any, Callable, Awaitable
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class EventBus:
    def __init__(self):
        self.callbacks: Dict[str, list[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        self.queues: Dict[str, asyncio.Queue] = {}
        self.tasks: list[asyncio.Task] = []

    async def publish(self, stream: str, event: Dict[str, Any]) -> str:
        with tracer.start_as_current_span("event_bus.publish") as span:
            span.set_attribute("stream", stream)
            if stream not in self.queues:
                self.queues[stream] = asyncio.Queue()
            
            event_json = json.dumps(event)
            await self.queues[stream].put(event_json)
            # In an in-memory queue, message_id isn't as easily tracked, but we can generate or mock one.
            message_id = "mem-" + str(id(event_json))
            logger.info("Published event", stream=stream, message_id=message_id)
            return message_id

    def subscribe(self, stream: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        if stream not in self.callbacks:
            self.callbacks[stream] = []
        self.callbacks[stream].append(callback)

    async def listen(self, group: str, consumer: str):
        # group and consumer are mostly ignored in this simple in-memory queue, 
        # but we maintain the signature for compatibility.
        for stream in self.callbacks.keys():
            if stream not in self.queues:
                self.queues[stream] = asyncio.Queue()
            task = asyncio.create_task(self._consume(stream))
            self.tasks.append(task)
            
        # Keep listening running indefinitely to mimic Redis blocking read
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("EventBus listener cancelled")

    async def _consume(self, stream: str):
        while True:
            try:
                msg_data = await self.queues[stream].get()
                payload = json.loads(msg_data)
                for callback in self.callbacks.get(stream, []):
                    with tracer.start_as_current_span("event_bus.consume"):
                        try:
                            await callback(payload)
                        except Exception as e:
                            logger.error("Error processing message", error=str(e))
                            # Send to DLQ
                            dlq_stream = f"{stream}_dlq"
                            if dlq_stream not in self.queues:
                                self.queues[dlq_stream] = asyncio.Queue()
                            await self.queues[dlq_stream].put(json.dumps({"payload": msg_data, "error": str(e)}))
                self.queues[stream].task_done()
            except Exception as e:
                logger.error("EventBus consume error", error=str(e))
