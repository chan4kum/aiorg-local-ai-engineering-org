from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    name = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"))
    description = Column(Text)
    status = Column(String, default="pending")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    agent_name = Column(String)
    status = Column(String, default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class LlmCall(Base):
    __tablename__ = "llm_calls"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id"))
    prompt = Column(Text)
    response = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ToolCall(Base):
    __tablename__ = "tool_calls"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id"))
    tool_name = Column(String)
    inputs = Column(JSON)
    outputs = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ArtifactVersion(Base):
    __tablename__ = "artifact_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artifact_id = Column(UUID(as_uuid=True), ForeignKey("artifacts.id"))
    version = Column(Integer)
    content_hash = Column(String)
    diff = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id"))
    score = Column(Float)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MemoryRecord(Base):
    __tablename__ = "memory_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id"))
    content = Column(Text)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, index=True)
    source = Column(String)
    payload = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Log(Base):
    __tablename__ = "logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String)
    message = Column(Text)
    metadata_ = Column("metadata", JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AgentConfig(Base):
    __tablename__ = "agent_configs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    configuration = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
