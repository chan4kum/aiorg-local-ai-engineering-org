from agents.base.agent import AgentBase
from .prompts import PM_SYSTEM_PROMPT
from .tools import PM_TOOLS

class ProductManagerAgent(AgentBase):
    """
    Product Manager Agent responsible for defining PRDs, user stories, and feature scopes.
    """
    def __init__(self):
        super().__init__(
            name="ProductManager",
            role="Product Manager",
            system_prompt=PM_SYSTEM_PROMPT,
            tools=PM_TOOLS
        )
