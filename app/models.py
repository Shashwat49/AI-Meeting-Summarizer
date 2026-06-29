from sqlalchemy import (
    Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # stores the hashed password
    company = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="projects")
    meetings = relationship("Meeting", back_populates="project")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    title = Column(String)
    description = Column(Text)   # raw transcript stored here
    status = Column(String)
    summary = Column(Text)
    action_items = Column(JSON)
    key_decisions = Column(JSON)
    deadlines = Column(JSON)

    # --- extra columns added to support AI output fields ---
    participants = Column(JSON)
    date_time = Column(String)
    duration = Column(String)
    sentiment = Column(String)

    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="meetings")
