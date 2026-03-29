import os, sys
from dotenv import load_dotenv
from agent.graph import build_graph
from agent.github_utils import get_issue, create_test_pr
from agent.reasoning_trace import ReasoningTrace

load_dotenv()

def run_agent(issue_number: int):
    print(f"\n🤖 DevOps Agent starting for Issue #{issue_number}")
    
    # Get the issue from GitHub
    issue = get_issue(issue_number)
    trace = ReasoningTrace()
    
    # Initial state for the agent
    initial_state = {
        "issue": issue,
        "trace": trace,
        "iteration": 0,
        "run_result": {},
        "last_error": "",
        "fixed_code": "",
        "buggy_file": "",
    }
    
    # Build and run the agent graph
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    
    # Get PR URL from agent
    pr_url = final_state.get('pr_url')
    
    # If no PR is generated, create a dummy test PR for workflow verification
    if not pr_url:
        print("\n⚠️ No bug detected. Creating a test PR for workflow...")
        pr_url = create_test_pr(issue_number)
    
    print(f"\n✅ Done! PR created: {pr_url}")
    trace.save_to_file("reasoning_trace.md")

if __name__ == "__main__":
    issue_number = int(sys.argv[1])   # pass issue number as argument
    run_agent(issue_number)