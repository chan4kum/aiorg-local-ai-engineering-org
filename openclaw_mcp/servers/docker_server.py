import os
import sys
import json
import docker
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Docker MCP Server", description="Manages local Docker containers with strict security limits.")

# Initialize Docker Client
# Uses DOCKER_HOST env var, or falls back to local socket
client = docker.from_env()

@mcp.tool()
def docker_list_containers() -> str:
    """Lists running and stopped containers, returning their status, health, image, and ports."""
    try:
        containers = client.containers.list(all=True)
        results = []
        for c in containers:
            health = "unknown"
            if "Health" in c.attrs.get("State", {}):
                health = c.attrs["State"]["Health"]["Status"]
            
            results.append({
                "name": c.name,
                "status": c.status,
                "health": health,
                "uptime": c.attrs.get("State", {}).get("StartedAt"),
                "image": c.image.tags[0] if c.image.tags else c.image.id,
                "ports": c.attrs.get("NetworkSettings", {}).get("Ports", {})
            })
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error connecting to Docker: {str(e)}"

@mcp.tool()
def docker_get_logs(container_name: str, tail: int = 100, keyword: str = None) -> str:
    """Retrieves logs from a container, strictly limited to the last `tail` lines (max 500)."""
    tail_limit = min(tail, 500)
    try:
        container = client.containers.get(container_name)
        logs = container.logs(tail=tail_limit).decode('utf-8').splitlines()
        
        if keyword:
            logs = [line for line in logs if keyword.lower() in line.lower()]
            
        return "\n".join(logs) if logs else f"No logs found matching '{keyword}'."
    except Exception as e:
        return f"Error retrieving logs for {container_name}: {str(e)}"

@mcp.tool()
def docker_execute_readonly(container_name: str, command: str) -> str:
    """Executes a benign read-only command inside a container (e.g., ls, cat, ps)."""
    # Restrict dangerous keywords
    dangerous = ["rm", "dd", "chmod", "chown", "mv", "cp", ">", ">>", "apt", "apk", "yum"]
    if any(k in command.split() for k in dangerous):
        return f"SECURITY_ERROR: Command rejected. Admin access required for destructive operation: {command}"
    
    try:
        container = client.containers.get(container_name)
        result = container.exec_run(command)
        output = result.output.decode('utf-8')
        return output[:4000] # Cap output to prevent context window overflow
    except Exception as e:
        return f"Error executing command: {str(e)}"

@mcp.tool()
def docker_execute_admin(container_name: str, command: str) -> str:
    """Executes a privileged admin command inside a container. (Requires Human Approval)"""
    return f"HUMAN_APPROVAL_REQUIRED: Halting execution. Admin command '{command}' in '{container_name}' requires explicit user confirmation via the OpenClaw orchestrator."

@mcp.tool()
def docker_manage(container_name: str, action: str) -> str:
    """Manages a container state (allowed: start, stop, restart). Destructive actions require human approval."""
    allowed_actions = ["start", "stop", "restart"]
    
    if action not in allowed_actions:
        return f"HUMAN_APPROVAL_REQUIRED: Action '{action}' on '{container_name}' is potentially destructive and requires explicit user confirmation."
    
    try:
        container = client.containers.get(container_name)
        if action == "start":
            container.start()
        elif action == "stop":
            container.stop()
        elif action == "restart":
            container.restart()
            
        return f"Success: Container '{container_name}' has been {action}ed."
    except Exception as e:
        return f"Error managing container '{container_name}': {str(e)}"

if __name__ == "__main__":
    # Support dual-transport (SSE for network, stdio for IDEs)
    # Check if SSE is requested via environment variable or args
    use_sse = os.environ.get("MCP_TRANSPORT") == "sse" or "--sse" in sys.argv
    
    if use_sse:
        print("[Docker MCP] Starting SSE transport on port 8080...", file=sys.stderr)
        # Assuming the newer fastmcp interface supports host/port directly
        mcp.run(transport="sse", port=8080)
    else:
        # Default to stdio for Cursor/Claude Desktop integration
        mcp.run(transport="stdio")
