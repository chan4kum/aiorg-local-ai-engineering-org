from agents.base.agent import AgentBase
from .prompts import FRONTEND_SYSTEM_PROMPT
from .tools import FRONTEND_TOOLS

class FrontendEngineerAgent(AgentBase):
    """
    Frontend Engineer Agent responsible for developing user interfaces and integrating with APIs.
    """
    def __init__(self):
        super().__init__(
            name="FrontendEngineer",
            role="Frontend Engineer",
            system_prompt=FRONTEND_SYSTEM_PROMPT,
            tools=FRONTEND_TOOLS
        )
