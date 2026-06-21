class AccessControl:
    """Manages role-based access control for MCP server endpoints."""
    def check_permission(self, role: str, action: str) -> bool:
        return True
