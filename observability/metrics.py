"""
Observability Metrics Tracking Framework

Implements reusable context managers, validators, and callback handlers
to measure SQLAgent execution duration, token usage, validations, and repair trails.
"""

import time
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger("SQLAgent.Metrics")

class TokenAccumulatorCallback(BaseCallbackHandler):
    """
    LangChain callback handler that intercepts LLM execution endpoints 
    and thread-safely aggregates prompt, completion, and total tokens.
    """
    def __init__(self):
        super().__init__()
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Called at the end of LLM generation to extract and add tokens."""
        try:
            for generation in response.generations:
                for gen in generation:
                    # Look for message attribute on generation
                    message = getattr(gen, "message", None)
                    if message:
                        # 1. Try standard LangChain usage_metadata
                        usage = getattr(message, "usage_metadata", None)
                        if usage:
                            self.prompt_tokens += usage.get("input_tokens", 0)
                            self.completion_tokens += usage.get("output_tokens", 0)
                            self.total_tokens += usage.get("total_tokens", 0)
                            continue
                            
                        # 2. Try response_metadata fallback
                        resp_meta = getattr(message, "response_metadata", {})
                        token_usage = resp_meta.get("token_usage", {})
                        if token_usage:
                            self.prompt_tokens += token_usage.get("prompt_tokens", 0) or token_usage.get("input_tokens", 0) or 0
                            self.completion_tokens += token_usage.get("completion_tokens", 0) or token_usage.get("output_tokens", 0) or 0
                            self.total_tokens += token_usage.get("total_tokens", 0) or 0
        except Exception as e:
            logger.warning(f"Error accumulating tokens: {e}")


def init_metrics_state(state: Dict[str, Any]) -> None:
    """
    Initializes the observability state container inside the LangGraph state.
    
    Args:
        state: The current LangGraph state dictionary.
    """
    if "metrics" not in state or state["metrics"] is None:
        state["metrics"] = {
            "latency": {},
            "tokens": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "validation": {"syntax": None, "semantic": None},
            "correction_history": [],
            "execution": {"success": None, "row_count": 0, "error": None}
        }


@contextmanager
def track_latency(state: Dict[str, Any], stage_name: str):
    """
    Context manager to dynamically measure the execution time of a graph node.
    
    Args:
        state: The current LangGraph state dictionary.
        stage_name: Name of the pipeline stage being measured.
    """
    init_metrics_state(state)
    start_time = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start_time
        state["metrics"]["latency"][stage_name] = elapsed


def record_validation(
    state: Dict[str, Any], 
    validator_type: str, 
    is_valid: bool, 
    reason: str, 
    suggested_fix: Optional[str] = None
) -> None:
    """
    Records the outcome of a validation check (syntax or semantic).
    
    Args:
        state: The current LangGraph state.
        validator_type: 'syntax' or 'semantic'.
        is_valid: Outcome of validation.
        reason: Explanatory text.
        suggested_fix: Suggested AST query patch if invalid.
    """
    init_metrics_state(state)
    state["metrics"]["validation"][validator_type] = {
        "is_valid": is_valid,
        "reason": reason,
        "suggested_fix": suggested_fix
    }


def record_correction(
    state: Dict[str, Any],
    attempt_number: int,
    failed_sql: str,
    error_message: str,
    corrected_sql: str,
    thought_process: str = ""
) -> None:
    """
    Appends a detailed log of a query repair/correction attempt to the loop history.
    
    Args:
        state: The current LangGraph state.
        attempt_number: Correction attempt index (1-based).
        failed_sql: The broken SQL statement.
        error_message: Compiler/DB validation exception text.
        corrected_sql: The repaired SQL statement.
        thought_process: The repair reasoning explaining the repair action.
    """
    init_metrics_state(state)
    state["metrics"]["correction_history"].append({
        "attempt": attempt_number,
        "failed_sql": failed_sql,
        "error_message": error_message,
        "corrected_sql": corrected_sql,
        "thought_process": thought_process,
        "timestamp": time.strftime("%H:%M:%S")
    })



def record_execution(
    state: Dict[str, Any],
    success: bool,
    row_count: int = 0,
    error: Optional[str] = None
) -> None:
    """
    Records PostgreSQL execution parameters.
    
    Args:
        state: The current LangGraph state.
        success: Whether statement ran without exception.
        row_count: Total returned database records.
        error: DB driver error message if failed.
    """
    init_metrics_state(state)
    state["metrics"]["execution"] = {
        "success": success,
        "row_count": row_count,
        "error": error
    }
