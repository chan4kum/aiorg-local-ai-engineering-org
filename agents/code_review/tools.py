from typing import Dict, Any

async def analyze_diff(diff_content: str) -> dict:
    """Analyzes a git diff and returns a list of comments/suggestions."""
    return {"comments": ["Looks good, but missing tests."]}

async def enforce_style_guide(file_path: str) -> bool:
    """Checks if a file adheres to the style guide."""
    return True

REVIEW_TOOLS = [
    analyze_diff,
    enforce_style_guide
]
