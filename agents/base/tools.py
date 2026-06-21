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
    def __init__(self, mcp_server_name: str, mcp_container_name: str, tool_name: str, description: str, parameters: List[ToolParameter]):
        from services.mcp_client_manager import mcp_manager
        self.mcp_manager = mcp_manager
        self.server_name = mcp_server_name
        self.container_name = mcp_container_name
        self.name = tool_name
        self.description = description
        self.parameters = parameters

    async def execute(self, **kwargs) -> Any:
        with tracer.start_as_current_span(f"tool.mcp.{self.name}"):
            try:
                # Dispatch the call via the central manager
                result = await self.mcp_manager.call_tool(
                    server_name=self.server_name,
                    container_name=self.container_name,
                    tool_name=self.name,
                    arguments=kwargs
                )
                logger.info("Executed MCP tool", tool_name=self.name, server_name=self.server_name)
                return result
            except Exception as e:
                logger.error("MCP tool execution failed", tool_name=self.name, error=str(e))
                raise
