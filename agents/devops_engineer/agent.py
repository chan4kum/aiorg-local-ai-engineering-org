from agents.base.agent import AgentBase
from .prompts import DEVOPS_SYSTEM_PROMPT
from .tools import DEVOPS_TOOLS

class DevOpsEngineerAgent(AgentBase):
    """
    DevOps Engineer Agent responsible for CI/CD pipelines, infrastructure as code, and deployment.
    """
    def __init__(self):
        super().__init__(
            name="DevOpsEngineer",
            role="DevOps Engineer",
            system_prompt=DEVOPS_SYSTEM_PROMPT,
            tools=DEVOPS_TOOLS
        )
