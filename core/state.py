"""
LangGraph State Definition

Represents the memory passed between nodes during execution.
"""

from typing import TypedDict, Any, Optional, Union
from schemas.planner import QueryPlan

class SQLAgentState(TypedDict):
    original_query: str        # The raw user natural language query
    db_schema: str             # Database schema string to provide context
    refined_query: str         # The output from the Intent Clarification Agent
    query_plan: Union[str, QueryPlan]  # The structured query execution plan (Pydantic model or initial empty string)
    sql_query: str             # The current SQL query (generated or corrected)
    error_message: Optional[str] # Any error encountered during SQL compilation/validation
    retry_count: int           # The number of times the agent tried to correct a query
    final_result: Optional[Any]  # Target for the database execution results
