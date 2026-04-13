from typing import Optional, Literal, List, Dict, Union, Annotated
from pydantic import BaseModel, Field

# ── Shared types ────────────────────────────────────────────────────

ColumnType = Literal['number', 'string', 'date', 'boolean']

class ColumnSchema(BaseModel):
    name: str
    type: ColumnType
    uniqueCount: int
    nullCount: int
    sampleValues: List[Union[str, int, float, bool, None]]

class ConversationTurn(BaseModel):
    role: Literal['user', 'assistant']
    content: str

class SqlError(BaseModel):
    failedSql: str
    errorMessage: str
    stepNumber: int

# ── Request ─────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    schema: List[ColumnSchema]        
    history: List[ConversationTurn]   
    sessionId: str
    sqlError: Optional[SqlError] = None
    queryResult: Optional[List[Dict]] = None  # final step result rows

# ── Response variants ────────────────────────────────────────────────

class ClarificationResponse(BaseModel):
    type: Literal['clarification']
    question: str

class AnswerResponse(BaseModel):
    type: Literal['answer']
    text: str
    # chartSpec: Optional[ChartSpec] = None  TODO Phase 4
    insights: Optional[str] = None
    followUps: Optional[List[str]] = None

class ExecutionStep(BaseModel):
    stepNumber: int
    type: Literal['derive', 'aggregate', 'filter', 'final_answer']
    sql: str
    outputTableName: str
    description: str
    needsLLMAfter: bool

class ExecutionPlanResponse(BaseModel):
    type: Literal['execution_plan']
    steps: List[ExecutionStep]
    estimatedStepCount: int

class NoDataResponse(BaseModel):
    type: Literal['no_data']
    reason: str

class ErrorResponse(BaseModel):
    type: Literal['error']
    message: str

class FixedSQLResponse(BaseModel):
    type: Literal['fixed_sql']
    stepNumber: int      
    sql: str             # the corrected SQL
    explanation: str  

# ── Union ────────────────────────────────────────────────────────────

ChatResponse = Annotated[
    Union[
        ClarificationResponse,
        AnswerResponse,
        ExecutionPlanResponse,
        NoDataResponse,
        ErrorResponse,
        FixedSQLResponse
    ],
    Field(discriminator='type')
]
