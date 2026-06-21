from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class MemoryEntry(BaseModel):
    content: str
    metadata: Dict[str, Any]

@router.get("/search")
async def search_memory(q: str = Query(..., description="Query string")):
    # Assuming qdrant search here
    return [{"score": 0.99, "content": "Memory result for: " + q}]

@router.post("")
async def add_memory(entry: MemoryEntry):
    # Store in Vector DB (Qdrant)
    return {"status": "added", "entry": entry.model_dump()}

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    return {"status": "deleted", "id": memory_id}
