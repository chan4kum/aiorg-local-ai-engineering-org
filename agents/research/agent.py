from agents.base.agent import AgentBase
from .prompts import RESEARCH_SYSTEM_PROMPT
from .tools import RESEARCH_TOOLS

class ResearchAgent(AgentBase):
    """
    Research Agent responsible for gathering information, reading documentation, and analyzing tools.
    """
    def __init__(self):
        super().__init__(
            name="Research",
            role="Research Specialist",
            system_prompt=RESEARCH_SYSTEM_PROMPT,
            tools=RESEARCH_TOOLS
        )
