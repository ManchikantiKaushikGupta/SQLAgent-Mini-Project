from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm
from features.intent_clarification.prompt import INTENT_CLARIFICATION_SYSTEM_PROMPT


def clarify_intent(query: str) -> str:
    """
    Clarifies an ambiguous natural language query using Gemini.

    Takes the raw user input, sends it to the LLM with the intent clarification
    system prompt, and returns a refined query suitable for SQL planning.

    Args:
        query: The raw user query string.

    Returns:
        A refined, unambiguous query string.
    """
    llm = get_llm()

    messages = [
        SystemMessage(content=INTENT_CLARIFICATION_SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]

    response = llm.invoke(messages)
    refined_query = response.content.strip()

    return refined_query
