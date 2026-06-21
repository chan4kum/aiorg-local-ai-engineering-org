from typing import Dict, Any

async def run_sast(directory: str) -> dict:
    """Simulates running Static Application Security Testing."""
    return {"vulnerabilities": []}

async def check_dependencies(requirements_file: str) -> dict:
    """Simulates checking dependencies for CVEs."""
    return {"safe": True}

SECURITY_TOOLS = [
    run_sast,
    check_dependencies
]
