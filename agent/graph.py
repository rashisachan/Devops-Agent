from langgraph.graph import StateGraph, END
from agent.nodes import (
    read_issue_node, find_files_node, identify_bug_node,
    generate_fix_node, run_code_node, create_pr_node
)

def should_retry(state: dict) -> str:
    """
    CYCLIC LOGIC: Did the code run successfully?
    If yes → create PR. If no and retries left → try again.
    """
    max_iterations = 3
    iteration = state.get("iteration", 0)
    success = state.get("run_result", {}).get("success", False)
    
    if success:
        return "create_pr"
    elif iteration < max_iterations:
        state["iteration"] = iteration + 1
        return "generate_fix"    # ← loops back!
    else:
        return "create_pr"       # give up, still submit best attempt

def build_graph():
    graph = StateGraph(dict)   # state is just a plain dict
    
    # Add all nodes
    graph.add_node("read_issue",    read_issue_node)
    graph.add_node("find_files",    find_files_node)
    graph.add_node("identify_bug",  identify_bug_node)
    graph.add_node("generate_fix",  generate_fix_node)
    graph.add_node("run_code",      run_code_node)
    graph.add_node("create_pr",     create_pr_node)
    
    # Linear flow
    graph.set_entry_point("read_issue")
    graph.add_edge("read_issue",   "find_files")
    graph.add_edge("find_files",   "identify_bug")
    graph.add_edge("identify_bug", "generate_fix")
    graph.add_edge("generate_fix", "run_code")
    
    # CYCLIC EDGE — this is the magic!
    graph.add_conditional_edges(
        "run_code",         # after running code...
        should_retry,       # call this to decide...
        {
            "generate_fix": "generate_fix",  # loop back
            "create_pr":    "create_pr"      # or finish
        }
    )
    
    graph.add_edge("create_pr", END)
    
    return graph.compile()