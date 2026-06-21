from pydantic import BaseModel
from typing import Optional, List, Any
from .domain import Project, Workflow, Task

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class ProjectResponse(ApiResponse):
    data: Optional[Project] = None

class ProjectListResponse(ApiResponse):
    data: List[Project] = []
