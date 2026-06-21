from langchain_core.tools import tool
import httpx
import os

@tool
def review_github_pr(repo_full_name: str, pr_number: int) -> str:
    """
    Review a GitHub Pull Request.
    Fetches the PR diff and returns it for analysis.
    """
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"token {token}" if token else ""
    }
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Failed to fetch PR diff: {e}"

@tool
def comment_on_github_pr(repo_full_name: str, pr_number: int, comment_body: str) -> str:
    """
    Post a review comment on a GitHub Pull Request.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Failed: GITHUB_TOKEN environment variable not set."
        
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    
    try:
        response = httpx.post(url, headers=headers, json={"body": comment_body})
        response.raise_for_status()
        return "Comment posted successfully."
    except Exception as e:
        return f"Failed to post comment: {e}"
