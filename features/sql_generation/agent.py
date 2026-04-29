"""
SQL Generation Agent

Converts a structured query execution plan into a raw SQL statement.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm
from features.sql_generation.prompt import (
    SQL_GENERATION_SYSTEM_PROMPT,
    SQL_GENERATION_HUMAN_TEMPLATE,
)


def generate_sql(plan: str, schema: str) -> str:
    """
    Generates a SQL SELECT statement based on a query execution plan and
    database schema.

    Args:
        plan: The structured query execution plan (output of Query Planning).
        schema: The database schema string.

    Returns:
        A raw SQL query string.

    Raises:
        ValueError: If plan or schema are empty strings.
    """
    if not plan or not plan.strip():
        raise ValueError("plan must be a non-empty string.")

    if not schema or not schema.strip():
        raise ValueError("schema must be a non-empty string.")

    llm = get_llm()

    human_content = SQL_GENERATION_HUMAN_TEMPLATE.format(
        schema=schema.strip(),
        plan=plan.strip(),
    )

    messages = [
        SystemMessage(content=SQL_GENERATION_SYSTEM_PROMPT),
        HumanMessage(content=human_content),
    ]

    response = llm.invoke(messages)
    
    # Clean up formatting the LLM might have added despite instructions
    sql_query = response.content.strip()
    if sql_query.startswith("```sql"):
        sql_query = sql_query.split("```sql", 1)[1]
    if sql_query.startswith("```"):
        sql_query = sql_query.split("```", 1)[1]
    if sql_query.endswith("```"):
        sql_query = sql_query.rsplit("```", 1)[0]
    
    return sql_query.strip()

