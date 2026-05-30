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
from features.validation_correction.semantic_validator import validate_sql_semantics
from db.database import execute_sql_query
import logging
from observability import (
    init_metrics_state,
    track_latency,
    record_validation,
    record_correction,
    record_execution
)
from core.security import get_security_manager, SecurityException

MAX_RETRIES = 3

logger = logging.getLogger("SQLAgent.Graph")
logger.setLevel(logging.INFO)

def node_clarify_intent(state: SQLAgentState):
    init_metrics_state(state)
    sec_mgr = get_security_manager()
    # Redact input PII before passing to intent clarification and downstream agents
    state["original_query"] = sec_mgr.redactor.redact_text(state["original_query"])
    with track_latency(state, "intent_clarification"):
        refined = clarify_intent(state["original_query"], state.get("db_schema", ""))
    return {"original_query": state["original_query"], "refined_query": refined, "metrics": state["metrics"]}

def node_retrieve_schema(state: SQLAgentState):
    query = state.get("refined_query") or state["original_query"]
    logger.info("Executing Schema Retrieval stage...")
    init_metrics_state(state)
    with track_latency(state, "schema_retrieval"):
        try:
            from retrieval.schema_retriever import get_schema_retriever
            retriever = get_schema_retriever()
            retrieved = retriever.retrieve(query)
            
            # Prune retrieved schema based on RBAC role
            role = state.get("user_role") or "restricted_user"
            sec_mgr = get_security_manager()
            pruned_schema = sec_mgr.prune_schema_for_role(retrieved, role)
            state["db_schema"] = pruned_schema
        except Exception as e:
            logger.error(f"Error during schema retrieval: {e}. Falling back to original schema.")
            role = state.get("user_role") or "restricted_user"
            sec_mgr = get_security_manager()
            pruned_schema = sec_mgr.prune_schema_for_role(state.get("db_schema", ""), role)
            state["db_schema"] = pruned_schema
    return {"db_schema": pruned_schema, "metrics": state["metrics"]}

def node_query_planning(state: SQLAgentState):
    init_metrics_state(state)
    with track_latency(state, "query_planning"):
        plan = generate_query_plan(state["refined_query"], state.get("db_schema", ""))
    return {"query_plan": plan, "metrics": state["metrics"]}

def node_sql_generation(state: SQLAgentState):
    init_metrics_state(state)
    with track_latency(state, "sql_generation"):
        sql = generate_sql(state["query_plan"], state.get("db_schema", ""))
    return {"sql_query": sql, "error_message": None, "retry_count": 0, "metrics": state["metrics"]}

def node_validate_sql(state: SQLAgentState):
    sql = state.get("sql_query", "")
    init_metrics_state(state)
    with track_latency(state, "syntax_validation"):
        try:
            # 1. Validates syntax and safety via SQLGlot
            validate_sql_safety(sql, dialect="postgres")
            
            # 2. Validate RBAC permissions and apply limit clamping
            role = state.get("user_role") or "restricted_user"
            username = state.get("username") or "anonymous"
            sec_mgr = get_security_manager()
            safe_sql = sec_mgr.validate_sql_security(sql, role_name=role, username=username)
            
            record_validation(state, "syntax", True, "SQL syntax, RBAC, and limit checks passed successfully.")
            return {"sql_query": safe_sql, "error_message": None, "security_error": None, "metrics": state["metrics"]}
        except SecurityException as sec_err:
            # Terminal security violation: abort the correction retry loops!
            logger.error(f"Terminal Security Violation: {sec_err}")
            record_validation(state, "syntax", False, f"Security Exception: {sec_err}")
            return {
                "error_message": f"Security Exception: {sec_err}",
                "security_error": str(sec_err),
                "retry_count": MAX_RETRIES,  # Aborts correction path
                "metrics": state["metrics"]
            }
        except Exception as e:
            record_validation(state, "syntax", False, str(e))
            return {"error_message": str(e), "metrics": state["metrics"]}

def node_correct_sql(state: SQLAgentState):
    failed_sql = state["sql_query"]
    error_msg = state["error_message"]
    current_retries = state.get("retry_count", 0)
    init_metrics_state(state)
    with track_latency(state, f"sql_correction_attempt_{current_retries + 1}"):
        correction_result = correct_sql(
            failed_sql=failed_sql,
            error_message=error_msg,
            schema=state.get("db_schema", ""),
            original_query=state.get("refined_query") or state["original_query"]
        )
        corrected_sql = correction_result.corrected_sql
        thought_process = correction_result.thought_process
    record_correction(
        state=state,
        attempt_number=current_retries + 1,
        failed_sql=failed_sql,
        error_message=error_msg,
        corrected_sql=corrected_sql,
        thought_process=thought_process,
        error_classification=correction_result.error_classification
    )
    return {"sql_query": corrected_sql, "retry_count": current_retries + 1, "error_message": None, "metrics": state["metrics"]}


