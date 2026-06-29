from pydantic import BaseModel, EmailStr, Field
from typing import List, Literal, Optional
from datetime import datetime


# ---------- Auth schemas ----------

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str = Field(min_length=6)
    company: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    company: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Project schemas ----------

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Meeting schemas ----------

class TranscriptInput(BaseModel):
    project_id: int = Field(description="ID of the project this meeting belongs to")
    transcript: str = Field(min_length=1, description="Raw meeting transcript text")


class MeetingOut(BaseModel):
    id: int
    project_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[List[str]] = None
    key_decisions: Optional[List[str]] = None
    deadlines: Optional[List[str]] = None
    participants: Optional[List[str]] = None
    date_time: Optional[str] = None
    duration: Optional[str] = None
    sentiment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingListOut(BaseModel):
    """Lighter version used when listing many meetings."""
    id: int
    project_id: int
    title: Optional[str] = None
    sentiment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
