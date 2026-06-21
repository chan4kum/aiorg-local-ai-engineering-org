from typing import Dict, Any, Callable, Awaitable
from backend.services.event_bus import EventBus
import structlog

logger = structlog.get_logger()

class AgentCommunicationMixin:
    def __init__(self, event_bus: EventBus, agent_name: str):
        self.event_bus = event_bus
        self.agent_name = agent_name
        self.inbox_stream = f"agent:{agent_name}:inbox"

    async def setup_communication(self):
        self.event_bus.subscribe(self.inbox_stream, self._handle_incoming_message)
        logger.info("Agent communication setup", stream=self.inbox_stream)

    async def _handle_incoming_message(self, payload: Dict[str, Any]):
        logger.info("Agent received message", agent=self.agent_name, payload=payload)
        await self.on_message_received(payload)

    async def on_message_received(self, payload: Dict[str, Any]):
        """Override this method to handle incoming messages"""
        pass

    async def publish_message(self, recipient: str, content: str, msg_type: str = "text"):
        target_stream = f"agent:{recipient}:inbox" if recipient != "system" else "system:events"
        event = {
            "sender": self.agent_name,
            "recipient": recipient,
            "type": msg_type,
            "content": content
        }
        await self.event_bus.publish(target_stream, event)
        logger.debug("Agent published message", sender=self.agent_name, recipient=recipient)
