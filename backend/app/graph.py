from langgraph.graph import StateGraph, START, END

from app.state import GraphState
from app.nodes.classify_intent import classify_intent
from app.nodes.clarify import clarify
from app.nodes.planner import planner
from app.nodes.fix_sql import fix_sql
from app.nodes.generate_answer import generate_answer
from app.nodes.format_response import format_response

def route_after_classification(state: GraphState) -> str:
    intent = state.get("intent")
    if intent == "ambiguous":
        return "clarify"
    if intent == "data_question":
        return "planner"
    if intent == "general_question":
        return "generate_answer"
    if intent == "no_data":
        return "format_response"
    return "format_response"

def route_entry(state: GraphState) -> str:
    return state.get("entry_point", "classify_intent")


def build_graph() -> StateGraph:
    builder = StateGraph(GraphState)

    # ── Register nodes ───────────────────────────────────────────────
    builder.add_node("classify_intent", classify_intent)
    builder.add_node("clarify", clarify)
    builder.add_node("planner", planner)
    builder.add_node("fix_sql", fix_sql)
    builder.add_node("generate_answer", generate_answer)
    builder.add_node("format_response", format_response)

    # ── Entry point ──────────────────────────────────────────────────
    # main.py overrides this per request — START here is the default
    builder.add_conditional_edges(START, route_entry, {
        "classify_intent": "classify_intent",
        "fix_sql": "fix_sql",
        "generate_answer": "generate_answer",
    })

    # ── Conditional edge after classification ────────────────────────
    builder.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "clarify": "clarify",
            "planner": "planner",
            "generate_answer": "generate_answer",
            "format_response": "format_response",
        }
    )

    # ── Linear edges — all terminal nodes go to format_response ──────
    builder.add_edge("clarify", "format_response")
    builder.add_edge("planner", "format_response")
    builder.add_edge("fix_sql", "format_response")
    builder.add_edge("generate_answer", "format_response")

    # ── Exit ─────────────────────────────────────────────────────────
    builder.add_edge("format_response", END)

    return builder.compile()


graph = build_graph()