from typing import Optional
import json

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.state import GraphState
from app.utils import make_llm, format_schema, format_history
from app.state import GeneratedAnswerResult


class GenerateAnswer(BaseModel):
    reasoning: str
    text: str
    # chartSpec: Optional[ChartSpec] = None  TODO Phase 4
    insights: Optional[str] = None
    followUps: Optional[list[str]] = None


llm = make_llm(GenerateAnswer, temperature=0.3)

SYSTEM_PROMPT = """You are a data analyst assistant for a spreadsheet tool.
The user has asked a question about their data.

The spreadsheet schema:
{schema}

Query results (up to 50 rows):
{query_result}

Context: {query_context}

GUIDELINES:
- If query results contain data: reference specific numbers, do not speak in generalities
- If context is 'schema_only': answer confidently from schema metadata alone — no apology needed for missing results
- If context is 'no_rows_returned': tell the user the query returned no results and explain what that means
- Be concise — the user wants a quick answer, not a long explanation
- Do not hallucinate data not present in either results or schema
- Optionally include one non-obvious insight
- Optionally suggest 2-3 follow-up questions
- Never perform calculations that combine query result numbers with schema metadata numbers (e.g. dividing a total by uniqueCount). Only reference numbers that appear explicitly in the query results.

Respond with your reasoning first, then the answer.
"""

HUMAN_PROMPT = """Recent conversation:
{history}

User's message: {message}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

def generate_answer(state: GraphState) -> dict:
    try:
        chain = prompt | llm

        query_result = state["query_result"] or []
        formatted_result = json.dumps(query_result[:50], indent=2, default=str)

        # Tell the model why results are empty — removes defensive reasoning
        if state.get("intent") == "general_question":
            query_context = "schema_only — this question does not require data rows"
        elif not query_result:
            query_context = "no_rows_returned — the SQL query executed but matched no rows"
        else:
            query_context = f"{len(query_result)} rows returned from SQL execution"
        
        result: GenerateAnswer = chain.invoke({
            "schema": format_schema(state["schema"]),
            "history": format_history(state["history"]),
            "message": state["message"],
            "query_result": formatted_result,
            "query_context": query_context
        })
        
        print(f"[generate_answer] reasoning: {result.reasoning}")
        print(f"[generate_answer] text: {result.text}")
        print(f"[generate_answer] insights: {result.insights}")
        print(f"[generate_answer] followUps: {result.followUps}")

        return {
            "generated_answer": GeneratedAnswerResult(
                text=result.text,
                insights=result.insights,
                followUps=result.followUps
            )
        }

    except Exception as e:
        print(f"[generate_answer] error: {e}")
        return {
            "generated_answer": GeneratedAnswerResult(
                text="I encountered an error generating an answer. Please try again.", 
                insights=None, 
                followUps=None
            )
        } 