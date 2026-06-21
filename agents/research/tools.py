from typing import List, Dict, Any

async def web_search(query: str) -> List[Dict[str, str]]:
    """Simulates a web search."""
    return [{"title": "Docs", "url": "http://example.com/docs", "snippet": "Useful info"}]

async def fetch_url_content(url: str) -> str:
    """Fetches the content of a URL."""
    return f"Content of {url}"

RESEARCH_TOOLS = [
    web_search,
    fetch_url_content
]
