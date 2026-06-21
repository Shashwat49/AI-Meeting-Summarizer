"""
FastAPI app entrypoint.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, meetings, projects

# Creates tables in PostgreSQL if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Meeting Notes Summarizer API")

# Allow your frontend to call this API (update origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(meetings.router)


@app.get("/")
def root():
    return {"message": "AI Meeting Notes Summarizer API is running"}
