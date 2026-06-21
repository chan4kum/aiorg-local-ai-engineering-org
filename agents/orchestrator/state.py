from typing import TypedDict, List, Dict, Any, Optional

class WorkflowState(TypedDict):
    """
    Represents the state of the orchestrator workflow in LangGraph.
    """
    requirements: str
    status: str
    dag: Dict[str, Any]
    tasks_completed: bool
    errors: List[str]
    quality_passed: bool
    context: Dict[str, Any]
    artifacts: List[str]
