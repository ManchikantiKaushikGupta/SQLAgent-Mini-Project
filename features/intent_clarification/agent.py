"""
Intent Clarification Agent

Detects and resolves ambiguous natural language queries before SQL generation.
Uses the database schema for context-aware clarification.
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm
from features.intent_clarification.prompt import (
    INTENT_CLARIFICATION_SYSTEM_PROMPT,
    INTENT_CLARIFICATION_HUMAN_TEMPLATE,
)


# ---------------------------------------------------------------------------
# Vague term detection
# ---------------------------------------------------------------------------

VAGUE_PATTERNS = [
    r"\btop\b",
    r"\bbest\b",
    r"\brecent",        # catches: recent, recently
    r"\blatest\b",
    r"\bnew(?:est)?\b", # catches: new, newest
    r"\ba lot\b",
    r"\bmany\b",
    r"\bmost\b",
    r"\bpopular\b",
    r"\bexpensive\b",
    r"\bcheap(?:est)?\b",  # catches: cheap, cheapest
    r"\bsome\b",
    r"\bfew\b",
    r"\bgood\b",
    r"\bbad\b",
    r"\bhigh(?:est)?\b",   # catches: high, highest
    r"\blow(?:est)?\b",    # catches: low, lowest
    r"\blargest?\b",       # catches: large, largest
    r"\bsmallest?\b",      # catches: small, smallest
]

_VAGUE_RE = re.compile("|".join(VAGUE_PATTERNS), re.IGNORECASE)


def is_ambiguous(query: str) -> bool:
    """
    Checks whether a user query contains vague or ambiguous terms
    that need clarification before SQL generation.

    Args:
        query: The raw user query string.

    Returns:
        True if the query contains ambiguous terms, False otherwise.
    """
    return bool(_VAGUE_RE.search(query))


def get_matched_vague_terms(query: str) -> list[str]:
    """
    Returns a list of vague/ambiguous terms found in the query.

    Args:
        query: The raw user query string.

    Returns:
        A list of matched vague term strings.
    """
    return [match.group() for match in _VAGUE_RE.finditer(query)]


# ---------------------------------------------------------------------------
# Core clarification logic
# ---------------------------------------------------------------------------

def clarify_intent(query: str, schema: str = "") -> str:
    """
    Clarifies an ambiguous natural language query using the LLM.

    If the query contains no vague terms, it is returned as-is without
    making an LLM call, saving latency and tokens.

    If the query is ambiguous, it is sent to the LLM along with the
    database schema for context-aware refinement.

    Args:
        query: The raw user query string.
        schema: The database schema string (table/column names and types).
                Used to help the LLM resolve entity and column references.

    Returns:
        A refined, unambiguous query string ready for SQL planning.
    """
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    # Fast path: skip LLM call if query is already precise
    if not is_ambiguous(query):
        return query.strip()

    llm = get_llm()

    human_content = INTENT_CLARIFICATION_HUMAN_TEMPLATE.format(
        schema=schema if schema else "Schema not provided.",
        query=query.strip(),
    )

    messages = [
        SystemMessage(content=INTENT_CLARIFICATION_SYSTEM_PROMPT),
        HumanMessage(content=human_content),
    ]

    response = llm.invoke(messages)
    from core.llm import extract_text
    refined_query = extract_text(response)

    return refined_query

