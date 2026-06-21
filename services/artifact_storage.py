import os
import json
from typing import Dict, Any

class ArtifactStorage:
    def __init__(self, workspace_path: str = "/tmp/openclaw/workspaces/artifacts"):
        self.workspace_path = workspace_path
        os.makedirs(self.workspace_path, exist_ok=True)
        
    def save_artifact(self, filename: str, content: str, metadata: Dict[str, Any]) -> str:
        """
        Saves physical artifact and returns the path. 
        In a real app, it would also index metadata in Postgres.
        """
        file_path = os.path.join(self.workspace_path, filename)
        with open(file_path, "w") as f:
            f.write(content)
            
        print(f"[ArtifactStorage] Saved physical artifact to {file_path}")
        print(f"[ArtifactStorage] Indexing metadata in postgres: {metadata}")
        
        return file_path

artifact_storage = ArtifactStorage()
