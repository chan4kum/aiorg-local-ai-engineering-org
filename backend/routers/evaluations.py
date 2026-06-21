from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class EvaluationRequest(BaseModel):
    artifact_id: str
    criteria: Dict[str, Any]

@router.get("")
async def list_evaluations():
    return []

@router.get("/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    return {"id": evaluation_id, "status": "completed"}

@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_evaluation(request: EvaluationRequest):
    return {"message": "Evaluation started", "artifact_id": request.artifact_id}
