import json
import re
import logging
from typing import List, Optional, Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from core.llm import get_llm
from schemas.validation import SemanticValidationResult

logger = logging.getLogger(__name__)

SEMANTIC_VALIDATOR_SYSTEM_PROMPT = """
You are an expert SQL QA specialist. Your job is to check if a generated SQL query is semantically and logically correct and actually answers the user's refined natural language query.

You will be provided with:
1. The database schema.
2. The refined natural language query (user intent).
3. The generated SQL query.
4. The actual execution results of the SQL query (in JSON format).

You must populate all relevant fields in the provided schema:
- is_valid: True if the SQL query matches the schema, user intent, and the results are logically correct. False otherwise.
- reason: Clear explanation of why the query is correct, or if incorrect, details on the mismatch (e.g., wrong aggregation, incorrect column, missed filter, wrong join condition, or returning empty results when records exist).
- suggested_fix: If invalid, suggest a clear correction for the SQL generation agent.

Rules:
- If the execution results are empty (e.g. `[]`), check if the query was overly restrictive (e.g., using INNER JOIN instead of LEFT JOIN, or incorrect filter value). If so, mark as invalid.
- Ensure the columns selected align with what the user asked.
- Output ONLY a single JSON object matching the requested schema. No intro, no explanation, no markdown outside JSON.
"""

SEMANTIC_VALIDATOR_HUMAN_TEMPLATE = """
Database Schema:
{schema}

Refined User Intent:
{refined_query}

Generated SQL Query:
{sql_query}

Execution Results:
{results}
"""

def validate_sql_semantics(
    sql_query: str,
    results: Optional[List[Dict[str, Any]]],
    refined_query: str,
    schema: str
) -> SemanticValidationResult:
    """
    Validates the semantic and logical correctness of a SQL query by comparing it
    against the user intent, schema, and actual execution results.
    
    Args:
        sql_query: The generated SQL query string.
        results: The execution output list of row dicts.
        refined_query: The clarified user intent query.
        schema: The database schema.
        
    Returns:
        A SemanticValidationResult Pydantic model with validation results.
    """
    if not sql_query or not sql_query.strip():
        raise ValueError("sql_query must be a non-empty string.")
    if not refined_query or not refined_query.strip():
        raise ValueError("refined_query must be a non-empty string.")
    if not schema or not schema.strip():
        raise ValueError("schema must be a non-empty string.")

    logger.info(f"Semantically validating SQL query: {sql_query}")
    
    llm = get_llm()
    
    formatted_results = json.dumps(results, indent=2) if results is not None else "[]"
    
    human_content = SEMANTIC_VALIDATOR_HUMAN_TEMPLATE.format(
        schema=schema.strip(),
        refined_query=refined_query.strip(),
        sql_query=sql_query.strip(),
        results=formatted_results
    )
    
    messages = [
        SystemMessage(content=SEMANTIC_VALIDATOR_SYSTEM_PROMPT),
        HumanMessage(content=human_content)
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
        logger.debug(f"Raw LLM response for semantic validation:\n{content}")

        # Extract JSON block deterministically
        match = re.search(r"(\{.*\})", content, re.DOTALL)
        if not match:
            logger.error(f"Failed to find JSON block in LLM response: {content}")
            raise ValueError("The semantic validator did not output a valid JSON validation block.")

        json_str = match.group(1)
        data = json.loads(json_str)

        # Validate against the Pydantic SemanticValidationResult model
        if hasattr(SemanticValidationResult, "model_validate"):
            result = SemanticValidationResult.model_validate(data)
        else:
            result = SemanticValidationResult.parse_obj(data)

        logger.info(
            f"Semantic validation completed. Is Valid: {result.is_valid}. "
            f"Reason: {result.reason}"
        )
        return result
    except Exception as e:
        logger.exception("Error during semantic SQL validation")
        raise e
