# AI Meeting Notes Summarizer — Backend API

FastAPI backend wrapping your existing Gemini/LangChain summarizer logic,
with JWT auth and PostgreSQL storage. Matches your existing
`users` -> `projects` -> `meetings` schema.

## Project Structure

```
app/
├── main.py              # FastAPI app entrypoint
├── database.py          # PostgreSQL connection (SQLAlchemy)
├── models.py             # DB tables: User, Project, Meeting (matches your existing schema)
├── schemas.py             # Request/response validation models
├── summarizer.py          # Your exact Streamlit logic, wrapped in a function
├── core/
│   ├── security.py        # Password hashing + JWT helpers
│   └── deps.py             # get_current_user dependency
└── routers/
    ├── auth.py             # /auth/signup, /auth/login
    ├── projects.py          # /projects/* endpoints
    └── meetings.py          # /meetings/* endpoints
```

## IMPORTANT: Database Migration Required

Your `meetings` table already exists but is missing 4 columns the AI
summarizer needs (`participants`, `date_time`, `duration`, `sentiment`).
**Run `migration.sql` against your database once before starting the app:**

```bash
psql "$DATABASE_URL" -f migration.sql
```

`Base.metadata.create_all()` in `main.py` only creates tables that don't
exist yet — it will **not** alter your existing `users`, `projects`, or
`meetings` tables. So this migration step is required, otherwise saving
a meeting will fail with a "column does not exist" error.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your real values:
   ```bash
   cp .env.example .env
   ```
   - `DATABASE_URL`: your existing PostgreSQL connection string
   - `SECRET_KEY`: a random secret for JWT signing (`openssl rand -hex 32`)
   - `GOOGLE_API_KEY`: your Gemini API key

3. Run the migration (see above) against your existing database.

4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open the interactive API docs at: `http://127.0.0.1:8000/docs`

## API Endpoints

### Auth
| Method | Endpoint        | Description                 |
|--------|-----------------|------------------------------|
| POST   | `/auth/signup`  | Create a new user account    |
| POST   | `/auth/login`   | Login, returns JWT token     |

`/auth/login` expects form data (`username`, `password`) — not JSON —
because it follows the standard OAuth2 password flow. Use the `username`
field for the user's email.

### Projects (all require `Authorization: Bearer <token>` header)
| Method | Endpoint              | Description                  |
|--------|-------------------------|-------------------------------|
| POST   | `/projects/`             | Create a new project          |
| GET    | `/projects/`              | List your projects            |
| GET    | `/projects/{project_id}`   | Get one project                |

### Meetings (all require `Authorization: Bearer <token>` header)
| Method | Endpoint                       | Description                                          |
|--------|----------------------------------|--------------------------------------------------------|
| POST   | `/meetings/summarize`            | Submit `{ project_id, transcript }`, get + save summary |
| GET    | `/meetings/`                      | List all meetings (optionally `?project_id=X`)         |
| GET    | `/meetings/{meeting_id}`           | Get full details of one meeting                        |
| DELETE | `/meetings/{meeting_id}`           | Delete a meeting                                        |

## Example Frontend Flow

1. `POST /auth/signup` with `{ "email": "...", "password": "..." }`
2. `POST /auth/login` with form fields `username` + `password` → get `access_token`
3. Store the token (e.g. in localStorage)
4. `POST /projects/` with `{ "name": "Q3 Planning" }` → get back a `project_id`
5. `POST /meetings/summarize` with `{ "project_id": 1, "transcript": "..." }` and header
   `Authorization: Bearer <access_token>` → returns structured summary
6. `GET /meetings/?project_id=1` to render history/dashboard list for that project
7. `GET /meetings/{id}` to render full details of one meeting

## Notes

- Your summarizer logic (prompt, schema, chain) in `app/summarizer.py` is
  **unchanged** from your Streamlit script — only wrapped in a function
  called `summarize_transcript(transcript: str)`.
- Meetings belong to projects, projects belong to users — all access is
  scoped so users only ever see their own data.
- CORS is currently open to all origins (`*`) for development — restrict
  `allow_origins` in `app/main.py` to your frontend's URL before deploying.
