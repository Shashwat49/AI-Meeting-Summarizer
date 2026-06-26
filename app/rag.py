import os
from supabase import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="retrieval_query",
    dimensions=768
)
llm = GoogleGenerativeAI(model="gemini-2.5-flash-lite")

parser = StrOutputParser()

def retrieve_relevant_meetings(query: str, user_id: int, project_id: int = None, k: int = 4) -> list:
    test = supabase.table("meeting_embeddings").select("id, meeting_id, user_id").execute()
    print(f"[RAG DEBUG] Direct table query: {test.data}")
    
    query_vector = embeddings_model.embed_query(query)
    query_vector = query_vector[:768]

    query_vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

    response = supabase.rpc("match_meeting_embeddings", {
        "query_embedding": query_vector_str,
        "match_count": k
    }).execute()

    results = response.data or []
    print(f"[RAG DEBUG] Total results from DB: {len(results)}")
    for r in results:
        meta = r.get("metadata", {})
        print(f"[RAG DEBUG] meta user_id={meta.get('user_id')} (type={type(meta.get('user_id'))}), current user_id={user_id} (type={type(user_id)})")

    filtered = []
    for r in results:
        meta = r.get("metadata", {})
        if meta.get("user_id") != user_id:
            continue
        if project_id and meta.get("project_id") != project_id:
            continue
        filtered.append(r)

    return filtered


def build_context(chunks: list) -> str:
    if not chunks:
        return "No relevant meetings found."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        title = meta.get("title", "Untitled Meeting")
        content = chunk.get("content", "")
        context_parts.append(f"[Meeting {i}: {title}]\n{content}")

    return "\n\n---\n\n".join(context_parts)


prompt = PromptTemplate(
    template="""
You are an intelligent assistant that helps users query their meeting notes.

Answer the user's question based ONLY on the meeting context provided below.
If the answer is not found in the context, say "I couldn't find relevant information in your meetings."
Do not make up any information.
Be concise and precise.

meeting context:
{context}

user question:
{question}

answer:
""",
    input_variables=["context", "question"]
)

chain = (
    {
        "context": RunnablePassthrough(),
        "question": RunnablePassthrough()
    } | prompt | llm | parser
)


def query_meetings(question: str, user_id: int, project_id: int = None) -> dict:
    try:
        chunks = retrieve_relevant_meetings(question, user_id, project_id)
        context = build_context(chunks)

        sources = []
        for chunk in chunks:
            title = chunk.get("metadata", {}).get("title")
            if title and title not in sources:
                sources.append(title)

        answer = chain.invoke({"context": context, "question": question})

        return {
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        import traceback
        print(f"[RAG ERROR] {str(e)}")
        print(traceback.format_exc())
        raise
