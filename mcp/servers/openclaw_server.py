import asyncio
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any

# Create the MCP server for OpenClaw
mcp = FastMCP("OpenClaw")

OPENCLAW_API_URL = "http://localhost:8000/api/v1"

@mcp.tool()
async def create_openclaw_project(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Creates a new project/workspace in the OpenClaw local AI Engineering organization.
    
    Args:
        name: The name of the project.
        description: A brief description of what the AI team should build.
        
    Returns:
        JSON response containing the project_id.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OPENCLAW_API_URL}/projects",
                json={"name": name, "description": description},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def start_openclaw_workflow(project_id: str) -> Dict[str, Any]:
    """
    Starts the multi-agent workflow for a specific OpenClaw project.
    The Orchestrator agent will take over and delegate tasks to the engineering team.
    
    Args:
        project_id: The ID of the project to start.
        
    Returns:
        JSON response with the workflow status.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OPENCLAW_API_URL}/projects/{project_id}/start",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def get_openclaw_project_status(project_id: str) -> Dict[str, Any]:
    """
    Retrieves the current status and state of an OpenClaw project.
    
    Args:
        project_id: The ID of the project.
        
    Returns:
        JSON response with project details.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{OPENCLAW_API_URL}/projects/{project_id}",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Start the MCP server using standard I/O (required for MCP clients like Cursor/Claude Desktop)
    mcp.run()
