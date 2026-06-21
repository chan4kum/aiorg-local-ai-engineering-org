from agents.base.agent import AgentBase
from .prompts import DOCS_SYSTEM_PROMPT
from .tools import DOCS_TOOLS

class DocumentationAgent(AgentBase):
    """
    Documentation Agent responsible for API docs, READMEs, and user guides.
    """
    def __init__(self):
        super().__init__(
            name="Documentation",
            role="Technical Writer",
            system_prompt=DOCS_SYSTEM_PROMPT,
            tools=DOCS_TOOLS
        )
