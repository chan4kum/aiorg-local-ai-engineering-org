# mcp stub package to satisfy imports

# mcp/__init__.py
class ClientSession:
    """A minimal stub for MCP ClientSession.
    It accepts read/write streams but does not perform any real communication.
    """
    def __init__(self, read_stream=None, write_stream=None):
        self.read_stream = read_stream
        self.write_stream = write_stream

    async def __aenter__(self):
        # No real setup needed
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def initialize(self):
        # Stub does nothing
        return None

    async def list_tools(self):
        # Return an empty tool list structure compatible with usage
        class ToolsResult:
            def __init__(self):
                self.tools = []
        return ToolsResult()

    async def call_tool(self, tool_name, arguments):
        # Stub raises NotImplementedError to make clear it's a placeholder
        raise NotImplementedError("MCP stub does not implement tool calls")

class StdioServerParameters:
    """Simple container for command and args used by stdio client stub."""
    def __init__(self, command: str, args: list):
        self.command = command
        self.args = args

# mcp/client/__init__.py (empty, just to make package)

# mcp/client/stdio.py
import asyncio
from contextlib import asynccontextmanager
from mcp import StdioServerParameters

@asynccontextmanager
async def stdio_client(server_params: StdioServerParameters):
    """Stub stdio client that pretends to open a subprocess.
    It yields placeholder read and write stream objects.
    """
    # In a real implementation, you would launch the process here.
    # For the stub we just provide dummy objects.
    class DummyStream:
        async def read(self, n=-1):
            return b""
        async def write(self, data):
            return None
        async def drain(self):
            return None
        async def close(self):
            return None
    read_stream = DummyStream()
    write_stream = DummyStream()
    try:
        yield read_stream, write_stream
    finally:
        # No real resources to clean up
        pass
