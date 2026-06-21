import asyncio
from contextlib import asynccontextmanager
from mcp import StdioServerParameters

@asynccontextmanager
async def stdio_client(server_params: StdioServerParameters):
    """Stub stdio client that yields dummy read/write streams.
    This mimics the real MCP stdio client without launching a subprocess.
    """
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
        pass
