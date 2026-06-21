class MCPServerRegistry:
    """Registry for MCP Servers."""
    def __init__(self):
        self.servers = {}

    def register(self, name: str, server_cls):
        self.servers[name] = server_cls
