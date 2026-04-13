from typing import Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.state import GraphState
from app.utils import make_llm, format_schema, format_history


class IntentClassification(BaseModel):
    reasoning: str  # always put reasoning FIRST, LLM fills this before intent
    intent: Literal['ambiguous', 'data_question', 'general_question', 'no_data']


llm = make_llm(IntentClassification, temperature=0)

SYSTEM_PROMPT = """You are an intent classifier for a data analysis tool. \
Your only job is to read the user's message and classify it into exactly one intent. \
You do not answer questions. You do not generate SQL. You only classify.

The user has uploaded a spreadsheet with the following schema:
{schema}

Intent definitions — read these carefully before classifying:

AMBIGUOUS: The question cannot be answered without more information.
  Use this when column names are unclear, the question has multiple valid 
  interpretations, or a key term does not map to any column in the schema.
  Examples:
    - "show me the numbers" (which numbers? no column called 'numbers')
    - "what is the value?" (value of what? multiple columns could apply)
    - "compare the results" (compare which columns? over what?)

DATA_QUESTION: The question requires reading, filtering, or aggregating 
  actual data rows to answer. The schema alone is not enough.
  Examples:
    - "what is total revenue by region?" (needs aggregation)
    - "show me customers with score above 90" (needs filtering)
    - "add a profit column = revenue minus cost" (needs row-level transform)
    - "create a pivot table of sales by month and region" (needs aggregation)

GENERAL_QUESTION: The question can be answered using only the schema metadata —
  column names, types, null counts, unique counts. No data rows needed.
  Examples:
    - "what columns does this sheet have?" (schema answers this)
    - "which columns have missing values?" (nullCount answers this)
    - "what type is the JoiningDate column?" (schema answers this)

NO_DATA: The sheet clearly contains no information relevant to the question.
  The column names and types make it impossible to answer.
  Examples:
    - asking about inventory when the sheet only has HR data
    - asking about geographic data when no location columns exist

The boundary between AMBIGUOUS and DATA_QUESTION:
  If you can identify WHICH columns the question refers to → DATA_QUESTION
  If you cannot map the question to specific columns → AMBIGUOUS

Respond with your reasoning first, then the intent."""

HUMAN_PROMPT = """Recent conversation:
{history}

User's message: {message}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

def classify_intent(state: GraphState) -> dict:
    try:
        chain = prompt | llm
        
        result: IntentClassification = chain.invoke({
            "schema": format_schema(state["schema"]),
            "history": format_history(state["history"]),
            "message": state["message"],
        })
        
        # Log reasoning during development — remove or move to proper
        # logging before production
        # print(f"[classify_intent] reasoning: {result.reasoning}")
        # print(f"[classify_intent] intent: {result.intent}")
        
        return {"intent": result.intent}

    except Exception as e:
        # Safe fallback — treat errors as ambiguous so the graph
        # routes to the clarify node rather than crashing
        # print(f"[classify_intent] error: {e}")
        return {"intent": "ambiguous"}