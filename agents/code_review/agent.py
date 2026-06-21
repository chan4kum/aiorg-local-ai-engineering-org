from agents.base.agent import AgentBase
from .prompts import REVIEW_SYSTEM_PROMPT
from .tools import REVIEW_TOOLS

class CodeReviewAgent(AgentBase):
    """
    Code Review Agent responsible for ensuring code quality, style, and correctness.
    """
    def __init__(self):
        super().__init__(
            name="CodeReviewer",
            role="Code Reviewer",
            system_prompt=REVIEW_SYSTEM_PROMPT,
            tools=REVIEW_TOOLS
        )
