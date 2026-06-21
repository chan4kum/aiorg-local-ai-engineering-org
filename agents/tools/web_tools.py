from langchain_core.tools import tool
import httpx
import os

@tool
def search_web(query: str) -> str:
    """
    Search the web for real-time information using the Tavily Search API.
    Useful for gathering current events, reading documentation, or researching technical topics.
    """
    api_key = os.getenv("TAVILY_API_KEY", "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")
    
    if not api_key:
        return "Failed: TAVILY_API_KEY is not set."
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": 5
    }
    
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        # Format the response nicely
        result_text = f"Answer: {data.get('answer', 'No direct answer generated.')}\n\nSources:\n"
        for idx, result in enumerate(data.get('results', [])):
            result_text += f"{idx + 1}. [{result.get('title')}]({result.get('url')}): {result.get('content')[:200]}...\n"
            
        return result_text
    except Exception as e:
        return f"Failed to perform web search: {e}"
