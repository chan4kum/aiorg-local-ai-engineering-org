from agents.base.agent import AgentBase
from .prompts import ORCHESTRATOR_SYSTEM_PROMPT
from .tools import ORCHESTRATOR_TOOLS
from typing import Dict, Any

class OrchestratorAgent(AgentBase):
    """
    Orchestrator Agent responsible for managing the AI engineering workflow,
    creating task DAGs, and delegating work to other specialized agents.
    """
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            role="Lead AI Engineering Orchestrator",
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=ORCHESTRATOR_TOOLS
        )

    async def orchestrate_workflow(self, requirements: str, initial_context: Dict[str, Any]) -> str:
        """
        Entry point for orchestrating a complex workflow.
        """
        # In a real setup, this might invoke the LangGraph workflow.
        return await self.execute(task=f"Orchestrate workflow for: {requirements}", context=initial_context)
