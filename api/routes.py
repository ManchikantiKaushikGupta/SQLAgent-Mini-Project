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
    user_role: Optional[str] = None
    username: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class QueryResponse(BaseModel):
    original_query: str
    refined_query: Optional[str]
    sql_query: Optional[str]
    results: Optional[List[Dict[str, Any]]]
    error: Optional[str]
    metrics: Optional[Dict[str, Any]] = None
    active_provider: Optional[str] = None
    active_model: Optional[str] = None


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

    # Initialize the Security Manager to log query_request
    from core.security import get_security_manager
    sec_mgr = get_security_manager()
    role = request.user_role or sec_mgr.config.default_role
    username = request.username or "anonymous"

    # Emit dynamic audit event for API entry
    sec_mgr.audit_logger.log_event(
        action="query_request",
        role=role,
        username=username,
        details={"query": request.query}
    )

    initial_state = {
        "original_query": request.query,
        "db_schema": schema,
        "refined_query": "",
        "query_plan": "",
        "sql_query": "",
        "error_message": None,
        "retry_count": 0,
        "final_result": None,
        "user_role": role,
        "username": username,
        "security_error": None
    }

    from core.llm import register_thread_callbacks, clear_thread_callbacks, provider_override, model_override
    from observability.metrics import TokenAccumulatorCallback
    from llm.factory import load_config
    
    tokens_tracker = TokenAccumulatorCallback()
    register_thread_callbacks([tokens_tracker])

    # Establish request-scoped LLM overrides if specified
    provider_token = provider_override.set(request.provider if request.provider else None)
    model_token = model_override.set(request.model if request.model else None)

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

        # Retrieve the dynamically resolved provider/model configured/used for this execution
        config = load_config()
        final_provider = config.get("provider", "gemini")
        final_model = config.get("model")
        if not final_model:
            prov_specific = config.get(final_provider, {})
            if isinstance(prov_specific, dict):
                final_model = prov_specific.get("model", "Unknown")
            else:
                final_model = "Unknown"

        return QueryResponse(
            original_query=result_state.get("original_query", ""),
            refined_query=result_state.get("refined_query"),
            sql_query=result_state.get("sql_query"),
            results=result_state.get("final_result"),
            error=result_state.get("error_message"),
            metrics=metrics,
            active_provider=final_provider,
            active_model=final_model
        )
    except Exception as e:
        logger.error(f"Error executing query graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        provider_override.reset(provider_token)
        model_override.reset(model_token)
        clear_thread_callbacks()


@router.get("/config")
def get_config():
    """
    Returns the current LLM configurations and dynamic schema settings.
    """
    from llm.factory import load_config
    try:
        config = load_config()
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{filename}")
def get_benchmark(filename: str):
    """
    Serves the selected benchmark JSON log file from the evaluation directory.
    """
    import os
    from fastapi.responses import FileResponse
    
    # Restrict filenames to prevent directory traversal
    allowed_files = [
        "run_history.json",
        "run_history_spider.json",
        "run_history_spider_realistic.json",
        "run_history_spider_syn.json",
        "failed_queries.json",
        "failed_queries_spider.json"
    ]
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="Invalid benchmark file name.")
        
    eval_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evaluation"))
    file_path = os.path.join(eval_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Benchmark history log file not found.")
        
    return FileResponse(file_path)

