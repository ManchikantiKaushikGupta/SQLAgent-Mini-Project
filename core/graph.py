from langgraph.graph import StateGraph, END
from typing import Dict, Any

from .state import AgentState
from features.intent_clarification.agent import clarify_intent

# --- Placeholder Agent Nodes ---

def intent_clarification_node(state: AgentState) -> Dict[str, Any]:
    print(f"--- Intent Clarification ---")
    print(f"Original Query: {state['query']}")
    refined_query = clarify_intent(state["query"])
    print(f"Refined Query:  {refined_query}")
    return {"refined_query": refined_query}

def query_planning_node(state: AgentState) -> Dict[str, Any]:
    print(f"--- Query Planning ---")
    # Dummy processing
    plan = f"Plan to execute: {state['refined_query']}"
    return {"plan": plan}

def sql_generation_node(state: AgentState) -> Dict[str, Any]:
    print(f"--- SQL Generation ---")
    # Dummy processing returning a safe SQL query
    sql_query = "SELECT * FROM users LIMIT 10;"
    return {"sql_query": sql_query}

def validation_correction_node(state: AgentState) -> Dict[str, Any]:
    print(f"--- Validation & Correction ---")
    print(f"SQL Query to execute: {state.get('sql_query')}")
    
    # In the future, here we would:
    # 1. Validate the SQL with SQLGlot
    # 2. Execute via SQLAlchemy
    # 3. Handle errors and possibly route back to SQL Generation
    
    # Dummy results
    results = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    return {"results": results, "error": None}

# --- Build the Graph ---

def build_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("intent_clarification", intent_clarification_node)
    workflow.add_node("query_planning", query_planning_node)
    workflow.add_node("sql_generation", sql_generation_node)
    workflow.add_node("validation_correction", validation_correction_node)

    # Add edges
    workflow.add_edge("intent_clarification", "query_planning")
    workflow.add_edge("query_planning", "sql_generation")
    workflow.add_edge("sql_generation", "validation_correction")
    workflow.add_edge("validation_correction", END)

    # Set entry point
    workflow.set_entry_point("intent_clarification")

    # Compile the graph
    app = workflow.compile()
    return app
