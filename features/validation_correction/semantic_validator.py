import json
import re
import logging
from typing import List, Optional, Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from core.llm import get_llm
from schemas.validation import SemanticValidationResult

logger = logging.getLogger(__name__)

SEMANTIC_VALIDATOR_SYSTEM_PROMPT = """
You are an expert SQL QA specialist. Your job is to check if a generated SQL query is semantically and logically correct and actually answers the user's refined natural language query, guided by execution outcomes and rule-based diagnostic alerts.

You will be provided with:
1. The database schema.
2. The refined natural language query (user intent).
3. The generated SQL query.
4. The actual execution results of the SQL query (in JSON format).
5. Pre-computed rule-based intent alerts (if any).

You must populate all relevant fields in the provided schema:
- is_valid: True if the SQL query matches the schema, user intent, and the results are logically correct. False otherwise.
- reason: Clear explanation of why the query is correct, or if incorrect, details on the mismatch (e.g., wrong aggregation, incorrect column, missed filter, wrong join condition, or returning empty results when records exist). Include details from the rule-based alerts if they point to real errors.
- suggested_fix: If invalid, suggest a clear correction for the SQL generation agent.

Rules:
- If there are rule-based alerts, inspect them carefully. They indicate strong signs of logical mismatches (e.g., missing limits, aggregations, or filters). If a rule alert is correct, mark as invalid.
- If the execution results are empty (e.g. `[]`), check if the query was overly restrictive (e.g., using INNER JOIN instead of LEFT JOIN, or incorrect filter value). If so, mark as invalid.
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

Rule-Based Intent Alerts:
{alerts}
"""

def run_rule_based_semantic_checks(
    sql_query: str,
    refined_query: str,
    results: Optional[List[Dict[str, Any]]]
) -> List[str]:
    """
    Executes fast, deterministic semantic check rules to spot obvious logical mismatches
    between the user intent and the generated SQL before invoking the LLM.
    """
    alerts = []
    sql_lower = sql_query.lower()
    query_lower = refined_query.lower()
    
    # 1. Empty Results check
    if results is not None and len(results) == 0:
        # If the user is asking for records/counting, but we got exactly 0 rows back
        if not any(word in query_lower for word in ["how many", "count", "number of", "exist", "any"]):
            alerts.append("Execution returned 0 rows, which strongly indicates an overly restrictive filter or incorrect JOIN type.")

    # 2. Limit / Top K check
    if any(word in query_lower for word in ["top", "limit", "most", "highest", "first 5", "first 3", "first 10", "cheapest", "expensive", "costliest"]):
        if "limit" not in sql_lower:
            alerts.append("The intent requests a limit or ranked 'top' subset of records, but the SQL query lacks a LIMIT clause.")
        if "order by" not in sql_lower:
            alerts.append("The intent requests ranked or ordered subset of records, but the SQL query lacks an ORDER BY clause.")

    # 3. Filter Literal check
    # Check common filter values in E-commerce seed db and standard evaluations
    filter_vals = ["electronics", "apparel", "furniture", "sporting", "premium", "completed", "shipped", "delivered", "new york", "london", "san francisco", "tokyo", "sydney"]
    for filter_val in filter_vals:
        if filter_val in query_lower:
            # Check if this literal is present in the SQL (stripped of spaces and quotes for robustness)
            clean_val = filter_val.replace(" ", "")
            clean_sql = sql_lower.replace(" ", "").replace("'", "").replace('"', "")
            if clean_val not in clean_sql:
                alerts.append(f"The intent references filter criteria '{filter_val}', but this filter criteria/literal was not found in the SQL statement.")

    # 4. Aggregation check
    if any(word in query_lower for word in ["average", "avg", "mean"]):
        if "avg(" not in sql_lower:
            alerts.append("The intent requests an 'average' or 'mean' metric, but the SQL statement lacks an AVG() aggregate function.")
            
    if any(word in query_lower for word in ["total", "sum", "spent"]):
        if "sum(" not in sql_lower:
            alerts.append("The intent requests a 'total' or 'sum' metric, but the SQL statement lacks a SUM() aggregate function.")

    return alerts


def validate_sql_semantics(
    sql_query: str,
    results: Optional[List[Dict[str, Any]]],
    refined_query: str,
    schema: str
) -> SemanticValidationResult:
    """
    Validates the semantic and logical correctness of a SQL query by comparing it
    against the user intent, schema, and actual execution results using a hybrid
    approach of deterministic check rules and LLM deep-reasoning.
    
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
    
    # Step 1: Run fast deterministic rule-based checks first
    alerts = run_rule_based_semantic_checks(sql_query, refined_query, results)
    
    if alerts:
        logger.warning(f"Deterministic semantic check rules triggered {len(alerts)} alerts: {alerts}")
    
    # Step 2: Formulate the hybrid prompt including rule alerts
    llm = get_llm()
    
    formatted_results = json.dumps(results, indent=2) if results is not None else "[]"
    formatted_alerts = "\n".join([f"- [ALERT] {a}" for a in alerts]) if alerts else "- No rule violations detected."
    
    human_content = SEMANTIC_VALIDATOR_HUMAN_TEMPLATE.format(
        schema=schema.strip(),
        refined_query=refined_query.strip(),
        sql_query=sql_query.strip(),
        results=formatted_results,
        alerts=formatted_alerts
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
