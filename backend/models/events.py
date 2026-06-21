from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class EventType(str, Enum):
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    AGENT_MESSAGE = "agent.message"
    SYSTEM_ALERT = "system.alert"

class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]
    source: str

class AgentMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    sender: str
    recipient: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
