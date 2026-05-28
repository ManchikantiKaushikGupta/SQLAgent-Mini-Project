"""
Query Planning Agent

Converts a refined natural language query into a structured, step-by-step
execution plan that guides the SQL Generation Agent.
"""

import json
import re
import logging
from typing import Union
from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm
from schemas.planner import QueryPlan
from features.query_planning.prompt import (
    QUERY_PLANNING_SYSTEM_PROMPT,
    QUERY_PLANNING_HUMAN_TEMPLATE,
)

logger = logging.getLogger(__name__)


def generate_query_plan(refined_query: str, schema: str) -> QueryPlan:
    """
    Generates a structured, step-by-step SQL query plan from a refined
    natural language query and the database schema.

    Uses Chain-of-Thought reasoning to identify:
    - Which tables are needed
    - What joins are required
    - Filters, aggregations, groupings, and sort orders

    Args:
        refined_query: The clarified, unambiguous user query string
                       (output of the Intent Clarification Agent).
        schema: The database schema string (table/column names and types).

    Returns:
        A structured QueryPlan Pydantic model containing the thought process,
        tables, joins, filters, aggregations, groupings, orderings, and limit.

    Raises:
        ValueError: If refined_query or schema are empty.
    """
    if not refined_query or not refined_query.strip():
        logger.error("generate_query_plan failed: refined_query is empty")
        raise ValueError("refined_query must be a non-empty string.")

    if not schema or not schema.strip():
        logger.error("generate_query_plan failed: schema is empty")
        raise ValueError("schema must be a non-empty string.")

    logger.info(f"Generating query plan for query: {refined_query.strip()}")

    llm = get_llm()

    human_content = QUERY_PLANNING_HUMAN_TEMPLATE.format(
        schema=schema.strip(),
        refined_query=refined_query.strip(),
    )

    messages = [
        SystemMessage(content=QUERY_PLANNING_SYSTEM_PROMPT),
        HumanMessage(content=human_content),
    ]

    try:
        response = llm.invoke(messages)
        raw_content = response.content
        
        # Handle cases where content is returned as a list of parts/dicts
        if isinstance(raw_content, list):
            text_parts = []
            for part in raw_content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif hasattr(part, "text"):
                    text_parts.append(part.text)
                else:
                    text_parts.append(str(part))
            content = "".join(text_parts)
        else:
            content = str(raw_content)

        content = content.strip()
        logger.debug(f"Raw LLM response for query planning:\n{content}")

        # Deterministically extract JSON block from the response
        match = re.search(r"(\{.*\})", content, re.DOTALL)
        if not match:
            logger.error(f"Failed to find JSON block in LLM response: {content}")
            raise ValueError("The query planner did not output a valid JSON plan block.")

        json_str = match.group(1)
        data = json.loads(json_str)

        # Validate against the Pydantic QueryPlan model
        if hasattr(QueryPlan, "model_validate"):
            plan = QueryPlan.model_validate(data)
        else:
            plan = QueryPlan.parse_obj(data)

        logger.info(
            f"Successfully generated structured query plan. "
            f"Tables needed: {[t.table_name for t in plan.tables]}, "
            f"Filters count: {len(plan.filters)}, "
            f"Joins count: {len(plan.joins)}"
        )
        return plan
    except Exception as e:
        logger.exception("Error during query planning or JSON validation")
        raise e
