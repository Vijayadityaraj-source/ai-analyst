import type { ParsedFile } from "./sheet"
import type { ChatResponse, ExecutionStep, ConversationTurn } from "./api"

export interface DisplayMessage {
    id : string                         // crypto.randomUUID() when message is created
    role: 'assistant' | 'user'
    timestamp: Date
    content: string | ChatResponse 
}

export interface AppState {
    parsedFile: ParsedFile | null       // from Phase 1
    sessionId: string                   // crypto.randomUUID() on mount
    history: ConversationTurn[]         // grows with each exchange
    messages: DisplayMessage[]          // what MessageList renders
    isLoading: boolean                  // disables input while waiting
    executionPlan: ExecutionStep[]      // stored between round trips
    loadingStatus: string
}

