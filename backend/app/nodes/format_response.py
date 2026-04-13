from app.state import GraphState


def format_response(state: GraphState) -> dict:
    """
    Assembles the final ChatResponse dict based on which state fields
    were populated during the graph run. Each branch maps to one
    ChatResponse variant. format_response never calls an LLM.
    """

    if state.get("fixed_sql_result"): #FixedSQLResult
        r = state["fixed_sql_result"]
        return {
            "response": {
                "type": "fixed_sql",          
                "sql": r.sql,
                "explanation": r.explanation,
                "stepNumber": r.stepNumber
            }
        }

    if state.get("clarification_question"): #ClarificationResponse
        return {
            "response": {
                "type": "clarification",
                "question": state["clarification_question"]
            }
        }

    if state.get("execution_plan"): #ExecutionPlanResponse
        steps = state["execution_plan"]
        return {
            "response": {
                "type": "execution_plan",
                "steps": [s.model_dump() for s in steps],   
                "estimatedStepCount": len(steps)
            }
        }

    if state.get("generated_answer"): #AnswerResponse
        a = state["generated_answer"]
        return {
            "response": {
                "type": "answer",
                "text": a.text,
                "insights": a.insights,
                "followUps": a.followUps
            }
        }

    if state.get("intent") == "no_data": #NoDataResponse
        return {
            "response": {
                "type": "no_data",
                "reason": "No relevant data was found in the spreadsheet to answer your question."
            }
        }

    # ErrorResponse
    return { 
        "response": {
            "type": "error",
            "message": "An unexpected error occurred. Please try again."   
        }
    }