import os, sys
from dotenv import load_dotenv
from agent.graph import build_graph
from agent.github_utils import get_issue
from agent.reasoning_trace import ReasoningTrace

load_dotenv()

def run_agent(issue_number: int):
    print(f"\n🤖 DevOps Agent starting for Issue #{issue_number}")
    
    issue = get_issue(issue_number)
    trace = ReasoningTrace()
    
    initial_state = {
        "issue": issue,
        "trace": trace,
        "iteration": 0,
        "run_result": {},
        "last_error": "",
        "fixed_code": "",
        "buggy_file": "",
    }
    
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    
    print(f"\n✅ Done! PR created: {final_state.get('pr_url', 'N/A')}")
    trace.save_to_file("reasoning_trace.md")

if __name__ == "__main__":
    issue_number = int(sys.argv[1])   # pass issue number as argument
import os, sys
from dotenv import load_dotenv
from agent.graph import build_graph
from agent.github_utils import get_issue
from agent.reasoning_trace import ReasoningTrace

load_dotenv()

def run_agent(issue_number: int):
    print(f"\n🤖 DevOps Agent starting for Issue #{issue_number}")
    
    issue = get_issue(issue_number)
    trace = ReasoningTrace()
    
    initial_state = {
        "issue": issue,
        "trace": trace,
        "iteration": 0,
        "run_result": {},
        "last_error": "",
        "fixed_code": "",
        "buggy_file": "",
    }
    
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    
    print(f"\n✅ Done! PR created: {final_state.get('pr_url', 'N/A')}")
    trace.save_to_file("reasoning_trace.md")

if __name__ == "__main__":
    issue_number = int(sys.argv[1])   # pass issue number as argument
    run_agent(issue_number)