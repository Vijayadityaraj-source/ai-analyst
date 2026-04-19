from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.state import GraphState
from app.utils import make_llm, format_schema, format_history
from app.models.chat import ExecutionStep

class ExecutionPlan(BaseModel):
    reasoning: str
    execution_plan: list[ExecutionStep]

llm = make_llm(ExecutionPlan, temperature=0)

SYSTEM_PROMPT = """You are an execution planner for a data analysis tool.
Your job is to produce an ordered list of SQL steps that will answer the user's question.

SPREADSHEET SCHEMA:
{schema}

SQL RULES — follow these exactly:
- SQL dialect: DuckDB
- The original uploaded data is always in a table called 'data'. Step outputs are named step_1_result, step_2_result, etc.
- Only write SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or CREATE.
- Always add LIMIT 200 to the final step if not already present.
- Never generate Python, JavaScript, or any language other than SQL.

STEP TYPES — use exactly these values for the `type` field:
- derive: adds new columns to existing rows, e.g. "add a profit column = revenue minus cost"
- aggregate: groups and summarises rows, e.g. "total revenue by region"
- filter: removes rows based on a condition, e.g. "customers with score above 80"
- final_answer: the last step, produces the data the LLM will use to answer

THE needsLLMAfter FIELD:
Set to true only on the final step. Set to false on all others.

EXAMPLE:
User question: "Show me total revenue by region for customers with score above 80"
Execution plan:
1. filter | SELECT * FROM data WHERE score > 80 | → step_1_result | needsLLMAfter: false
2. aggregate | SELECT region, SUM(revenue) AS total_revenue FROM step_1_result GROUP BY region LIMIT 200 | → step_2_result | needsLLMAfter: true

Respond with your reasoning first, then the execution plan."""

HUMAN_PROMPT = """Recent conversation:
{history}

User's message: {message}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

def planner(state: GraphState) -> dict:
    try:
        chain = prompt | llm
        result: ExecutionPlan = chain.invoke({
            "schema": format_schema(state["schema"]),
            "history": format_history(state["history"]),
            "message": state["message"],
        })
        print(f"[planner] reasoning: {result.reasoning}")
        print(f"[planner] execution_plan: {result.execution_plan}")
        return {"execution_plan": result.execution_plan}

    except Exception as e:
        print(f"[planner] error: {e}")
        return {"execution_plan": None}