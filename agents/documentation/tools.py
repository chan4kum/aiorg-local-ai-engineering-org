from typing import Dict, Any

async def generate_readme(project_info: dict) -> str:
    """Generates a comprehensive README.md."""
    return f"# {project_info.get('name', 'Project')}\n\nDescription..."

async def document_code(source_code: str) -> str:
    """Adds docstrings and comments to raw source code."""
    return f'\"\"\"Docstring\"\"\"\n{source_code}'

DOCS_TOOLS = [
    generate_readme,
    document_code
]
