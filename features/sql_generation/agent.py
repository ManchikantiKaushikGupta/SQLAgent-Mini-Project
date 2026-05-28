"""
SQL Generation Agent

Converts a structured query execution plan into a raw SQL statement.
"""

import logging
from typing import Union
from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm
from schemas.planner import QueryPlan
from features.sql_generation.prompt import (
    SQL_GENERATION_SYSTEM_PROMPT,
    SQL_GENERATION_HUMAN_TEMPLATE,
)

logger = logging.getLogger(__name__)


def generate_sql(plan: Union[str, QueryPlan], schema: str) -> str:
    """
    Generates a SQL SELECT statement based on a query execution plan and
    database schema.

    Args:
        plan: The structured query execution plan (Pydantic QueryPlan model or string).
        schema: The database schema string.

    Returns:
        A raw SQL query string.

    Raises:
        ValueError: If plan or schema are empty.
    """
    if not plan:
        logger.error("generate_sql failed: plan is empty")
        raise ValueError("plan must be provided.")

    if not schema or not schema.strip():
        logger.error("generate_sql failed: schema is empty")
        raise ValueError("schema must be a non-empty string.")

    if isinstance(plan, str):
        if not plan.strip():
            logger.error("generate_sql failed: plan is an empty string")
            raise ValueError("plan must be a non-empty string.")
        formatted_plan = plan.strip()
    else:
        # Structured Pydantic model
        if hasattr(plan, "model_dump_json"):
            formatted_plan = plan.model_dump_json(indent=2)
        else:
            formatted_plan = plan.json(indent=2)

    logger.info("Generating SQL from structured query execution plan...")
    logger.debug(f"Formatted plan passed to generator:\n{formatted_plan}")

    llm = get_llm()

    human_content = SQL_GENERATION_HUMAN_TEMPLATE.format(
        schema=schema.strip(),
        plan=formatted_plan,
    )

    messages = [
        SystemMessage(content=SQL_GENERATION_SYSTEM_PROMPT),
        HumanMessage(content=human_content),
    ]

    try:
        response = llm.invoke(messages)
        from core.llm import extract_text
        sql_query = extract_text(response)


        # Clean up formatting the LLM might have added despite instructions
        if sql_query.startswith("```sql"):
            sql_query = sql_query.split("```sql", 1)[1]
        if sql_query.startswith("```"):
            sql_query = sql_query.split("```", 1)[1]
        if sql_query.endswith("```"):
            sql_query = sql_query.rsplit("```", 1)[0]

        sql_query = sql_query.strip()
        logger.info(f"Successfully generated SQL query: {sql_query}")
        return sql_query
    except Exception as e:
        logger.exception("Error invoking LLM for SQL generation")
        raise e

