import React from "react"
import type { DisplayMessage } from "../types/app"

interface MessageBubbleProps {
    message: DisplayMessage
    onSend: (message: string) => void
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onSend }) => {

    const renderContent = () => {
        // User message — plain string
        if (typeof message.content === "string") {
            return <p>{message.content}</p>
        }

        switch (message.content.type) {
            case "answer":
                return (
                    <div>
                        <p>{message.content.text}</p>

                        {message.content.insights && (
                            <p className="mt-2 text-sm text-gray-600 italic">
                                💡 {message.content.insights}
                            </p>
                        )}

                        {message.content.followUps && message.content.followUps.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-2">
                                {message.content.followUps.map((followUp, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => onSend(followUp)}
                                        className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
                                    >
                                        {followUp}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                )

            case "clarification":
                return (
                    <div>
                        <p className="mb-2">{message.content.question}</p>
                    </div>
                )

            case "execution_plan":
                return (
                    <div>
                        <p className="font-medium mb-1">
                            Running {message.content.estimatedStepCount} step{message.content.estimatedStepCount > 1 ? "s" : ""}:
                        </p>
                        <ol className="ml-4 list-decimal space-y-1">
                            {message.content.steps.map((step) => (
                                <li key={step.stepNumber} className="text-sm">
                                    {step.description}
                                </li>
                            ))}
                        </ol>
                    </div>
                )

            case "no_data":
                return (
                    <p className="text-yellow-700">
                        ⚠️ {message.content.reason}
                    </p>
                )

            case "fixed_sql":
                return (
                    <div>
                        <p className="mb-1">
                            Corrected SQL for step {message.content.stepNumber}:
                        </p>
                        <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
                            {message.content.sql}
                        </pre>
                        <p className="mt-1 text-sm text-gray-600">
                            {message.content.explanation}
                        </p>
                    </div>
                )

            case "error":
                return (
                    <p className="text-red-600">
                        ❌ {message.content.message}
                    </p>
                )

            default:
                return (
                    <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                        {JSON.stringify(message.content, null, 2)}
                    </pre>
                )
        }
    }

    const isUser = message.role === "user"

    return (
        <div className={`max-w-xl p-4 rounded-lg mb-2 ${
            isUser
                ? "bg-blue-100 self-end ml-auto"
                : "bg-gray-100 self-start"
        }`}>
            {renderContent()}
        </div>
    )
}