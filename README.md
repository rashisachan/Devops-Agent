# DevOps Agent — Autonomous Bug Fixer

An autonomous DevOps agent that watches your GitHub repository for bug reports and automatically identifies, fixes, and submits a Pull Request — complete with a full Reasoning Trace showing how it thought through the problem.

## What It Does

1. A user opens a GitHub Issue describing a bug
2. The `auto-fix` label is added → triggers a GitHub Actions workflow
3. The agent (powered by LangGraph) clones the repo, reads the issue, and finds the buggy file
4. It generates a fix using **Groq (LLaMA 3.3 70B)**, runs the code to verify it works, and retries up to 3 times if it fails
5. A Pull Request is automatically opened with the fix + a full Reasoning Trace in the PR description

---

## Architecture

GitHub Issue (labeled: auto-fix)
        │
        ▼
GitHub Actions Workflow
        │
        ▼
┌─────────────────────────────────────────┐
│           LangGraph Agent               │
│                                         │
│  read_issue → find_files → identify_bug │
│       ↑                         │       │
│       │                         ▼       │
│  generate_fix ←──────────── run_code    │
│  (retry loop)         pass      │       │
│                                 ▼       │
│                            create_pr    │
└─────────────────────────────────────────┘
        │
        ▼
Pull Request with Fix + Reasoning Trace

### The Cyclic Loop (The Key Feature)

The agent uses a cyclic LangGraph — after generating a fix, it actually runs the code. If it fails, it loops back to `generate_fix` with the error message, up to 3 iterations. This is what makes it truly autonomous rather than just a code generator.


## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | LangGraph (cyclic state graph) |
| LLM | Groq API — LLaMA 3.3 70B Versatile |
| GitHub Integration | PyGithub + GitPython |
| Workflow Trigger | GitHub Actions |
| Frontend | Vanilla HTML/CSS/JS |


## Project Structure

├── .github/
│   └── workflows/
│       └── agent_trigger.yml    # Triggers on issue labeled 'auto-fix'
├── agent/
│   ├── __init__.py
│   ├── graph.py                 # LangGraph state machine with cyclic loop
│   ├── nodes.py                 # All 6 agent nodes
│   ├── tools.py                 # File finder + code runner
│   ├── github_utils.py          # GitHub API helpers
│   └── reasoning_trace.py       # Logging + PR trace formatter
├── main.py                      # Entry point
├── calculator.py                # Demo buggy file
├── index.html                   # Frontend dashboard
├── requirements.txt
└── .env                         # API keys 


## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/rashisachan/Devops-Agent.git
cd Devops-Agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root:

```env
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_pat
GITHUB_REPO=your_username/your_repo
```

- Get a free Groq API key at [console.groq.com](https://console.groq.com)
- Create a GitHub PAT at Settings → Developer Settings → Personal Access Tokens (needs `repo` scope)

### 4. Add GitHub Secrets

Go to your repo → **Settings → Secrets and Variables → Actions** and add:

| Secret | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |

> `GITHUB_TOKEN` is provided automatically by GitHub Actions.

### 5. Enable workflow permissions

Go to Settings → Actions → General → Workflow Permissions:
- Select Read and write permissions
- Check Allow GitHub Actions to create and approve pull requests


## Usage

### Trigger the agent

1. Open a new Issue in your repo describing the bug
2. Add the `auto-fix` label
3. The agent triggers automatically via GitHub Actions

### Run locally

```bash
python main.py <issue_number>
# e.g. python main.py 42
```

### Use the frontend dashboard

Open `index.html` in a browser, enter your repo name and GitHub token, and use the form to submit bug reports and view the agent's reasoning trace.

---

## Reasoning Trace

Every PR created by the agent includes a full reasoning trace in the PR description, for example:

```
## Agent Reasoning Trace

### Step 1: Read Issue
- Details: Issue #13: add() function subtracts instead of adds

### Step 2: Clone Repo
- Details: Cloning repository locally...

### Step 3: Find Files
- Details: Found 5 candidate files
- Result: ['calculator.py', 'main.py', ...]

### Step 4: Identify Bug
- Details: LLM identified bug in: calculator.py
- Result: The add function subtracts instead of adding

### Step 5: Generate Fix
- Details: Iteration 1 — LLM generated a fix

### Step 6: Run Code
- Details: Executed calculator.py
- Result:  PASSED — stdout: 5, 12

### Step 7: Create PR
- Details: Pushing fix to branch: auto-fix/issue-13


## Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph) — cyclic agent framework
- [Groq](https://groq.com) — fast LLM inference
- [PyGithub](https://github.com/PyGithub/PyGithub) — GitHub API client
