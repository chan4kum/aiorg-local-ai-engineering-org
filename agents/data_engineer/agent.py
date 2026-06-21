from agents.base.agent import AgentBase
from .prompts import DATA_SYSTEM_PROMPT
from .tools import DATA_TOOLS

class DataEngineerAgent(AgentBase):
    """
    Data Engineer Agent responsible for data pipelines, ETL, and vector database management.
    """
    def __init__(self):
        super().__init__(
            name="DataEngineer",
            role="Data Engineer",
            system_prompt=DATA_SYSTEM_PROMPT,
            tools=DATA_TOOLS
        )
