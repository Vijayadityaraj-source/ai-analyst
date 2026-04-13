import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from app.models.chat import ColumnSchema
from typing import Type, TypeVar

T = TypeVar('T', bound=BaseModel)

def make_llm(output_schema: Type[T], temperature: float = 0):
    """
    Creates a Gemini LLM instance with structured output.
    temperature=0 for classification/SQL nodes (deterministic)
    temperature=0.3 for answer/insight nodes (some variation is fine)
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=temperature,
    ).with_structured_output(output_schema)


def format_history(history: list, max_turns: int = 4) -> str:
    if not history:
        return "No previous conversation."
    recent = history[-max_turns:]
    lines = []
    for turn in recent:
        # handle both dict (from state) and Pydantic model (direct call)
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
        samples = ', '.join(str(v) for v in col["sampleValues"][:5] if v is not None)
        lines.append(
            f"{col['name']} ({col['type']}) | unique: {col['uniqueCount']} | nulls: {col['nullCount']} | samples: {samples}"
        )
    return '\n'.join(lines)