def node_execute_sql(state: SQLAgentState):
    sql = state.get("sql_query")
    init_metrics_state(state)
    if not sql:
        record_execution(state, False, error="No SQL query to execute.")
        return {"final_result": None, "error_message": "No SQL query to execute.", "metrics": state["metrics"]}
        
    with track_latency(state, "database_execution"):
        try:
            # Connects to PostgreSQL and fetches results mapping
            results = execute_sql_query(sql)
            
            # Redact/mask results if role is not authorized to see raw PII
            role = state.get("user_role") or "restricted_user"
            sec_mgr = get_security_manager()
            role_perms = sec_mgr.get_role_permissions(role)
            redacted_results = sec_mgr.redactor.redact_results(results, role_perms)
            
            record_execution(state, True, len(redacted_results) if redacted_results else 0)
            
            # Emit structured execution completed audit event
            sec_mgr.audit_logger.log_event(
                action="query_execution_completed",
                role=role,
                username=state.get("username"),
                details={"sql": sql, "row_count": len(redacted_results)}
            )
            
            return {"final_result": redacted_results, "error_message": None, "metrics": state["metrics"]}
        except Exception as e:
            record_execution(state, False, error=str(e))
            return {"final_result": None, "error_message": str(e), "metrics": state["metrics"]}

def node_semantic_validate(state: SQLAgentState):
    sql = state.get("sql_query", "")
    init_metrics_state(state)
    if state.get("error_message"):
        return {}
        
    with track_latency(state, "semantic_validation"):
        try:
            # Performs execution-aware semantic correctness validation
            validation_res = validate_sql_semantics(
                sql_query=sql,
                results=state.get("final_result"),
                refined_query=state.get("refined_query") or state["original_query"],
                schema=state.get("db_schema", "")
            )
            
            if not validation_res.is_valid:
                error_msg = f"Semantic Validation Error: {validation_res.reason}"
                if validation_res.suggested_fix:
                    error_msg += f" Suggested fix: {validation_res.suggested_fix}"
                record_validation(state, "semantic", False, validation_res.reason, validation_res.suggested_fix)
                return {"error_message": error_msg, "metrics": state["metrics"]}
                
            record_validation(state, "semantic", True, "Semantic correctness validated successfully.")
            return {"error_message": None, "metrics": state["metrics"]}
        except Exception as e:
            record_validation(state, "semantic", False, f"Semantic Validation Exception: {str(e)}")
            return {"error_message": f"Semantic Validation Exception: {str(e)}", "metrics": state["metrics"]}

def decide_after_syntax_validation(state: SQLAgentState) -> Literal["execute", "correct", "end"]:
    """Conditional Edge routing after checking SQL syntax and safety."""
    if not state.get("error_message"):
        return "execute"
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "end"
    return "correct"

def decide_after_execution(state: SQLAgentState) -> Literal["semantic_validate", "correct", "end"]:
    """Conditional Edge routing after executing SQL query."""
    if not state.get("error_message"):
        return "semantic_validate"
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "end"
    return "correct"

def decide_after_semantic_validation(state: SQLAgentState) -> Literal["correct", "end"]:
    """Conditional Edge routing after semantic verification."""
    if not state.get("error_message"):
        return "end"
    if state.get("retry_count", 0) >= MAX_RETRIES:
        return "end"
    return "correct"

def build_workflow():
    """Compiles and returns the LangGraph application."""
    workflow = StateGraph(SQLAgentState)

    # Add Nodes
    workflow.add_node("clarify", node_clarify_intent)
    workflow.add_node("retrieve_schema", node_retrieve_schema)
    workflow.add_node("plan", node_query_planning)
    workflow.add_node("generate", node_sql_generation)
    workflow.add_node("validate", node_validate_sql)
    workflow.add_node("correct", node_correct_sql)
    workflow.add_node("execute_db", node_execute_sql)
    workflow.add_node("semantic_validate", node_semantic_validate)

    # Add Edges (linear flow for generation)
    workflow.set_entry_point("clarify")
    workflow.add_edge("clarify", "retrieve_schema")
    workflow.add_edge("retrieve_schema", "plan")
    workflow.add_edge("plan", "generate")
    workflow.add_edge("generate", "validate")

    # Add Conditional Edges based on stage-wise validation success
    workflow.add_conditional_edges(
        "validate",
        decide_after_syntax_validation,
        {
            "execute": "execute_db",
            "correct": "correct",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "execute_db",
        decide_after_execution,
        {
            "semantic_validate": "semantic_validate",
            "correct": "correct",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "semantic_validate",
        decide_after_semantic_validation,
        {
            "correct": "correct",
            "end": END
        }
    )

    # Loop back from correct to validate to re-check the fixed SQL
    workflow.add_edge("correct", "validate")

    return workflow.compile()
