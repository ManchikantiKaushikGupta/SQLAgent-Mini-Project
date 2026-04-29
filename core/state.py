from typing import TypedDict, Optional, List, Any

class AgentState(TypedDict):
    """
    State object passed between nodes in the LangGraph pipeline.
    """
    # User's raw query
    query: str
    
    # Refined query from Intent Clarification
    refined_query: Optional[str]
    
    # Execution plan from Query Planning
    plan: Optional[str]
    
    # Generated SQL query from SQL Generation
    sql_query: Optional[str]
    
    # Results from Database Execution (Validation & Correction agent)
    results: Optional[List[Any]]
    
    # Any errors encountered during the process
    error: Optional[str]
    
    # Number of retries for SQL correction
    retry_count: int
