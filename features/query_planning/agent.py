"""
Query Planning Agent

Converts a refined natural language query into a structured, step-by-step
execution plan that guides the SQL Generation Agent.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm
from features.query_planning.prompt import (
    QUERY_PLANNING_SYSTEM_PROMPT,
    QUERY_PLANNING_HUMAN_TEMPLATE,
)


def generate_query_plan(refined_query: str, schema: str) -> str:
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
        A numbered plain-text execution plan string ready to be passed
        to the SQL Generation Agent.

    Raises:
        ValueError: If refined_query or schema are empty.
    """
    if not refined_query or not refined_query.strip():
        raise ValueError("refined_query must be a non-empty string.")

    if not schema or not schema.strip():
        raise ValueError("schema must be a non-empty string.")

    llm = get_llm()

    human_content = QUERY_PLANNING_HUMAN_TEMPLATE.format(
        schema=schema.strip(),
        refined_query=refined_query.strip(),
    )

    messages = [
        SystemMessage(content=QUERY_PLANNING_SYSTEM_PROMPT),
        HumanMessage(content=human_content),
    ]

    response = llm.invoke(messages)
    plan = response.content.strip()

    return plan
