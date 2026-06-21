from langgraph.graph import StateGraph, END
from .state import WorkflowState
from .nodes import (
    analyze_requirements,
    create_task_dag,
    assign_tasks,
    monitor_progress,
    handle_failure,
    quality_gate,
    finalize
)

def create_orchestrator_graph() -> StateGraph:
    """
    Creates the LangGraph StateGraph for the orchestrator workflow.
    """
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("analyze_requirements", analyze_requirements)
    workflow.add_node("create_task_dag", create_task_dag)
    workflow.add_node("assign_tasks", assign_tasks)
    workflow.add_node("monitor_progress", monitor_progress)
    workflow.add_node("handle_failure", handle_failure)
    workflow.add_node("quality_gate", quality_gate)
    workflow.add_node("finalize", finalize)

    # Set entry point
    workflow.set_entry_point("analyze_requirements")

    # Add edges
    workflow.add_edge("analyze_requirements", "create_task_dag")
    workflow.add_edge("create_task_dag", "assign_tasks")
    workflow.add_edge("assign_tasks", "monitor_progress")
    
    # Conditional logic for monitoring progress
    workflow.add_conditional_edges(
        "monitor_progress",
        lambda state: "handle_failure" if state["errors"] else ("quality_gate" if state["tasks_completed"] else "monitor_progress"),
        {
            "handle_failure": "handle_failure",
            "quality_gate": "quality_gate",
            "monitor_progress": "monitor_progress"
        }
    )

    workflow.add_edge("handle_failure", "assign_tasks") # Reassign or adjust tasks

    workflow.add_conditional_edges(
        "quality_gate",
        lambda state: "finalize" if state["quality_passed"] else "assign_tasks", # Re-work if quality fails
        {
            "finalize": "finalize",
            "assign_tasks": "assign_tasks"
        }
    )

    workflow.add_edge("finalize", END)

    return workflow.compile()
