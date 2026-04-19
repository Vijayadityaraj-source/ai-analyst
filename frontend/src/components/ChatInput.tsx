import React, { useState } from "react"

interface ChatInputProps {
    onSend: (message: string) => void
    isLoading: boolean
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading }) => {
    const [inputValue, setInputValue] = useState("")

    const handleSend = () => {
        if (inputValue.trim() === "") return
        onSend(inputValue.trim())
        setInputValue("")
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            handleSend()
        }
    }

    return (
        <div className="flex mt-4">
            <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                placeholder={isLoading ? "Waiting for response..." : "Type your message..."}
                className="flex-1 py-2 px-4 text-lg"
            />
            <button 
                onClick={handleSend}
                disabled={isLoading || inputValue.trim() === ""}
                className="ml-4 py-2 px-4 text-lg disabled:opacity-50"
            >
                Submit
            </button>
        </div>
    )
}