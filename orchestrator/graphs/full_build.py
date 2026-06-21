from typing import Annotated, Dict, Any, List, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 1. Define the Global Workflow State
class WorkflowState(TypedDict):
    # Standard LangGraph conversation history
    messages: Annotated[list, add_messages]
    # Scoped project context tracking
    user_request: str
    current_phase: str
    architecture_spec: Dict[str, Any]
    tasks_list: List[Dict[str, Any]]
    completed_tasks: List[str]
    workspace_diffs: List[str]
    errors_encountered: List[str]
    # New additions for loops and quality scoring
    iteration_count: int
    quality_score: float

# 2. Define Node Wrappers (Delegating to specialized agents)
async def planner_node(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Planner mapping out requirements...")
    return {"current_phase": "planning"}

async def human_approval_1(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Human Approval Gate #1: Planning")
    return {}

async def architect_node(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Architect generating blueprint...")
    return {"current_phase": "architecture"}

async def human_approval_2(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Human Approval Gate #2: Architecture")
    return {}

async def developer_node(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Developer writing code (calls advisors as needed)...")
    # Increment iteration count if returning from QA failure
    current_iter = state.get("iteration_count", 0)
    return {"current_phase": "implementation", "iteration_count": current_iter + 1}

async def reviewer_node(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Reviewer inspecting implementation and architecture compliance...")
    return {"current_phase": "review"}

async def qa_node(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] QA coordinating evaluation service score...")
    # In a real run, this would be set by the evaluation service wrapper
    return {"current_phase": "validation"}

async def release_manager_node(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Release Manager handling git, snapshot, and deployment...")
    return {"current_phase": "release"}

async def human_approval_3(state: WorkflowState) -> Dict[str, Any]:
    print("[Node] Human Approval Gate #3: Release")
    return {}

# 3. Conditional Router Logic
def qa_router(state: WorkflowState) -> Literal["release_manager", "developer"]:
    """Routes based on QA score and iteration count."""
    score = state.get("quality_score", 100.0)
    iterations = state.get("iteration_count", 1)
    
    if score >= 85.0 or iterations >= 3:
        return "release_manager"
    else:
        print(f"[Router] QA score {score} < 85. Iteration {iterations}. Looping back to Developer.")
        return "developer"

# 4. Build the Compiled StateGraph Machine
def create_full_build_graph():
    workflow = StateGraph(WorkflowState)
    
    # Register Core Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("human_approval_1", human_approval_1)
    workflow.add_node("architect", architect_node)
    workflow.add_node("human_approval_2", human_approval_2)
    workflow.add_node("developer", developer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("qa", qa_node)
    workflow.add_node("release_manager", release_manager_node)
    workflow.add_node("human_approval_3", human_approval_3)
    
    # Define Core Structural Edges (Sequential Loop)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "human_approval_1")
    workflow.add_edge("human_approval_1", "architect")
    workflow.add_edge("architect", "human_approval_2")
    workflow.add_edge("human_approval_2", "developer")
    
    # Loop segment
    workflow.add_edge("developer", "reviewer")
    workflow.add_edge("reviewer", "qa")
    
    # Conditional QA Routing
    workflow.add_conditional_edges(
        "qa",
        qa_router,
        {
            "release_manager": "release_manager",
            "developer": "developer"
        }
    )
    
    # Release segment
    workflow.add_edge("release_manager", "human_approval_3")
    workflow.add_edge("human_approval_3", END)
    
    return workflow.compile(interrupt_before=["human_approval_1", "human_approval_2", "human_approval_3"])
