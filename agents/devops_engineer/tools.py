from typing import Dict, Any

async def generate_dockerfile(project_type: str) -> str:
    """Generates a Dockerfile for the specified project type."""
    return "FROM python:3.11\nCMD ['python', 'main.py']"

async def write_ci_pipeline(ci_tool: str) -> str:
    """Generates a CI/CD pipeline configuration."""
    return "name: CI\non: [push]"

DEVOPS_TOOLS = [
    generate_dockerfile,
    write_ci_pipeline
]
