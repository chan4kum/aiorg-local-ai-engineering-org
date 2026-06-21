from typing import Dict, Any

async def create_architecture_doc(prd_content: str) -> str:
    """Generates an Architecture Document based on a PRD."""
    return f"# Architecture Document\nBased on PRD..."

async def generate_mermaid_diagram(architecture_description: str) -> str:
    """Generates a Mermaid.js diagram from an architecture description."""
    return "graph TD;\n  A-->B;"

SA_TOOLS = [
    create_architecture_doc,
    generate_mermaid_diagram
]
