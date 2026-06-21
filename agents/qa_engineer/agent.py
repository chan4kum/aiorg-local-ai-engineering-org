from agents.base.agent import AgentBase
from .prompts import QA_SYSTEM_PROMPT
from .tools import QA_TOOLS

class QAEngineerAgent(AgentBase):
    """
    QA Engineer Agent responsible for test plan creation, test execution, and quality metrics.
    """
    def __init__(self):
        super().__init__(
            name="QAEngineer",
            role="QA Engineer",
            system_prompt=QA_SYSTEM_PROMPT,
            tools=QA_TOOLS
        )
