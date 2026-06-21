from agents.base.agent import AgentBase
from .prompts import BACKEND_SYSTEM_PROMPT
from .tools import BACKEND_TOOLS

class BackendEngineerAgent(AgentBase):
    """
    Backend Engineer Agent responsible for developing server-side logic, APIs, and database schemas.
    """
    def __init__(self):
        super().__init__(
            name="BackendEngineer",
            role="Backend Engineer",
            system_prompt=BACKEND_SYSTEM_PROMPT,
            tools=BACKEND_TOOLS
        )
