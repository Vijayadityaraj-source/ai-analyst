import os
from typing import Type, TypeVar
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.models.chat import ColumnSchema

T = TypeVar('T', bound=BaseModel)


def make_llm(output_schema: Type[T], temperature: float = 0):
    """
    Creates a Gemini LLM with Groq as automatic fallback.
    
    If Gemini hits a rate limit or any error, LangChain automatically
    retries the same call using Groq llama-3.3-70b.
    
    temperature=0   → classification and SQL nodes (deterministic)
    temperature=0.3 → answer and insight nodes (natural language variation)
    """

    # ── Primary: Gemini ──────────────────────────────────────────────
    primary = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=temperature,
    ).with_structured_output(output_schema)

    # ── Fallback: Groq Llama 3.3 70B ────────────────────────────────
    fallback = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=temperature,
    ).with_structured_output(output_schema)

    # ── Wire fallback ────────────────────────────────────────────────
    # If primary raises ANY exception, LangChain automatically
    # retries with fallback using the same input.
    # exceptions_to_handle narrows this to rate limit errors only.
    return primary.with_fallbacks(
        [fallback],
        exceptions_to_handle=(Exception,)  # catches rate limits, timeouts, API errors
    )


def format_history(history: list, max_turns: int = 4) -> str:
    if not history:
        return "No previous conversation."
    recent = history[-max_turns:]
    lines = []
    for turn in recent:
        if isinstance(turn, dict):
            role = "User" if turn["role"] == "user" else "Assistant"
            content = turn["content"]
        else:
            role = "User" if turn.role == "user" else "Assistant"
            content = turn.content
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def format_schema(schema: list[dict]) -> str:
    lines = []
    for col in schema:
        samples = ', '.join(
            str(v) for v in col["sampleValues"][:5] if v is not None
        )
        lines.append(
            f"{col['name']} ({col['type']}) | unique: {col['uniqueCount']} | nulls: {col['nullCount']} | samples: {samples}"
        )
    return '\n'.join(lines)