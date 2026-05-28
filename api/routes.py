"""
FastAPI Routes

Defines endpoints for the SQLAgent application.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Optional, Dict, List
import logging

from core.graph import build_workflow
from db.database import get_database_schema

router = APIRouter()
logger = logging.getLogger(__name__)

# Reusable compiled graph
try:
    workflow_app = build_workflow()
except Exception as e:
    logger.warning(f"Could not build workflow graph immediately: {e}")
    workflow_app = None


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    original_query: str
    refined_query: Optional[str]
    sql_query: Optional[str]
    results: Optional[List[Dict[str, Any]]]
    error: Optional[str]
    metrics: Optional[Dict[str, Any]] = None


@router.post("/ask", response_model=QueryResponse)
async def ask_database(request: QueryRequest):
    """
    Takes a natural language query, runs it through the SQLAgent graph,
    and returns the SQL execution results.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if workflow_app is None:
        raise HTTPException(status_code=500, detail="Workflow graph not initialized.")

    schema = get_database_schema()

    initial_state = {
        "original_query": request.query,
        "db_schema": schema,
        "refined_query": "",
        "query_plan": "",
        "sql_query": "",
        "error_message": None,
        "retry_count": 0,
        "final_result": None
    }

    from core.llm import register_thread_callbacks, clear_thread_callbacks
    from observability.metrics import TokenAccumulatorCallback
    
    tokens_tracker = TokenAccumulatorCallback()
    register_thread_callbacks([tokens_tracker])

    try:
        # Run the graph until the end
        result_state = workflow_app.invoke(initial_state)

        # Inject final token usage stats into the metrics telemetry
        metrics = result_state.get("metrics", {})
        if metrics:
            metrics["tokens"] = {
                "prompt_tokens": tokens_tracker.prompt_tokens,
                "completion_tokens": tokens_tracker.completion_tokens,
                "total_tokens": tokens_tracker.total_tokens
            }
            
            # Inject serialized Query Plan into metrics context
            plan = result_state.get("query_plan")
            if plan:
                if hasattr(plan, "model_dump"):
                    metrics["query_plan"] = plan.model_dump()
                elif hasattr(plan, "dict"):
                    metrics["query_plan"] = plan.dict()
                else:
                    metrics["query_plan"] = plan


        return QueryResponse(
            original_query=result_state.get("original_query", ""),
            refined_query=result_state.get("refined_query"),
            sql_query=result_state.get("sql_query"),
            results=result_state.get("final_result"),
            error=result_state.get("error_message"),
            metrics=metrics
        )
    except Exception as e:
        logger.error(f"Error executing query graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        clear_thread_callbacks()

