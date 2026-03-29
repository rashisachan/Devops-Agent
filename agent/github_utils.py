import os, git
from github import Github
from dotenv import load_dotenv

load_dotenv()

gh = Github(os.getenv("GITHUB_TOKEN"))

def get_issue(issue_number: int):
    """Fetch issue title + body from GitHub."""
    repo = gh.get_repo(os.getenv("GITHUB_REPO"))
    issue = repo.get_issue(number=issue_number)
    return {
        "title": issue.title,
        "body": issue.body,
        "number": issue_number
    }

def clone_repo(clone_path="./cloned_repo"):
    """Clone the target repo locally."""
    repo_name = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://{token}@github.com/{repo_name}.git"
    if os.path.exists(clone_path):
        return git.Repo(clone_path)   # already cloned
    return git.Repo.clone_from(url, clone_path)

def create_pull_request(branch_name: str, fix_description: str, 
                         issue_number: int):
    """Push branch and open a PR."""
    repo = gh.get_repo(os.getenv("GITHUB_REPO"))
    pr = repo.create_pull(
        title=f"🤖 Auto-fix for Issue #{issue_number}",
        body=f"## Agent Fix\n\n{fix_description}\n\nCloses #{issue_number}",
        head=branch_name,
        base="main"
    )
    return pr.html_url

def commit_and_push(repo_path: str, branch_name: str, 
                     file_path: str, new_content: str):
    """Commit the fix and push to a new branch."""
    repo = git.Repo(repo_path)
    
    # Write fixed file
    full_path = os.path.join(repo_path, file_path)
    with open(full_path, "w") as f:
        f.write(new_content)
    
    # Create branch, commit, push
    repo.git.checkout("-b", branch_name)
    repo.index.add([file_path])
    repo.index.commit(f"🤖 Auto-fix: {branch_name}")
    origin = repo.remote(name="origin")
    origin.push(branch_name)