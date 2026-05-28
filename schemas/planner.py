from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any

class TableRequirement(BaseModel):
    table_name: str = Field(..., description="The exact name of the table required from the schema")
    purpose: str = Field(..., description="The role or purpose of this table in the query")

    @model_validator(mode="before")
    @classmethod
    def normalize_table(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"table_name": data, "purpose": "Required for query execution"}
        if isinstance(data, dict):
            if "name" in data and "table_name" not in data:
                data["table_name"] = data["name"]
        return data

class JoinRequirement(BaseModel):
    left_table: str = Field(..., description="The left table name in the join")
    right_table: str = Field(..., description="The right table name in the join")
    join_type: str = Field("INNER", description="Type of join (INNER, LEFT, RIGHT, FULL)")
    on_condition: str = Field(..., description="The column condition to join on (e.g. users.id = orders.user_id)")

    @model_validator(mode="before")
    @classmethod
    def normalize_join(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "condition" in data and "on_condition" not in data:
                data["on_condition"] = data["condition"]
        return data

class FilterRequirement(BaseModel):
    column: str = Field(..., description="The fully qualified column name to filter on (e.g. users.status)")
    operator: str = Field(..., description="The operator to use (e.g. '=', '!=', '>', '<', 'LIKE', 'IN', 'IS NULL')")
    value: str = Field(..., description="The value or value description to compare against (e.g. 'active', 5)")

class AggregationRequirement(BaseModel):
    expression: str = Field(..., description="The aggregation expression (e.g. SUM(orders.amount), COUNT(users.id))")
    alias: str = Field(..., description="Alias to use for the aggregation (e.g. total_amount, user_count)")
    purpose: str = Field(..., description="Why this aggregation is performed")

class OrderByRequirement(BaseModel):
    expression: str = Field(..., description="The column or expression to sort by (e.g. total_amount, users.id)")
    direction: str = Field("ASC", description="Sorting direction (ASC or DESC)")

    @model_validator(mode="before")
    @classmethod
    def normalize_order_by(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "column" in data and "expression" not in data:
                data["expression"] = data["column"]
            if "dir" in data and "direction" not in data:
                data["direction"] = data["dir"]
        return data

class QueryPlan(BaseModel):
    """
    A structured, step-by-step query execution plan that guides the SQL Generation Agent.
    """
    thought_process: str = Field(..., description="Chain-of-thought explanation of how to construct the query plan")
    tables: List[TableRequirement] = Field(default_factory=list, description="List of tables needed for the query")
    joins: List[JoinRequirement] = Field(default_factory=list, description="List of join requirements")
    filters: List[FilterRequirement] = Field(default_factory=list, description="List of filters or WHERE conditions")
    aggregations: List[AggregationRequirement] = Field(default_factory=list, description="List of aggregations required")
    group_by: List[str] = Field(default_factory=list, description="List of columns or expressions to group by")
    order_by: List[OrderByRequirement] = Field(default_factory=list, description="List of ordering/sorting requirements")
    limit: Optional[int] = Field(None, description="The maximum number of results to return (LIMIT clause)")

    @model_validator(mode="before")
    @classmethod
    def normalize_plan(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If tables is a list of strings, convert to TableRequirement structures
            if "tables" in data and isinstance(data["tables"], list):
                normalized_tables = []
                for t in data["tables"]:
                    if isinstance(t, str):
                        normalized_tables.append({"table_name": t, "purpose": "Required for query execution"})
                    elif isinstance(t, dict):
                        if "name" in t and "table_name" not in t:
                            t["table_name"] = t["name"]
                        normalized_tables.append(t)
                    else:
                        normalized_tables.append(t)
                data["tables"] = normalized_tables
                
            # If group_by contains dict objects, extract their column name
            if "group_by" in data and isinstance(data["group_by"], list):
                normalized_gb = []
                for gb in data["group_by"]:
                    if isinstance(gb, str):
                        normalized_gb.append(gb)
                    elif isinstance(gb, dict):
                        if "column" in gb:
                            normalized_gb.append(gb["column"])
                        elif "expression" in gb:
                            normalized_gb.append(gb["expression"])
                        else:
                            normalized_gb.append(str(list(gb.values())[0]))
                    else:
                        normalized_gb.append(str(gb))
                data["group_by"] = normalized_gb
        return data
