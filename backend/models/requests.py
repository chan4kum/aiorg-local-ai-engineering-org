from pydantic import BaseModel
from typing import Optional, Dict, Any

class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None

class CreateWorkflowRequest(BaseModel):
    project_id: str
    name: str

class StartTaskRequest(BaseModel):
    workflow_id: str
    description: str
    parameters: Optional[Dict[str, Any]] = None
