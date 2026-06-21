import asyncio
from typing import Dict, Any
from agents.orchestrator.graph import create_orchestrator_graph
from orchestrator.state.checkpointer import CheckpointerFactory

class OrchestrationEngine:
    """
    Main orchestration engine that coordinates all agents and executes LangGraph workflows.
    """
    def __init__(self):
        self.graph = create_orchestrator_graph()

    async def run_workflow(self, initial_state: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a LangGraph workflow with the provided initial state.
        """
        checkpointer = await CheckpointerFactory.get_checkpointer()
        if config is None:
            config = {"configurable": {"thread_id": "default"}}
            
        # Re-compile with checkpointer (since create_orchestrator_graph compiles without it)
        # Note: In a real scenario, create_orchestrator_graph() might take the checkpointer directly.
        # However, since StateGraph.compile() can take it:
        self.graph.checkpointer = checkpointer
        
        final_state = await self.graph.ainvoke(initial_state, config=config)
        return final_state
