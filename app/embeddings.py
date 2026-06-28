from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

# ----- Utilities -----
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="retrieval_document",
    dimensions=768
)

def store_meeting_embedding(meeting_id: int, project_id: int, user_id: int, title: str, summary: str, action_items: list = [], decisions: list = [], deadlines: list = [], participants: list = [], sentiment: str = ""):
    action_items_text = "\n".join(f"- {item}" for item in action_items) if action_items else "None"
    decisions_text = "\n".join(f"- {d}" for d in decisions) if decisions else "None"
    deadlines_text = "\n".join(f"- {d}" for d in deadlines) if deadlines else "None"
    participants_text = ", ".join(participants) if participants else "None"

    text_to_embed = f"""Meeting: {title}
Participants: {participants_text}
Sentiment: {sentiment}
Summary: {summary}
Action Items:
{action_items_text}
Key Decisions:
{decisions_text}
Deadlines:
{deadlines_text}"""

    print(f"[EMBEDDING] Starting for meeting_id={meeting_id}")
    print(f"[EMBEDDING] Text to embed:\n{text_to_embed}")

    vector = embeddings.embed_query(text_to_embed)
    vector = vector[:768]

    result = supabase_client.table("meeting_embeddings").insert({
        "meeting_id": meeting_id,
        "project_id": project_id,
        "user_id": user_id,
        "content": text_to_embed,
        "embedding": vector,
        "metadata": {
            "meeting_id": meeting_id,
            "project_id": project_id,
            "user_id": user_id,
            "title": title,
        }
    }).execute()
    print(f"[EMBEDDING] Successfully stored for meeting_id={meeting_id}")






