from langgraph.graph import StateGraph, END
from agents.orchestrator.state import WorkflowState

def create_incremental_build_graph() -> StateGraph:
    """Incremental project build workflow for bug fixes or features."""
    workflow = StateGraph(WorkflowState)
    workflow.add_node("start_incremental", lambda state: state)
    workflow.set_entry_point("start_incremental")
    workflow.add_edge("start_incremental", END)
    return workflow.compile()
