from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Dict

from backend.dependencies import get_db_session
from backend.database.repositories.agent_run_repo import AgentRunRepository

# Suppose models for agents exist in models.responses
# from backend.models.responses import AgentResponse, AgentRunResponse

router = APIRouter()

@router.get("")
async def list_agents():
    # Example generic implementation since agent repository is usually static or configured
    return [{"id": "agent-1", "name": "Code Writer Agent"}, {"id": "agent-2", "name": "Reviewer Agent"}]

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    return {"id": agent_id, "name": f"Agent {agent_id}"}

@router.get("/{agent_id}/runs")
async def list_agent_runs(agent_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = AgentRunRepository(session)
    runs = await repo.get_all(agent_id=agent_id)
    return runs

@router.post("/{agent_id}/config")
async def update_agent_config(agent_id: str, config: Dict[str, Any]):
    # Typically config is saved in DB or sent to EventBus
    return {"agent_id": agent_id, "config": config, "status": "updated"}
