import asyncio
from typing import Dict, Any
from agents.orchestrator.graph import create_orchestrator_graph

class OrchestrationEngine:
    """
    Main orchestration engine that coordinates all agents and executes LangGraph workflows.
    """
    def __init__(self):
        self.graph = create_orchestrator_graph()

    async def run_workflow(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a LangGraph workflow with the provided initial state.
        """
        final_state = await self.graph.ainvoke(initial_state)
        return final_state
