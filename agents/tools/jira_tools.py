from langchain_core.tools import tool
import httpx
import os
import base64

@tool
def create_jira_ticket(project_key: str, summary: str, description: str, issue_type: str = "Task") -> str:
    """
    Create a new Jira ticket.
    Useful for creating technical debt, bug, or feature implementation tickets.
    """
    domain = os.getenv("JIRA_DOMAIN")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    
    if not all([domain, email, token]):
        return "Failed: JIRA_DOMAIN, JIRA_EMAIL, or JIRA_API_TOKEN not set."
        
    auth_string = f"{email}:{token}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_b64}"
    }
    url = f"https://{domain}/rest/api/3/issue"
    
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            },
            "issuetype": {"name": issue_type}
        }
    }
    
    try:
        response = httpx.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return f"Created ticket {data.get('key')} successfully."
    except Exception as e:
        return f"Failed to create Jira ticket: {e}"
