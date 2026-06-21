from typing import Dict, Any

async def generate_test_plan(user_story: str) -> str:
    """Generates a test plan for a given user story."""
    return f"# Test Plan\nStory: {user_story}"

async def run_test_suite(test_directory: str) -> dict:
    """Simulates running a test suite."""
    return {"passed": True, "coverage": "85%"}

QA_TOOLS = [
    generate_test_plan,
    run_test_suite
]
