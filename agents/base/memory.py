from typing import Dict, Any
from backend.memory.memory_manager import MemoryManager

class AgentMemoryMixin:
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    async def get_context(self, session_id: str, run_id: str, query: str) -> str:
        context_data = await self.memory.retrieve_context(session_id, run_id, query)
        
        # Format the context into a string
        recent = "\n".join([f"- {msg['text']}" for msg in context_data.get("recent_history", [])])
        semantic = "\n".join([f"- {res['text']}" for res in context_data.get("semantic_context", [])])
        
        return f"Recent Conversation:\n{recent}\n\nRelevant Memories:\n{semantic}"

    async def save_memory(self, session_id: str, run_id: str, interaction: str, metadata: Dict[str, Any] = None):
        await self.memory.save_interaction(session_id, run_id, interaction, metadata)
