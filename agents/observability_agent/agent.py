from agents.base.agent import AgentBase
from .prompts import OBS_SYSTEM_PROMPT
from .tools import OBS_TOOLS

class ObservabilityAgent(AgentBase):
    """
    Observability Agent responsible for monitoring, logging, and tracing.
    """
    def __init__(self):
        super().__init__(
            name="Observability",
            role="Observability Engineer",
            system_prompt=OBS_SYSTEM_PROMPT,
            tools=OBS_TOOLS
        )
