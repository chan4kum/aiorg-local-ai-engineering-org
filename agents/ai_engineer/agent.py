from agents.base.agent import AgentBase
from .prompts import AI_SYSTEM_PROMPT
from .tools import AI_TOOLS

class AIEngineerAgent(AgentBase):
    """
    AI Engineer Agent responsible for implementing LLM pipelines, prompt engineering, and model fine-tuning.
    """
    def __init__(self):
        super().__init__(
            name="AIEngineer",
            role="AI Engineer",
            system_prompt=AI_SYSTEM_PROMPT,
            tools=AI_TOOLS
        )
