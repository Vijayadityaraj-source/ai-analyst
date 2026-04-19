import { useCallback } from "react"
import type { Dispatch } from "react"
import type { AppState } from "../types/app"
import type { ChatResponse } from "../types/api"
import { sendMessage as sendMessageApi } from "../api/chat"
import type { Action } from "./useAppState"

export function useChat(state: AppState, dispatch: Dispatch<Action>) {

    const sendMessage = useCallback(async (userInput: string) => {

        if (!state.parsedFile) {
            dispatch({
                type: "ADD_ASSISTANT_MESSAGE",
                payload: { type: "error", message: "Please upload a file before asking a question." }
            })
            return
        }

        dispatch({ type: "ADD_USER_MESSAGE", payload: userInput })
        dispatch({ type: "SET_LOADING", payload: true })
        dispatch({ type: "SET_LOADING_STATUS", payload: "Analysing your question..." })

        try {
            const response: ChatResponse = await sendMessageApi({
                message: userInput,
                schema: state.parsedFile.schema,
                history: state.history,
                sessionId: state.sessionId
            })

            if (response.type === "execution_plan") {
                dispatch({ type: "SET_EXECUTION_PLAN", payload: response.steps })
                // TODO Phase 3: trigger DuckDB-WASM execution here
            }

            dispatch({ type: "ADD_ASSISTANT_MESSAGE", payload: response })

        } catch (error: unknown) {
            const message = error instanceof Error
                ? error.message
                : "Something went wrong"

            dispatch({
                type: "ADD_ASSISTANT_MESSAGE",
                payload: { type: "error", message }
            })

        } finally {
            dispatch({ type: "SET_LOADING", payload: false })
            dispatch({ type: "SET_LOADING_STATUS", payload: "" })  // ← clear
        }

    }, [state.parsedFile, state.history, state.sessionId, dispatch])

    return { sendMessage }
}