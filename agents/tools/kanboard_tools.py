import os
import httpx
import base64
from typing import Dict, Any, List
from langchain_core.tools import tool

KANBOARD_API_URL = os.getenv("KANBOARD_API_URL", "http://kanboard:80/jsonrpc.php")
KANBOARD_API_TOKEN = os.getenv("KANBOARD_API_TOKEN", "")

async def _call_kanboard_api(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to execute JSON-RPC calls against local Kanboard."""
    auth_str = f"jsonrpc:{KANBOARD_API_TOKEN}"
    auth_bytes = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    
    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": params
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(KANBOARD_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            raise Exception(f"Kanboard API Error: {result['error']}")
        return result.get("result")

@tool
async def create_task(title: str, project_id: int = 1, description: str = "") -> int:
    """Invoked by Product Manager to generate technical tasks."""
    params = {
        "title": title,
        "project_id": project_id,
        "description": description
    }
    task_id = await _call_kanboard_api("createTask", params)
    return task_id

@tool
async def move_task(task_id: int, project_id: int = 1, column_id: int = 2) -> bool:
    """Invoked by Engineering nodes to shift state (e.g., Column 2 = In Progress, 3 = Done)."""
    params = {
        "task_id": task_id,
        "project_id": project_id,
        "column_id": column_id
    }
    return await _call_kanboard_api("moveTaskPosition", params)

@tool
async def query_board(project_id: int = 1) -> List[Dict[str, Any]]:
    """Invoked by the Orchestrator to check active status of tickets."""
    params = {"project_id": project_id}
    tasks = await _call_kanboard_api("getAllTasks", params)
    return tasks
