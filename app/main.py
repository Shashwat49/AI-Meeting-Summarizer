from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, meetings, projects, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Meeting Notes Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-meeting-summarizer-1-dvsg.onrender.com",
        "https://id-preview--1dfa762d-637e-443e-a5bd-577bb076af5c.lovable.app",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(meetings.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "AI Meeting Notes Summarizer API is running"}
