"""
SQL Error Taxonomy Pydantic Schemas

Defines the formal representation of SQL syntax, execution, and semantic errors
to guide structured database and query repairs.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

class SQLErrorClassification(BaseModel):
    """
    Structured classification of a SQL error within the formal error taxonomy.
    """
    category: Literal[
        "SchemaError",
        "JoinError",
        "AggregationError",
        "FilterError",
        "OrderingError",
        "LimitError",
        "SubqueryError",
        "SetOperationError",
        "SemanticError"
    ] = Field(
        ...,
        description="The formal category of the SQL validation or execution error."
    )
    subcategory: str = Field(
        ...,
        description="A brief (2-5 words) subcategory detailing the specific error condition."
    )
    description: str = Field(
        ...,
        description="A clear, detailed description explaining exactly why the SQL failed."
    )
    failing_clause: Optional[Literal[
        "select", "from", "joins", "where", "group", "having", "order", "limit", "set_op", "unknown"
    ]] = Field(
        None,
        description="The specific SQL clause containing the error. Mapping 'joins', 'group', 'where', 'limit', or 'order' enables surgical AST patching."
    )
    suggested_fix: str = Field(
        ...,
        description="A concrete, prescriptive instruction on how the error should be corrected."
    )
