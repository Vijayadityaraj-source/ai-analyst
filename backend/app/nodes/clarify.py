from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.state import GraphState
from app.utils import make_llm, format_schema, format_history

class Clarification(BaseModel):
    reasoning: str  # always put reasoning FIRST, LLM fills this before intent
    clarification_question: str

llm = make_llm(Clarification, temperature=0)

SYSTEM_PROMPT = """You are a clarification assistant for a data analysis tool.
The user has asked a question that is ambiguous — it cannot be answered without more information.
Your job is to ask ONE specific clarifying question that resolves the ambiguity.

The user has uploaded a spreadsheet with the following schema:
{schema}

RULES FOR A GOOD CLARIFYING QUESTION:
- Reference the specific column name or term that is ambiguous
- Offer 2-3 concrete options where possible rather than asking open-ended questions
- Ask about only ONE ambiguity — the most important one
- Never ask a generic question like "Could you clarify?" or "What do you mean?"

EXAMPLES:
Bad:  "Could you please clarify your question?"
Good: "The column 'val' could refer to revenue or quantity — which did you mean?"

Bad:  "What kind of breakdown would you like?"
Good: "Would you prefer the breakdown as a bar chart, a summary table, or plain text?"

Bad:  "Which data are you interested in?"
Good: "There is no 'profit' column in this sheet. Should I calculate it as Revenue minus Cost?"
"""

HUMAN_PROMPT = """Recent conversation:
{history}

User's message: {message}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

def clarify(state: GraphState) -> dict:
    try:
        chain = prompt | llm
        
        result: Clarification = chain.invoke({
            "schema": format_schema(state["schema"]),
            "history": format_history(state["history"]),
            "message": state["message"],
        })
        
        # Log reasoning during development — remove or move to proper
        # logging before production
        print(f"[clarify] reasoning: {result.reasoning}")
        print(f"[clarify] clarification_question: {result.clarification_question}")
        
        return {"clarification_question": result.clarification_question}

    except Exception as e:
        # Safe fallback — treat errors as ambiguous so the graph
        # routes to the clarify node rather than crashing
        print(f"[clarify] error: {e}")
        return {"clarification_question": "I need more information to answer that. Could you tell me which columns you're interested in?"}