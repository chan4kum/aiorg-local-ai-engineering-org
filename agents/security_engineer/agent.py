from agents.base.agent import AgentBase
from .prompts import SECURITY_SYSTEM_PROMPT
from .tools import SECURITY_TOOLS

class SecurityEngineerAgent(AgentBase):
    """
    Security Engineer Agent responsible for threat modeling, vulnerability scanning, and code review.
    """
    def __init__(self):
        super().__init__(
            name="SecurityEngineer",
            role="Security Engineer",
            system_prompt=SECURITY_SYSTEM_PROMPT,
            tools=SECURITY_TOOLS
        )
