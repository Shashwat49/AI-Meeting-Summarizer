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

# ----- Function to store meeting embedding -----
def store_meeting_embedding(meeting_id: int, project_id: int, user_id: int, summary: str, title: str):
    print(f"[EMBEDDING] Starting for meeting_id={meeting_id}")
    
    text_to_embed = f"Meeting: {title} \nSummary: {summary}"
    
    vector = embeddings.embed_query(text_to_embed)
    print(f"[EMBEDDING] Vector generated, dimensions={len(vector)}")
    
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
    print(f"[EMBEDDING] Insert result: {result}")






