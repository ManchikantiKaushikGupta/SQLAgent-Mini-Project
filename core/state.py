"""
LangGraph State Definition

Represents the memory passed between nodes during execution.
"""

from typing import TypedDict, Any, Optional

class SQLAgentState(TypedDict):
    original_query: str        # The raw user natural language query
    db_schema: str             # Database schema string to provide context
    refined_query: str         # The output from the Intent Clarification Agent
    query_plan: str            # The step-by-step query plan string
    sql_query: str             # The current SQL query (generated or corrected)
    error_message: Optional[str] # Any error encountered during SQL compilation/validation
    retry_count: int           # The number of times the agent tried to correct a query
    final_result: Optional[Any]  # Target for the database execution results
