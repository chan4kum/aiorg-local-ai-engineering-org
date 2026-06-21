from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class Project(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Workflow(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    name: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    workflow_id: UUID
    description: str
    status: str = "pending"
    result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Artifact(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    name: str
    content: str
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    agent_name: str
    status: str = "running"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class Evaluation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    score: float
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
