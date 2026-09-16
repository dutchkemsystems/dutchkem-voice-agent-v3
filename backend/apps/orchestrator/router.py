from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Optional

from apps.orchestrator.llm_service import LLMService

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])

llm_service = LLMService()


class GenerateAnswerRequest(BaseModel):
    question: str
    question_type: str = "hr"
    candidate_profile: Dict = {}
    conversation_history: list = []


class GenerateAnswerResponse(BaseModel):
    answer: str


@router.post("/generate", response_model=GenerateAnswerResponse)
async def generate_answer(request: GenerateAnswerRequest):
    """Generate an interview answer using the LLM service."""
    try:
        answer = await llm_service.generate_interview_answer(
            question=request.question,
            question_type=request.question_type,
            candidate_profile=request.candidate_profile,
            conversation_history=request.conversation_history,
        )
        return GenerateAnswerResponse(answer=answer)
    except Exception as e:
        return GenerateAnswerResponse(answer=f"Error generating response: {str(e)}")


@router.get("/health")
async def orchestrator_health():
    """Check LLM service health."""
    try:
        from apps.orchestrator.ollama_client import OllamaClient
        client = OllamaClient()
        healthy = await client.health_check()
        return {"status": "ok" if healthy else "degraded", "ollama": healthy}
    except Exception:
        return {"status": "degraded", "ollama": False}
