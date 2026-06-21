"""
This file contains your EXACT summarizer logic from the Streamlit app,
just wrapped inside a function (summarize_transcript) instead of being
tied to Streamlit UI calls. The prompt, schema, and chain are untouched.
"""

from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

model = GoogleGenerativeAI(model='gemini-2.5-flash-lite')

# transcript -> prompt -> model -> output parser

class MeetingSummary(BaseModel):
    title: str = Field(description='defines the title fo the meeting')
    date_time: str = Field(description='specifies the timestamp of the meeting')
    duration: str = Field(description='time duration fo the meeting in minutes or hours')
    participants: List[str] = Field(description='lists the names of the participants')
    summary: str = Field(description='specifies a short summary of the whole meeting')
    action_items: List[str] = Field(description='defines a list of important actions which are to be performed after the meeting')
    decisions: List[str] = Field(description='key decisions taken during the meeting which are important')
    deadlines: List[str] = Field(description='specifies the important deadlines and works which are due')
    sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(description='specifies the tone of the meeting')

parser = PydanticOutputParser(pydantic_object=MeetingSummary)

prompt = PromptTemplate(
    template = """
You are an expert meeting transcription analyst.

Your task is to extract structured information from a meeting transcript.

You MUST follow these rules strictly:
- Do NOT invent or assume any information not present in the transcript.
- If a field is missing, return "N/A" or an empty list [] as appropriate.
- Be precise and factual.
- Do not repeat information across sections unless required.
- Keep all outputs concise and structured.
- Every action item must be tied to a speaker if mentioned.
- Deadlines must only be included if explicitly stated or clearly implied.

### EXTRACTION RULES

1. SUMMARY:
- 3 to 5 sentences max
- Include only key discussion points and outcomes

2. ACTION ITEMS:
- List all tasks assigned to individuals
- Must include speaker name if available
- Do NOT mix with decisions or deadlines

3. DECISIONS:
- Only final decisions made by the team
- Not discussions or suggestions

4. DEADLINES:
- Only time-based commitments (e.g. Tuesday, next week, Friday)
- Do NOT include general tasks here

5. SENTIMENT:
- Choose ONE: positive, negative, neutral, mixed
- Base it on overall tone of discussion

### OUTPUT FORMAT
{format_instructions}

TRANSCRIPT:
{transcript}
""",
    input_variables=['transcript'],
    partial_variables={'format_instructions': parser.get_format_instructions()}
)

chain = prompt | model | parser


def summarize_transcript(transcript: str) -> MeetingSummary:
    """
    Takes a raw transcript string and returns a MeetingSummary pydantic object.
    This is the exact chain.invoke() call from the Streamlit app, just
    wrapped in a reusable function so the FastAPI routes can call it.
    """
    result = chain.invoke({'transcript': transcript})
    return result
