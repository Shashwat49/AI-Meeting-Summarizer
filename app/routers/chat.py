from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.core.deps import get_current_user
from app import models
from app.rag import query_meetings

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str
    project_id: Optional[int] = None 


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]


@router.post("/", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    try:
        result = query_meetings(
            question=payload.question,
            user_id=current_user.id,
            project_id=payload.project_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong while querying meetings: {str(e)}"
        )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
