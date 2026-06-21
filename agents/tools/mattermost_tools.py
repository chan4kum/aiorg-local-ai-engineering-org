from langchain_core.tools import tool
import httpx
import os

@tool
def send_mattermost_message(text: str, channel: str = None) -> str:
    """
    Send a message to a Mattermost channel.
    Useful for notifying humans of critical errors, deployment status, or requesting approvals.
    Requires MATTERMOST_WEBHOOK_URL to be set in the environment.
    """
    webhook_url = os.getenv("MATTERMOST_WEBHOOK_URL")
    if not webhook_url:
        return "Failed: MATTERMOST_WEBHOOK_URL environment variable not set."
        
    payload = {"text": text}
    if channel:
        payload["channel"] = channel
        
    headers = {"Content-Type": "application/json"}
    
    try:
        response = httpx.post(webhook_url, headers=headers, json=payload, timeout=10.0)
        response.raise_for_status()
        return f"Message successfully sent to Mattermost."
    except Exception as e:
        return f"Failed to send Mattermost message: {e}"
