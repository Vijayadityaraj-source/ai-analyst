from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.state import GraphState, FixedSQLResult
from app.utils import make_llm, format_schema, format_history


class FixedSQL(BaseModel):
    reasoning: str
    fixed_sql: str
    explanation: str


llm = make_llm(FixedSQL, temperature=0)

SYSTEM_PROMPT = """You are a SQL fixing assistant for a data analysis tool.
A SQL query was executed against the user's spreadsheet and produced an error.
Your job is to correct the SQL query while preserving its intended meaning.

The user has uploaded a spreadsheet with the following schema:
{schema}

The SQL query that failed:
{sql}

The error message from the database:
{sql_error}

SQL RULES — follow these exactly:
- SQL dialect: DuckDB
- The original uploaded data is always in a table called 'data'. Step outputs are named step_1_result, step_2_result, etc.
- Only write SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or CREATE.
- Always add LIMIT 200 if not already present.
- Never generate Python, JavaScript, or any language other than SQL.
- Only reference column names that exist in the schema above.

Respond with your reasoning first, then the fixed SQL, then a brief explanation of what changed and why."""

HUMAN_PROMPT = """Recent conversation:
{history}

User's message: {message}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])


def fix_sql(state: GraphState) -> dict:
    try:
        chain = prompt | llm
        result: FixedSQL = chain.invoke({
            "schema": format_schema(state["schema"]),
            "history": format_history(state["history"]),
            "message": state["message"],
            "sql": state["sqlError"].failedSql,
            "sql_error": state["sqlError"].errorMessage,
        })

        print(f"[fix_sql] reasoning: {result.reasoning}")
        print(f"[fix_sql] fixed_sql: {result.fixed_sql}")
        print(f"[fix_sql] explanation: {result.explanation}")

        return {
            "fixed_sql_result": FixedSQLResult(
                sql=result.fixed_sql,
                explanation=result.explanation,
                stepNumber=state["sqlError"].stepNumber
            )
        }

    except Exception as e:
        print(f"[fix_sql] error: {e}")
        step_number = state["sqlError"].stepNumber if state.get("sqlError") else 0
        return {
            "fixed_sql_result": FixedSQLResult(
                sql=None,
                explanation=None,
                stepNumber=step_number
            )
        }