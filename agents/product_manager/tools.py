from typing import Dict, Any, List

async def generate_prd(requirements: str) -> str:
    """Generates a Product Requirements Document (PRD) from raw requirements."""
    return f"# PRD\nRequirements: {requirements}"

async def create_user_stories(prd_content: str) -> List[Dict[str, Any]]:
    """Creates a list of user stories from a PRD."""
    return [{"title": "User login", "description": "As a user, I want to login."}]

PM_TOOLS = [
    generate_prd,
    create_user_stories
]
