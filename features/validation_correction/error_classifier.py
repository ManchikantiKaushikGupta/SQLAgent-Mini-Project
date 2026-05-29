"""
SQL Error Taxonomy Classifier Module

Uses LLM-based structured diagnostics to categorize SQL execution or validation failures
into a formal error taxonomy, returning a validated SQLErrorClassification Pydantic model.
"""

import json
import re
import logging
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage

from core.llm import get_llm, extract_text
from schemas.error_taxonomy import SQLErrorClassification

logger = logging.getLogger(__name__)

ERROR_CLASSIFICATION_SYSTEM_PROMPT = """
You are an expert SQL diagnostics engine.
Your job is to analyze a failed SQL query, the database schema, the user's natural language intent, and the database/parser error message, and classify the failure into a formal SQL error taxonomy.

The 9 formal taxonomy categories are:
1. SchemaError: Issues with missing tables, missing columns, or invalid table/column aliases.
2. JoinError: Missing joins or incorrect join conditions.
3. AggregationError: Missing GROUP BY clauses, incorrect aggregate functions, or invalid grouping.
4. FilterError: Incorrect predicates in WHERE/HAVING, wrong comparison operators, or logical operator errors.
5. OrderingError: Incorrect ORDER BY columns or invalid sorting directions.
6. LimitError: Incorrect LIMIT values (e.g. negative values, wrong count).
7. SubqueryError: Correlated subquery issues, nested query syntax, or incorrect subquery usage.
8. SetOperationError: Invalid UNION, INTERSECT, or EXCEPT operations.
9. SemanticError: Mismatch with user intent or incorrect business logic.

You must output a single JSON object matching this schema:
- category: One of the 9 categories listed above.
- subcategory: A brief (2-5 words) subcategory detailing the error (e.g., "Missing GROUP BY column", "Unknown column in WHERE").
- description: A detailed description of what is wrong with the query and why.
- failing_clause: The specific clause where the error resides: one of "select", "from", "joins", "where", "group", "having", "order", "limit", "set_op", "unknown".
- suggested_fix: A concrete description of how to fix this error.

Output ONLY the raw JSON object, with no markdown formatting or extra text outside of the JSON block.
"""

ERROR_CLASSIFICATION_HUMAN_TEMPLATE = """
Database Schema:
{schema}

Original Intent:
{original_query}

Failed SQL Query:
{failed_sql}

Error Message:
{error_message}
"""

