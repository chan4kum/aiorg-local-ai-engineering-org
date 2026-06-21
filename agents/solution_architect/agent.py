from agents.base.agent import AgentBase
from .prompts import SA_SYSTEM_PROMPT
from .tools import SA_TOOLS

class SolutionArchitectAgent(AgentBase):
    """
    Solution Architect Agent responsible for system design, component selection,
    and technical strategy.
    """
    def __init__(self):
        super().__init__(
            name="SolutionArchitect",
            role="Lead Solution Architect",
            system_prompt=SA_SYSTEM_PROMPT,
            tools=SA_TOOLS
        )
