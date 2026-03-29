from langgraph.graph import StateGraph, END
from agent.nodes import (
    read_issue_node, find_files_node, identify_bug_node,
    generate_fix_node, run_code_node, create_pr_node
)

MAX_ITERATIONS = 3

def should_retry(state: dict) -> str:
    """
    CYCLIC LOGIC: Route only — do NOT mutate state here.
    """
    iteration = state.get("iteration", 0)
    success = state.get("run_result", {}).get("success", False)

    if success:
        return "create_pr"
    elif iteration < MAX_ITERATIONS:
        return "generate_fix"   # loop back
    else:
        return "create_pr"      # give up, submit best attempt

def generate_fix_with_increment(state: dict) -> dict:
    """
    ✅ FIX: Increment iteration count HERE (in a node), not in the router.
    Then call the actual generate_fix_node logic.
    """
    state["iteration"] = state.get("iteration", 0) + 1
    return generate_fix_node(state)

def build_graph():
    graph = StateGraph(dict)

    graph.add_node("read_issue",   read_issue_node)
    graph.add_node("find_files",   find_files_node)
    graph.add_node("identify_bug", identify_bug_node)
    graph.add_node("generate_fix", generate_fix_with_increment)  # ✅ wrapped version
    graph.add_node("run_code",     run_code_node)
    graph.add_node("create_pr",    create_pr_node)

    graph.set_entry_point("read_issue")
    graph.add_edge("read_issue",   "find_files")
    graph.add_edge("find_files",   "identify_bug")
    graph.add_edge("identify_bug", "generate_fix")
    graph.add_edge("generate_fix", "run_code")

    graph.add_conditional_edges(
        "run_code",
        should_retry,
        {
            "generate_fix": "generate_fix",
            "create_pr":    "create_pr"
        }
    )

    graph.add_edge("create_pr", END)
    return graph.compile()