from typing import TypedDict, Optional, Literal
from pydantic import BaseModel

class FixedSQLResult(BaseModel):
    sql: Optional[str]
    explanation: Optional[str]
    stepNumber: int

class GeneratedAnswerResult(BaseModel):
    text: str
    # chartSpec: Optional[ChartSpec]  TODO Phase 4
    insights: Optional[str] = None
    followUps: Optional[list[str]] = None

class GraphState(TypedDict):
    # ── Inputs (populated by main.py from ChatRequest) ──────────────  
    entry_point: str
    message: str
    schema: list[dict]
    history: list[dict]
    session_id: str
    sqlError: Optional[FixedSQLResult]
    query_result: Optional[list]

    # ── Written by nodes ─────────────────────────────────────────────
    intent: Optional[Literal['ambiguous', 'data_question', 'general_question', 'no_data']]
    clarification_question: Optional[str]
    execution_plan: Optional[list]
    fixed_sql_result: Optional[FixedSQLResult]  
    response: Optional[dict]                    # filled by formatted_response, can be ClarificationResponse, AnswerResponse, etc. determined by format_response logic based on which fields are populated
    generated_answer: Optional[GeneratedAnswerResult]