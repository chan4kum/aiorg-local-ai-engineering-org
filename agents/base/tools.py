from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel
import structlog
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

class BaseTool(ABC):
    name: str
    description: str
    parameters: List[ToolParameter]

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        p.name: {
                            "type": p.type,
                            "description": p.description
                        } for p in self.parameters
                    },
                    "required": [p.name for p in self.parameters if p.required]
                }
            }
        }

class MCPToolWrapper(BaseTool):
    """Wrapper for Model Context Protocol tools"""
    def __init__(self, mcp_client, tool_name: str, description: str, parameters: List[ToolParameter]):
        self.mcp = mcp_client
        self.name = tool_name
        self.description = description
        self.parameters = parameters

    async def execute(self, **kwargs) -> Any:
        with tracer.start_as_current_span(f"tool.mcp.{self.name}"):
            try:
                result = await self.mcp.call_tool(self.name, kwargs)
                logger.info("Executed MCP tool", tool_name=self.name)
                return result
            except Exception as e:
                logger.error("MCP tool execution failed", tool_name=self.name, error=str(e))
                raise
