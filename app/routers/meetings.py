"""
Routes for submitting transcripts and retrieving saved meetings.
Meetings belong to a project, which belongs to a user.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.core.deps import get_current_user
from app.summarizer import summarize_transcript
from app.embeddings import store_meeting_embedding

router = APIRouter(prefix="/meetings", tags=["Meetings"])


def _get_owned_project(project_id: int, db: Session, current_user: models.User) -> models.Project:
    """Ensures the project exists and belongs to the current user."""
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not yours")
    return project


@router.post("/summarize", response_model=schemas.MeetingOut, status_code=status.HTTP_201_CREATED)
def create_summary(
    payload: schemas.TranscriptInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Takes a project_id + transcript, runs it through the AI summarizer chain,
    saves the structured result under that project, and returns it.
    """
    _get_owned_project(payload.project_id, db, current_user)

    try:
        ai_result = summarize_transcript(payload.transcript)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong while generating the summary: {str(e)}",
        )

    new_meeting = models.Meeting(
        project_id=payload.project_id,
        title=ai_result.title,
        description=payload.transcript,  # raw transcript stored here
        status="completed",
        summary=ai_result.summary,
        action_items=ai_result.action_items,
        key_decisions=ai_result.decisions,
        deadlines=ai_result.deadlines,
        participants=ai_result.participants,
        date_time=ai_result.date_time,
        duration=ai_result.duration,
        sentiment=ai_result.sentiment,
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    try:
        store_meeting_embedding(
            meeting_id=new_meeting.id,
            project_id=payload.project_id,
            user_id=current_user.id,
            summary=ai_result.summary,
            title=ai_result.title,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Embedding failed: {str(e)}"
        )

    return new_meeting


@router.get("/", response_model=List[schemas.MeetingListOut])
def list_meetings(
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Returns meetings belonging to the logged-in user.
    Pass ?project_id=X to filter to one project, otherwise returns
    meetings across all of the user's projects.
    """
    query = (
        db.query(models.Meeting)
        .join(models.Project, models.Meeting.project_id == models.Project.id)
        .filter(models.Project.user_id == current_user.id)
    )
    if project_id is not None:
        query = query.filter(models.Meeting.project_id == project_id)

    return query.order_by(models.Meeting.created_at.desc()).all()


@router.get("/{meeting_id}", response_model=schemas.MeetingOut)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    meeting = (
        db.query(models.Meeting)
        .join(models.Project, models.Meeting.project_id == models.Project.id)
        .filter(models.Meeting.id == meeting_id, models.Project.user_id == current_user.id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    meeting = (
        db.query(models.Meeting)
        .join(models.Project, models.Meeting.project_id == models.Project.id)
        .filter(models.Meeting.id == meeting_id, models.Project.user_id == current_user.id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    db.delete(meeting)
    db.commit()
    return None
