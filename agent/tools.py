import os, subprocess

def find_relevant_files(repo_path: str, issue_text: str) -> list[str]:
    """
    Simple file finder — looks for .py files mentioned in issue
    or searches for keywords from issue body.
    """
    py_files = []
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden folders like .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith(".py"):
                rel_path = os.path.relpath(
                    os.path.join(root, f), repo_path
                )
                py_files.append(rel_path)
    
    # Score files by how many issue words appear in their name/path
    issue_words = set(issue_text.lower().split())
    scored = []
    for fp in py_files:
        score = sum(1 for w in issue_words if w in fp.lower())
        scored.append((score, fp))
    
    scored.sort(reverse=True)
    # Return top 5 candidates
    return [fp for _, fp in scored[:5]]

def read_file(repo_path: str, file_path: str) -> str:
    """Read file content."""
    full = os.path.join(repo_path, file_path)
    with open(full, "r") as f:
        return f.read()

def run_code(repo_path: str, file_path: str) -> dict:
    """
    Run a Python file and capture stdout + stderr.
    Returns success bool + output.
    """
    result = subprocess.run(
        ["python", file_path],
        capture_output=True,
        text=True,
        cwd=repo_path,
        timeout=30      # kill if runs >30s
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }