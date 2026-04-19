import { useReducer } from "react"
import type { Dispatch } from "react" 
import type { ParsedFile } from "../types/sheet"
import type { ChatResponse, ConversationTurn, ExecutionStep } from "../types/api"
import type { AppState, DisplayMessage } from "../types/app"

export type Action =
    | { type: 'SET_FILE'; payload: ParsedFile }
    | { type: 'ADD_USER_MESSAGE'; payload: string }
    | { type: 'ADD_ASSISTANT_MESSAGE'; payload: ChatResponse }
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'SET_EXECUTION_PLAN'; payload: ExecutionStep[] }
    | { type: 'CLEAR_EXECUTION_PLAN' }
    | { type: 'CLEAR_SESSION' }
    | { type: 'SET_LOADING_STATUS'; payload: string }

function serializeChatResponse(response: ChatResponse): string {
    if (!response) return ""

    switch (response.type) {
        case "answer":
            return `answer: ${response.text}`

        case "execution_plan":
            const stepDescriptions = response.steps
                .map(s=>s.description)
                .join(", ")
            return `execution_plan: ${response.steps.length} steps - ${stepDescriptions}`

        case "clarification":
            return `clarification: ${response.question}`

        case "no_data":
            return `no_data: ${response.reason}`

        case "fixed_sql":
            return `fixed_sql: corrected step ${response.stepNumber} — ${response.explanation}`
            
        case "error":
            return `error: ${response.message}`

        default:
            return `${(response as any).type}`
    }
}

const initialState: AppState = {
    parsedFile: null,
    sessionId: crypto.randomUUID(),
    history: [],
    messages: [],
    isLoading: false,
    executionPlan: [],
    loadingStatus: ''
}

function reducer(state: AppState, action: Action): AppState {
    switch (action.type) {
        case 'SET_FILE':
            return { 
                ...state, 
                parsedFile: action.payload,
                history: [],                    // reset on new file
                messages: [],
                executionPlan: [],
                isLoading: false
            }

        case 'ADD_USER_MESSAGE':{
                const newMessage: DisplayMessage = {
                    id: crypto.randomUUID(),
                    role: 'user',
                    timestamp: new Date(), 
                    content: action.payload
                }
                const newHistory: ConversationTurn = {
                    role: 'user',
                    content: action.payload
                }
                return {
                    ...state,
                    messages: [...state.messages, newMessage],
                    history: [...state.history, newHistory]
                }
            }

        case 'ADD_ASSISTANT_MESSAGE':{
                const newMessage: DisplayMessage = {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    timestamp: new Date(),
                    content: action.payload
                }
                const newHistory: ConversationTurn = {
                    role: 'assistant',
                    content: serializeChatResponse(action.payload)
                }
                return {
                    ...state,
                    messages: [...state.messages, newMessage],
                    history: [...state.history, newHistory]
                }
            }

        case 'SET_LOADING':
            return { 
                ...state, 
                isLoading: action.payload 
            }

        case 'SET_EXECUTION_PLAN':
            return { 
                ...state, 
                executionPlan: action.payload 
            }  

        case 'CLEAR_EXECUTION_PLAN':
            return { 
                ...state, 
                executionPlan: [] 
            }

        case 'CLEAR_SESSION':
            return {
                ...state,
                parsedFile: null,
                history: [],
                messages: [],
                executionPlan: [],
                isLoading: false
            }

        case 'SET_LOADING_STATUS':
            return { 
                ...state, 
                loadingStatus: action.payload 
            }

        default:
            return state
    }
}

export function useAppState(): [AppState, Dispatch<Action>] {
    return useReducer(reducer, initialState)
}