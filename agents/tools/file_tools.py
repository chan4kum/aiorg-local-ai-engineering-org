from langchain_core.tools import tool
import os

@tool
def read_local_file(file_path: str) -> str:
    """
    Read the contents of a local file.
    Only allows reading from within the agent's workspace (/tmp/openclaw/workspaces).
    """
    # Security: Ensure path doesn't escape workspace
    workspace = "/tmp/openclaw/workspaces"
    abs_path = os.path.abspath(os.path.join(workspace, file_path))
    if not abs_path.startswith(workspace):
        return "Security Error: Path traverses outside allowed workspace."
        
    try:
        with open(abs_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Failed to read file: {e}"

@tool
def write_local_file(file_path: str, content: str) -> str:
    """
    Write contents to a local file.
    Creates parent directories if they don't exist.
    Only allows writing within the agent's workspace.
    """
    workspace = "/tmp/openclaw/workspaces"
    abs_path = os.path.abspath(os.path.join(workspace, file_path))
    if not abs_path.startswith(workspace):
        return "Security Error: Path traverses outside allowed workspace."
        
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Failed to write file: {e}"
