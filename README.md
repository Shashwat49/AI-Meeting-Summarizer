# AI Meeting Summarizer

A full-stack AI application that transcribes meeting transcripts into structured summaries and lets you query across all your meetings using a RAG-based chat interface.

---

## What it does

- Paste a meeting transcript and get back a structured summary — title, participants, action items, decisions, deadlines, and sentiment
- All meetings are organized under projects
- A floating chat widget lets you ask questions across your meetings in natural language — powered by RAG (Retrieval Augmented Generation)

---

## Tech Stack

**Backend**
- FastAPI — REST API with JWT authentication
- LangChain LCEL — LLM orchestration
- Google Gemini (`gemini-2.5-flash-lite`) — summarization
- Google Gemini (`gemini-embedding-001`) — generating vector embeddings
- Pydantic — structured output parsing
- PostgreSQL via Supabase — database
- pgvector — storing and searching meeting embeddings
- Deployed on Render

**Frontend**
- Built with Lovable
- Floating chat widget for querying meetings

---

## How the RAG chat works

1. When a meeting is summarized, its content (title, summary, action items, decisions, deadlines) is converted into a vector embedding and stored in Supabase
2. When a user asks a question, the question is embedded and the most relevant meeting chunks are retrieved
3. Retrieved context is passed to Gemini which generates a grounded answer
4. The chat shows the answer along with which meetings it pulled from

---

## Project Structure

```
app/
├── main.py               # FastAPI app entry point
├── database.py           # DB connection
├── models.py             # SQLAlchemy models
├── schemas.py            # Pydantic schemas
├── summarizer.py         # LangChain summarization chain
├── embeddings.py         # Embedding generation and storage
├── rag.py                # RAG retrieval and chat chain
├── routers/
│   ├── auth.py           # Login and signup
│   ├── projects.py       # Project CRUD
│   ├── meetings.py       # Meeting summarization and retrieval
│   └── chat.py           # Chat endpoint
└── core/
    ├── deps.py           # Auth dependencies
    └── security.py       # JWT utilities
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get JWT token |
| POST | `/projects/` | Create a project |
| GET | `/projects/` | List all projects |
| DELETE | `/projects/{id}` | Delete a project |
| POST | `/meetings/summarize` | Submit transcript and get summary |
| GET | `/meetings/` | List meetings |
| GET | `/meetings/{id}` | Get a specific meeting |
| DELETE | `/meetings/{id}` | Delete a meeting |
| POST | `/chat/` | Query meetings using natural language |

---

## Environment Variables

```
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
GOOGLE_API_KEY=
SECRET_KEY=
```

---

## Live Demo

Backend: [https://ai-meeting-summarizer-rjzh.onrender.com](https://ai-meeting-summarizer-rjzh.onrender.com)

API Docs: [https://ai-meeting-summarizer-rjzh.onrender.com/docs](https://ai-meeting-summarizer-rjzh.onrender.com/docs)

---

## Notes

- Free tier Gemini API has a daily request limit — the app may respond slowly or hit quota during heavy use
- The backend is hosted on Render's free tier and may take ~50 seconds to wake up after inactivity
