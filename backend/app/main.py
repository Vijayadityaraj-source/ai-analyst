from dotenv import load_dotenv
load_dotenv()   # ← must be before any app imports

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Union
import os

from app.models.chat import (
    ChatRequest, ChatResponse,
    ClarificationResponse, AnswerResponse,
    ExecutionPlanResponse, NoDataResponse,
    ErrorResponse, FixedSQLResponse
)
from app.graph import graph

if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY is missing in .env file")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):

    # ── Decide entry point ───────────────────────────────────────────
    if request.sqlError:
        entry_point = "fix_sql"
    elif request.queryResult:
        entry_point = "generate_answer"
    else:
        entry_point = "classify_intent"

    # ── Build initial state ──────────────────────────────────────────
    initial_state = {
        # inputs
        "entry_point": entry_point,
        "message": request.message,
        "schema": [col.model_dump() for col in request.schema],
        "history": [turn.model_dump() for turn in request.history],
        "session_id": request.sessionId,
        "sqlError": request.sqlError,
        "query_result": request.queryResult,

        # node outputs — all start as None
        "intent": None,
        "clarification_question": None,
        "execution_plan": None,
        "fixed_sql_result": None,
        "generated_answer": None,
        "response": None,
    }

    # ── Run graph ────────────────────────────────────────────────────
    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        print(f"[main] graph error: {e}")
        raise HTTPException(status_code=500, detail="Graph execution failed")

    # ── Extract and validate response ────────────────────────────────
    response_dict = final_state.get("response")

    if not response_dict:
        raise HTTPException(status_code=500, detail="Graph produced no response")

    # Pydantic reads the 'type' discriminator and picks the correct variant
    # model_validate works on a plain dict and returns the correct ChatResponse subtype
    try:
        response_type_map = {
            "clarification": ClarificationResponse,
            "answer": AnswerResponse,
            "execution_plan": ExecutionPlanResponse,
            "no_data": NoDataResponse,
            "fixed_sql": FixedSQLResponse,
            "error": ErrorResponse,
        }
        response_type = response_dict.get("type")
        model_class = response_type_map.get(response_type, ErrorResponse)
        return model_class.model_validate(response_dict)

    except Exception as e:
        # print(f"[main] response validation error: {e}")
        return ErrorResponse(
            type="error",
            message="Response could not be validated. Please try again."
        )