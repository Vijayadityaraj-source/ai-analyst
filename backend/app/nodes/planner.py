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
- Only reference column names that exist in the schema above.
- Boolean values in DuckDB SQL are lowercase: true and false, not True and False.

STEP TYPES — use exactly these values for the `type` field:
- derive: adds new columns to existing rows
- aggregate: groups and summarises rows
- filter: removes rows based on a condition
- final_answer: the last step, produces the data the LLM will use to answer

THE needsLLMAfter FIELD:
- The LAST step must ALWAYS have needsLLMAfter: true
- Every other step must have needsLLMAfter: false
- Exactly one step gets needsLLMAfter: true — always the last one

EFFICIENCY RULE:
Only create multiple steps when the output of one step is genuinely needed 
as input to the next. Never create a step that just does SELECT * FROM data.
Query data directly whenever possible.

COMPLETENESS RULE:
Your execution_plan list must contain EVERY step you describe in your reasoning.
If your reasoning says "first filter, then aggregate" — BOTH steps must appear 
in the execution_plan list. Count your steps: estimatedStepCount must equal 
the exact number of ExecutionStep objects in your list.

EXAMPLE OF A CORRECT MULTI-STEP PLAN:
User question: "Show me total revenue for active customers grouped by region"
reasoning: "First filter active customers, then aggregate by region"
execution_plan:
  Step 1 — filter | SELECT * FROM data WHERE Active = true | step_1_result | needsLLMAfter: false
  Step 2 — aggregate | SELECT Region, SUM(Revenue) AS total_revenue FROM step_1_result GROUP BY Region LIMIT 200 | step_2_result | needsLLMAfter: true
estimatedStepCount: 2

Notice: BOTH steps appear. The filter step references data directly. 
The aggregate step references step_1_result, not data.

EXAMPLE OF A CORRECT SINGLE-STEP PLAN:
User question: "What is total revenue by region?"
reasoning: "One aggregate step is enough"
execution_plan:
  Step 1 — aggregate | SELECT Region, SUM(Revenue) AS total_revenue FROM data GROUP BY Region LIMIT 200 | step_1_result | needsLLMAfter: true
estimatedStepCount: 1

Respond with your reasoning first, then the execution plan.
CRITICAL: The type field for each step must be exactly one of these lowercase strings: derive, aggregate, filter, final_answer"""

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