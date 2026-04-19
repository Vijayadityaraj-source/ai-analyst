import type { ChatRequest, ChatResponse } from '../types/api'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
    })

    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json() as ChatResponse
}
