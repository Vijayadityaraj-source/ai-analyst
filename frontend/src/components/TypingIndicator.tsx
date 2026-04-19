interface TypingIndicatorProps {
    status: string
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ status }) => {
    return (
        <div className="flex items-center gap-3 p-4 bg-gray-100 rounded-lg max-w-xs">
            <div className="flex gap-1">
                <span className="dot-flicker w-2 h-2 bg-gray-400 rounded-full inline-block" />
                <span className="dot-flicker w-2 h-2 bg-gray-400 rounded-full inline-block" />
                <span className="dot-flicker w-2 h-2 bg-gray-400 rounded-full inline-block" />
            </div>
            <span className="text-sm text-gray-500">
                {status || "Thinking..."}
            </span>
        </div>
    )
}