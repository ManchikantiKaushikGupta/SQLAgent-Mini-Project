"""
LangGraph Workflow Definition

Connects individual agents into a cohesive cycle, managing query text
refinement, execution planning, SQL generation, and safe validation logic.
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from core.state import SQLAgentState
from features.intent_clarification.agent import clarify_intent
from features.query_planning.agent import generate_query_plan
from features.sql_generation.agent import generate_sql
from features.validation_correction.agent import validate_sql_safety, correct_sql

MAX_RETRIES = 3

def node_clarify_intent(state: SQLAgentState):
    refined = clarify_intent(state["original_query"], state.get("db_schema", ""))
    return {"refined_query": refined}

def node_query_planning(state: SQLAgentState):
    plan = generate_query_plan(state["refined_query"], state.get("db_schema", ""))
    return {"query_plan": plan}

def node_sql_generation(state: SQLAgentState):
    sql = generate_sql(state["query_plan"], state.get("db_schema", ""))
    return {"sql_query": sql, "error_message": None, "retry_count": 0}

def node_validate_sql(state: SQLAgentState):
    sql = state.get("sql_query", "")
    try:
        # Validates syntax and safety via SQLGlot
        validate_sql_safety(sql, dialect="postgres")
        return {"error_message": None}
    except Exception as e:
        return {"error_message": str(e)}

def node_correct_sql(state: SQLAgentState):
    corrected_sql = correct_sql(
        failed_sql=state["sql_query"],
        error_message=state["error_message"],
        schema=state.get("db_schema", ""),
        original_query=state.get("refined_query") or state["original_query"]
    )
    # Increment retry counter
    current_retries = state.get("retry_count", 0)
    return {"sql_query": corrected_sql, "retry_count": current_retries + 1, "error_message": None}

def node_execute_sql(state: SQLAgentState):
    # TO DO: Connect to db/database.py once PostgreSQL connection setup is ready
    return {"final_result": "Pending DB execution mapping"}

def decide_next_after_validation(state: SQLAgentState) -> Literal["execute", "correct", "end"]:
    """Conditional Edge routing after checking SQL validity."""
    if not state.get("error_message"):
        return "execute"  # Validation passed
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "end"      # Out of retries
    return "correct"      # Try again

def build_workflow():
    """Compiles and returns the LangGraph application."""
    workflow = StateGraph(SQLAgentState)

    # Add Nodes
    workflow.add_node("clarify", node_clarify_intent)
    workflow.add_node("plan", node_query_planning)
    workflow.add_node("generate", node_sql_generation)
    workflow.add_node("validate", node_validate_sql)
    workflow.add_node("correct", node_correct_sql)
    workflow.add_node("execute_db", node_execute_sql)

    # Add Edges (linear flow for generation)
    workflow.set_entry_point("clarify")
    workflow.add_edge("clarify", "plan")
    workflow.add_edge("plan", "generate")
    workflow.add_edge("generate", "validate")

    # Add Conditional Edges based on validation success
    workflow.add_conditional_edges(
        "validate",
        decide_next_after_validation,
        {
            "execute": "execute_db",
            "correct": "correct",
            "end": END
        }
    )

    # Loop back from correct to validate to re-check the fixed SQL
    workflow.add_edge("correct", "validate")
    workflow.add_edge("execute_db", END)

    return workflow.compile()
