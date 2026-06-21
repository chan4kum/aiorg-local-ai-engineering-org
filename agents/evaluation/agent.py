from agents.base.agent import AgentBase
from .prompts import EVAL_SYSTEM_PROMPT
from .tools import EVAL_TOOLS

class EvaluationAgent(AgentBase):
    """
    Evaluation Agent responsible for benchmarking models, pipelines, and agents.
    """
    def __init__(self):
        super().__init__(
            name="Evaluation",
            role="Evaluation Specialist",
            system_prompt=EVAL_SYSTEM_PROMPT,
            tools=EVAL_TOOLS
        )
