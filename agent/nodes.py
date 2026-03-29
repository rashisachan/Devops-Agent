import os
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from agent.tools import find_relevant_files, read_file, run_code
from agent.github_utils import clone_repo, commit_and_push, create_pull_request

llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

def read_issue_node(state: dict) -> dict:
    trace = state["trace"]
    trace.add("Read Issue", f"Issue #{state['issue']['number']}: {state['issue']['title']}")
    state["issue_summary"] = f"{state['issue']['title']}\n{state['issue']['body']}"
    return state

def find_files_node(state: dict) -> dict:
    trace = state["trace"]
    trace.add("Clone Repo", "Cloning repository locally...")
    clone_repo("./cloned_repo")
    state["repo_path"] = "./cloned_repo"
    candidates = find_relevant_files(state["repo_path"], state["issue_summary"])
    state["candidate_files"] = candidates
    trace.add("Find Files", f"Found {len(candidates)} candidate files", str(candidates))
    return state

def identify_bug_node(state: dict) -> dict:
    trace = state["trace"]
    file_contents = {}
    for fp in state["candidate_files"]:
        try:
            file_contents[fp] = read_file(state["repo_path"], fp)
        except:
            pass

    files_text = "\n\n".join(
        [f"### {fp}\n```python\n{content}\n```" for fp, content in file_contents.items()]
    )

    messages = [
        SystemMessage(content="""You are a code debugging expert.
Given a bug report and file contents, identify:
1. Which file contains the bug (exact filename)
2. What the bug is

Reply in this exact format:
FILE: filename.py
BUG: one sentence description of the bug"""),
        HumanMessage(content=f"""Bug Report:
{state['issue_summary']}

Files:
{files_text}""")
    ]

    response = llm.invoke(messages)
    text = response.content

    file_line = [l for l in text.split("\n") if l.startswith("FILE:")][0]
    bug_line  = [l for l in text.split("\n") if l.startswith("BUG:")][0]

    state["buggy_file"] = file_line.replace("FILE:", "").strip()
    state["bug_description"] = bug_line.replace("BUG:", "").strip()

    trace.add("Identify Bug", f"LLM identified bug in: {state['buggy_file']}", state["bug_description"])
    return state

def generate_fix_node(state: dict) -> dict:
    trace = state["trace"]
    iteration = state.get("iteration", 0)
    current_code = read_file(state["repo_path"], state["buggy_file"])
    previous_error = state.get("last_error", "No previous attempt")

    messages = [
        SystemMessage(content="""You are a Python bug fixer.
Return ONLY the complete fixed Python file content.
No explanations, no markdown fences, just the raw Python code."""),
        HumanMessage(content=f"""Bug report: {state['issue_summary']}
Bug identified: {state['bug_description']}
Iteration: {iteration} (0 = first try)
Previous error: {previous_error}

Current code in {state['buggy_file']}:
{current_code}

Return the complete fixed file:""")
    ]

    response = llm.invoke(messages)
    state["fixed_code"] = response.content.strip()

    trace.add("Generate Fix",
              f"Iteration {iteration} — LLM generated a fix",
              f"Fixed code length: {len(state['fixed_code'])} chars")
    return state

def run_code_node(state: dict) -> dict:
    trace = state["trace"]
    full_path = os.path.join(state["repo_path"], state["buggy_file"])

    # ✅ FIX: Read original BEFORE writing the fix
    original = read_file(state["repo_path"], state["buggy_file"])

    with open(full_path, "w") as f:
        f.write(state["fixed_code"])

    result = run_code(state["repo_path"], state["buggy_file"])
    state["run_result"] = result
    state["last_error"] = result["stderr"] if not result["success"] else ""

    status = "✅ PASSED" if result["success"] else "❌ FAILED"
    trace.add("Run Code",
              f"Executed {state['buggy_file']}",
              f"{status}\nstdout: {result['stdout'][:200]}\nstderr: {result['stderr'][:200]}")

    # Restore original if fix failed
    if not result["success"]:
        with open(full_path, "w") as f:
            f.write(original)

    return state

def create_pr_node(state: dict) -> dict:
    trace = state["trace"]
    issue_num = state["issue"]["number"]
    branch = f"auto-fix/issue-{issue_num}"

    trace.add("Create PR", f"Pushing fix to branch: {branch}")

    commit_and_push(state["repo_path"], branch, state["buggy_file"], state["fixed_code"])

    pr_body = f"{state['bug_description']}\n\n{trace.format_for_pr()}"
    pr_url = create_pull_request(branch, pr_body, issue_num)

    state["pr_url"] = pr_url
    trace.add("PR Created", "Pull Request opened!", pr_url)
    return state