def fallback_classify_error(
    failed_sql: str,
    error_message: str,
    original_query: str
) -> SQLErrorClassification:
    """
    Rule-based heuristic fallback classifier to ensure resilience if the LLM
    or JSON parsing encounters an issue.
    """
    logger.info("Executing rule-based heuristic fallback classification...")
    msg = error_message.lower()
    
    category = "SemanticError"
    subcategory = "General execution failure"
    description = f"Query failed execution with error: {error_message}"
    failing_clause = "unknown"
    suggested_fix = "Verify the syntax and ensure table/column references match the schema."

    # 1. AggregationError
    if "group by" in msg or "non-aggregated column" in msg or "aggregated" in msg or "grouping" in msg:
        category = "AggregationError"
        subcategory = "Invalid grouping or aggregation"
        description = "Columns are referenced in SELECT without being included in GROUP BY or covered by an aggregate function."
        failing_clause = "group"
        suggested_fix = "Add the missing columns to the GROUP BY clause or wrap them in an aggregate function like SUM, MAX, or MIN."
    
    # 2. JoinError
    elif "join" in msg or "on clause" in msg or "ambiguous column" in msg:
        category = "JoinError"
        subcategory = "Mismatched or missing join condition"
        description = "A table join is missing a required ON condition or uses ambiguous column references."
        failing_clause = "joins"
        suggested_fix = "Verify table aliases and ensure the JOIN ON clause accurately connects primary and foreign key columns."
        
    # 3. FilterError
    elif "where" in msg or "filter" in msg or "operator" in msg or "no such column" in msg or "column reference" in msg or "invalid input syntax" in msg or "type decimal" in msg:
        category = "FilterError"
        subcategory = "Invalid filter condition"
        description = "The WHERE filter contains an invalid column name, type mismatch, or incorrect comparison operator."
        failing_clause = "where"
        suggested_fix = "Correct column references in the WHERE filter and wrap string/date literal values in single quotes."

    # 4. LimitError
    elif "limit" in msg or "row count" in msg or "offset" in msg:
        category = "LimitError"
        subcategory = "Invalid LIMIT syntax"
        description = "The LIMIT value is negative, non-numeric, or incorrectly formatted."
        failing_clause = "limit"
        suggested_fix = "Correct the LIMIT clause to use a positive integer value."

    # 5. OrderingError
    elif "order by" in msg or "sort" in msg or "ordering" in msg:
        category = "OrderingError"
        subcategory = "Invalid ORDER BY expression"
        description = "The ORDER BY clause references a column that is not part of the dataset or has invalid sorting direction."
        failing_clause = "order"
        suggested_fix = "Ensure the ORDER BY column references a valid table column and uses ASC or DESC sorting keywords."

    # 6. SchemaError (general column/table missing)
    elif "table" in msg or "relation" in msg or "column" in msg:
        category = "SchemaError"
        subcategory = "Invalid schema reference"
        description = "A referenced table or column does not exist in the database schema."
        failing_clause = "unknown"
        suggested_fix = "Check the database schema to ensure all referenced tables and columns exist and are spelled correctly."

    return SQLErrorClassification(
        category=category,
        subcategory=subcategory,
        description=description,
        failing_clause=failing_clause,
        suggested_fix=suggested_fix
    )


def classify_sql_error(
    failed_sql: str,
    error_message: str,
    schema: str,
    original_query: str
) -> SQLErrorClassification:
    """
    Diagnoses and categorizes a SQL execution or parsing error under the formal
    error taxonomy using LLM structured outputs.
    
    Args:
        failed_sql: The query that failed validation or execution.
        error_message: The error generated by the database/parser.
        schema: The database schema.
        original_query: The refined or original natural language intent.
        
    Returns:
        A validated SQLErrorClassification Pydantic model.
    """
    if not failed_sql or not error_message or not schema:
        logger.warning("Empty arguments passed to classify_sql_error. Falling back to heuristic classification.")
        return fallback_classify_error(failed_sql, error_message, original_query)

    try:
        llm = get_llm()
        
        system_content = ERROR_CLASSIFICATION_SYSTEM_PROMPT
        human_content = ERROR_CLASSIFICATION_HUMAN_TEMPLATE.format(
            schema=schema.strip(),
            original_query=original_query.strip(),
            failed_sql=failed_sql.strip(),
            error_message=error_message.strip()
        )
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=human_content)
        ]
        
        logger.info("Calling LLM to classify SQL error into formal taxonomy...")
        response = llm.invoke(messages)
        content = extract_text(response).strip()
        
        # Parse JSON block
        match = re.search(r"(\{.*\})", content, re.DOTALL)
        if not match:
            logger.warning(f"Could not find JSON block in LLM error classification response: {content}")
            return fallback_classify_error(failed_sql, error_message, original_query)
            
        json_str = match.group(1)
        data = json.loads(json_str)
        
        if hasattr(SQLErrorClassification, "model_validate"):
            classification = SQLErrorClassification.model_validate(data)
        else:
            classification = SQLErrorClassification.parse_obj(data)
            
        logger.info(
            f"SQL error successfully classified: Category={classification.category}, "
            f"Subcategory='{classification.subcategory}', Clause={classification.failing_clause}"
        )
        return classification

    except Exception as e:
        logger.exception(f"Exception during LLM error classification: {e}")
        return fallback_classify_error(failed_sql, error_message, original_query)
