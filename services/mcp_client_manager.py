import asyncio
from typing import Dict, Any, List, Optional
import structlog
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from opentelemetry import trace

logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

class MCPClientManager:
    """Singleton manager for MCP server connections over stdio via docker exec."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPClientManager, cls).__new__(cls)
            cls._instance.sessions = {}
            cls._instance.contexts = {}
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def get_session(self, server_name: str, container_name: str, command: str = "node", args: List[str] = None) -> ClientSession:
        """Get or initialize a connection to an MCP server via docker exec."""
        if not args:
            args = ["build/index.js"]

        async with self._lock:
            if server_name in self.sessions:
                return self.sessions[server_name]

            logger.info("Initializing MCP connection", server_name=server_name, container=container_name)
            
            # Use docker exec -i to communicate with the isolated MCP container over stdio
            server_params = StdioServerParameters(
                command="docker",
                args=["exec", "-i", container_name, command] + args
            )

            # Enter the stdio client context
            stdio_ctx = stdio_client(server_params)
            read_stream, write_stream = await stdio_ctx.__aenter__()
            
            # Initialize the MCP session
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            
            # Initialize the protocol
            await session.initialize()
            
            self.contexts[server_name] = (stdio_ctx, session)
            self.sessions[server_name] = session
            logger.info("MCP connection established", server_name=server_name)
            
            return session

    async def list_tools(self, server_name: str, container_name: str, command: str = "node", args: List[str] = None) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        with tracer.start_as_current_span(f"mcp.list_tools.{server_name}"):
            session = await self.get_session(server_name, container_name, command, args)
            result = await session.list_tools()
            return [{"name": t.name, "description": t.description, "inputSchema": t.inputSchema} for t in result.tools]

    async def call_tool(self, server_name: str, container_name: str, tool_name: str, arguments: Dict[str, Any], command: str = "node", args: List[str] = None) -> Any:
        """Call a specific tool on the MCP server."""
        with tracer.start_as_current_span(f"mcp.call_tool.{server_name}.{tool_name}"):
            session = await self.get_session(server_name, container_name, command, args)
            try:
                result = await session.call_tool(tool_name, arguments)
                return result.content
            except Exception as e:
                logger.error("Failed to execute MCP tool", server_name=server_name, tool=tool_name, error=str(e))
                raise

    async def cleanup(self):
        """Close all active MCP sessions."""
        for server_name, (stdio_ctx, session) in self.contexts.items():
            logger.info("Closing MCP connection", server_name=server_name)
            try:
                await session.__aexit__(None, None, None)
                await stdio_ctx.__aexit__(None, None, None)
            except Exception as e:
                logger.error("Error closing MCP connection", server_name=server_name, error=str(e))
        self.sessions.clear()
        self.contexts.clear()

# Global singleton
mcp_manager = MCPClientManager()
