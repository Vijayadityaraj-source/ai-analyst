import type { ColumnSchema, SheetRow } from "./sheet"

export interface ConversationTurn{
    role : 'assistant' | 'user',
    content : string
}

export interface SqlError {
    failedSql: string
    errorMessage: string
    stepNumber: number
}

export interface ChatRequest{
    schema : ColumnSchema[],
    message : string,
    history : ConversationTurn[],
    sessionId : string //crypto.randomUUID() in react app
    sqlError?: SqlError
    queryResult?: SheetRow[]
}

interface ClarificationResponse{
    type : 'clarification',
    question : string
}

interface AnswerResponse{
    type : 'answer',
    text : string,
    // chartSpec?: ChartSpec
    insights?: string, 
    followUps?: string[]
}

interface NoDataResponse{
    type : 'no_data',
    reason : string
}

interface ErrorResponse{
    type: 'error'
    message: string 
}

interface FixedSQLResponse {
    type: 'fixed_sql'
    stepNumber: number      // which step was fixed — so frontend knows which to replace
    sql: string             // the corrected SQL
    explanation: string     // what changed — shown to user as a status message
}

export interface ExecutionPlanResponse {
    type: 'execution_plan'
    steps: ExecutionStep[]
    estimatedStepCount: number
}

export interface ExecutionStep {
    stepNumber: number
    type: 'derive' | 'aggregate' | 'filter' | 'final_answer'
    sql: string
    outputTableName: string
    description: string      // "Calculating profit margin per region"
    needsLLMAfter: boolean   // true on the last step — triggers answer generation
}

export type ChatResponse = 
    | ClarificationResponse
    | AnswerResponse
    | NoDataResponse
    | ErrorResponse
    | FixedSQLResponse
    | ExecutionPlanResponse
