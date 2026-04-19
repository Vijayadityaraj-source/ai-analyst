import React, { useEffect, useRef } from "react"
import type { DisplayMessage } from "../types/app"
import { MessageBubble } from "./MessageBubble"
import { TypingIndicator } from "./TypingIndicator"

interface MessageListProps {
    messages: DisplayMessage[]
    onSend: (message: string) => void
    isLoading: boolean
    loadingStatus: string
}

export const MessageList: React.FC<MessageListProps> = ({ messages, onSend, isLoading, loadingStatus }) => {
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, isLoading]) // ← also scroll when loading state changes

    return (
        <div className="flex flex-col space-y-4">
            {messages.map((message) => (
                <MessageBubble
                    key={message.id}
                    message={message}
                    onSend={onSend}
                />
            ))}

            {isLoading && <TypingIndicator status={loadingStatus} />}  {/* ← appears while waiting */}

            <div ref={bottomRef} />
        </div>
    )
}