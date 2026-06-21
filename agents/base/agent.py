from typing import Dict, Any, List, Optional
import asyncio
from pydantic import BaseModel, Field
import uuid
import structlog
from opentelemetry import trace

from backend.services.llm_service import LLMService
from services.event_bus import EventBus
from backend.memory.memory_manager import MemoryManager
from .memory import AgentMemoryMixin
from .observability import AgentObservabilityMixin
from .communication import AgentCommunicationMixin
from .tools import BaseTool

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class AgentConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    system_prompt: str
    model: str = "gpt-4"

class AgentBase(AgentMemoryMixin, AgentObservabilityMixin, AgentCommunicationMixin):
    def __init__(self, 
                 config: AgentConfig, 
                 llm_service: LLMService,
                 memory_manager: MemoryManager,
                 event_bus: EventBus,
                 tools: List[BaseTool] = None):
        AgentMemoryMixin.__init__(self, memory_manager)
        AgentObservabilityMixin.__init__(self)
        AgentCommunicationMixin.__init__(self, event_bus, config.name)
        
        self.config = config
        self.llm = llm_service
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.system_prompt = config.system_prompt
        self.is_running = False

    async def initialize(self):
        with self.start_span("agent.initialize") as span:
            span.set_attribute("agent.id", self.config.id)
            span.set_attribute("agent.name", self.config.name)
            await self.setup_communication()
            logger.info("Agent initialized", agent_name=self.config.name)

    async def process_task(self, task_id: str, prompt: str, session_id: str) -> Dict[str, Any]:
        with self.start_span("agent.process_task") as span:
            self.is_running = True
            try:
                span.set_attribute("task.id", task_id)
                span.set_attribute("session.id", session_id)
                
                context = await self.get_context(session_id, task_id, prompt)
                
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "system", "content": f"Context:\n{context}"},
                    {"role": "user", "content": prompt}
                ]
                
                response = await self.llm.generate_response(messages, model=self.config.model)
                
                # Execute tools if any requested in response (simplified logic)
                # In a real implementation we would parse tool calls from response
                
                await self.save_memory(session_id, task_id, f"User: {prompt}\nAgent: {response['content']}")
                await self.publish_message("system", f"Completed task {task_id}")
                
                return {
                    "status": "success",
                    "result": response["content"],
                    "usage": response["usage"]
                }
            except Exception as e:
                self.record_error(e)
                logger.error("Agent failed to process task", error=str(e), agent_name=self.config.name)
                return {
                    "status": "error",
                    "error": str(e)
                }
            finally:
                self.is_running = False

    async def run(self):
        self.is_running = True
        logger.info("Agent main loop started", agent_name=self.config.name)
        while self.is_running:
            await asyncio.sleep(1) # Keep alive loop, could listen to queues here
            
    async def stop(self):
        self.is_running = False
        logger.info("Agent stopped", agent_name=self.config.name)
