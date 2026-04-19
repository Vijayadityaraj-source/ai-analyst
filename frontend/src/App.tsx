import React from "react"
import * as XLSX from "xlsx"
import "./App.css"
import { parseSheet } from "./utils/parseSheet"
import { useAppState } from "./hooks/useAppState"
import { useChat } from "./hooks/useChat"
import { MessageList } from "./components/MessageList"
import { ChatInput } from "./components/ChatInput"

function App() {
    const [state, dispatch] = useAppState()
    const { sendMessage } = useChat(state, dispatch)

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        const reader = new FileReader()
        reader.onload = (event) => {
            const binaryStr = event.target?.result
            if (!binaryStr) return

            const workbook = XLSX.read(binaryStr, {
                type: "binary",
                cellDates: true,
            })

            const sheetName = workbook.SheetNames[0]
            const parsed = parseSheet(workbook, sheetName)
            dispatch({ type: "SET_FILE", payload: parsed })
        }
        reader.readAsBinaryString(file)
    }

    // ── Upload screen ─────────────────────────────────────────────
    if (!state.parsedFile) {
        return (
            <div className="h-screen flex flex-col items-center justify-center gap-4">
                <h1 className="text-2xl font-bold">AI Analyst</h1>
                <p className="text-gray-500">Upload an Excel file to get started</p>
                <label className="cursor-pointer px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    Upload File
                    <input
                        type="file"
                        accept=".xlsx,.xls,.csv"
                        onChange={handleFileUpload}
                        className="hidden"
                    />
                </label>
            </div>
        )
    }

    // ── Chat screen ───────────────────────────────────────────────
    return (
        <div className="flex flex-col h-screen">

            {/* Header */}
            <div className="p-4 border-b flex justify-between items-center bg-white">
                <div>
                    <span className="font-medium">{state.parsedFile.sheetName}</span>
                    <span className="ml-2 text-sm text-gray-500">
                        {state.parsedFile.rowCount} rows · {state.parsedFile.schema.length} columns
                    </span>
                </div>
                <button
                    onClick={() => dispatch({ type: "CLEAR_SESSION" })}  // ← correct action
                    className="text-sm text-gray-500 hover:text-red-500"
                >
                    Clear session
                </button>
            </div>

            {/* Message list — flex-1 makes it fill remaining height */}
            <div className="flex-1 overflow-y-auto p-4">
                <MessageList
                    messages={state.messages}
                    onSend={sendMessage}
                    isLoading={state.isLoading}
                    loadingStatus={state.loadingStatus}
                />
            </div>

            {/* Chat input — pinned to bottom */}
            <div className="p-4 border-t bg-white">
                <ChatInput
                    onSend={sendMessage}
                    isLoading={state.isLoading}
                />
            </div>

        </div>
    )
}

export default App