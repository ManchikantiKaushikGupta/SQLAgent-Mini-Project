import json
import re
import logging
import sqlglot
from sqlglot import exp
from typing import Optional, Tuple, Any
from langchain_core.messages import SystemMessage, HumanMessage
from core.llm import get_llm
from schemas.error_taxonomy import SQLErrorClassification

logger = logging.getLogger(__name__)

# Legacy System instructions to enforce single clause output (for backward compatibility)
CLAUSE_REPAIR_SYSTEM_PROMPT = """
You are an expert SQL clause repair assistant. 
Your job is to repair a SPECIFIC clause of a SQL query that failed a validation or execution check.

You will be provided with:
1. The database schema.
2. The original natural language query (user intent).
3. The failed SQL query.
4. The exact error message.
5. The specific clause type to repair.

Rules:
- Generate ONLY the corrected {clause_type_upper} clause.
- Output ONLY the single raw clause string. For example, if repairing WHERE, output a string like:
  WHERE users.status = 'active'
- Do NOT generate a full SELECT query.
- Do NOT include any explanations, markdown code blocks, or introductory text.
- Refer strictly to table and column names in the schema.
"""

CLAUSE_REPAIR_HUMAN_TEMPLATE = """
Database Schema:
{schema}

User Intent:
{original_query}

Failed SQL Query:
{failed_sql}

Error Message:
{error_message}

Failing Clause to Correct: {clause_type_upper}
"""

# New Taxonomy-Aware System Prompts
TAXONOMY_AWARE_CLAUSE_REPAIR_SYSTEM_PROMPT = """
You are an expert SQL clause repair assistant. 
Your job is to repair a SPECIFIC clause of a SQL query that failed a validation or execution check, guided by a formal error taxonomy classification.

You will be provided with:
1. The database schema.
2. The original natural language query (user intent).
3. The failed SQL query.
4. The exact error message.
5. The formal error classification (category, subcategory, description, and suggested fix).
6. The specific clause type to repair.

Rules:
- Generate ONLY the corrected {clause_type_upper} clause.
- Output ONLY the single raw clause string. For example, if repairing WHERE, output a string like:
  WHERE users.status = 'active'
- Do NOT generate a full SELECT query.
- Do NOT include any explanations, markdown code blocks, or introductory text.
- Refer strictly to table and column names in the schema.
"""

TAXONOMY_AWARE_CLAUSE_REPAIR_HUMAN_TEMPLATE = """
Database Schema:
{schema}

User Intent:
{original_query}

Failed SQL Query:
{failed_sql}

Error Message:
{error_message}

Formal Error Classification:
- Category: {error_category}
- Subcategory: {error_subcategory}
- Diagnostics: {error_description}
- Recommended Fix: {suggested_fix}

Failing Clause to Correct: {clause_type_upper}
"""


def detect_failing_clause(error_message: str) -> Optional[str]:
    """
    Parses the error message string to detect which clause is failing.
    Returns: "group", "joins", "where", "limit", "order", or None if general/unknown.
    """
    msg = error_message.lower()
    
    # 1. GROUP BY detection
    if "group by" in msg or "non-aggregated column" in msg or "aggregated" in msg or "grouping" in msg:
        return "group"
        
    # 2. JOIN detection
    if "join" in msg or "on clause" in msg or "ambiguous column" in msg or "unknown table" in msg:
        # Note: ambiguous column or unknown table can also be WHERE/SELECT, but often joins cause it
        return "joins"
        
    # 3. WHERE / Filter detection
    if "where" in msg or "filter" in msg or "operator" in msg or "column reference" in msg or "no such column" in msg:
        return "where"
        
    # 4. LIMIT detection
    if "limit" in msg or "row count" in msg or "offset" in msg:
        return "limit"
        
    # 5. ORDER BY detection
    if "order by" in msg or "sort" in msg or "ordering" in msg:
        return "order"
        
    return None


def repair_sql_clause(
    failed_sql: str,
    error_message: str,
    schema: str,
    original_query: str,
    classification: Optional[SQLErrorClassification] = None
) -> Optional[str]:
    """
    Surgically repairs a specific failing clause in a SQL query using SQLGlot AST manipulation.
    
    Args:
        failed_sql: The syntax-valid but logically/database failing SQL.
        error_message: The error generated.
        schema: The database schema.
        original_query: The user intent.
        classification: The optional Pydantic SQLErrorClassification model to guide the repair.
        
    Returns:
        The corrected SQL query string, or None if AST repair is not applicable or fails.
    """
    try:
        # Step 1: Parse the original query into AST
        parsed = sqlglot.parse_one(failed_sql)
    except Exception as e:
        logger.warning(f"Failed to parse failed SQL into AST for clause repair: {e}. Falling back to full regeneration.")
        return None

    # Step 2: Determine which clause is failing (from classification or fallback)
    clause_type = None
    if classification is not None and classification.failing_clause is not None:
        # Map taxonomy failing clauses to supported AST grafting types
        tax_clause = classification.failing_clause
        if tax_clause in ("group", "joins", "where", "limit", "order"):
            clause_type = tax_clause
        else:
            logger.info(f"Taxonomy clause '{tax_clause}' is not supported by surgical AST grafting. Falling back to full correction.")
            return None
    else:
        clause_type = detect_failing_clause(error_message)

    if not clause_type:
        logger.info("Could not determine specific failing SQL clause type. Falling back to full query correction.")
        return None
        
    clause_type_upper = clause_type.upper() if clause_type != "joins" else "JOIN"
    logger.info(f"Failing clause target: '{clause_type_upper}'. Commencing surgical clause patch...")

    # Step 3: Call the LLM to get ONLY the repaired clause
    llm = get_llm()
    
    # Use taxonomy-aware prompt if classification is provided
    if classification is not None:
        system_content = TAXONOMY_AWARE_CLAUSE_REPAIR_SYSTEM_PROMPT.format(clause_type_upper=clause_type_upper)
        human_content = TAXONOMY_AWARE_CLAUSE_REPAIR_HUMAN_TEMPLATE.format(
            schema=schema.strip(),
            original_query=original_query.strip(),
            failed_sql=failed_sql.strip(),
            error_message=error_message.strip(),
            error_category=classification.category,
            error_subcategory=classification.subcategory,
            error_description=classification.description,
            suggested_fix=classification.suggested_fix,
            clause_type_upper=clause_type_upper
        )
    else:
        system_content = CLAUSE_REPAIR_SYSTEM_PROMPT.format(clause_type_upper=clause_type_upper)
        human_content = CLAUSE_REPAIR_HUMAN_TEMPLATE.format(
            schema=schema.strip(),
            original_query=original_query.strip(),
            failed_sql=failed_sql.strip(),
            error_message=error_message.strip(),
            clause_type_upper=clause_type_upper
        )
    
    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content)
    ]
    
    try:
        response = llm.invoke(messages)
        raw_content = response.content
        
        # Handle cases where content is returned as list of parts
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
            repaired_clause = "".join(text_parts)
        else:
            repaired_clause = str(raw_content)

        repaired_clause = repaired_clause.strip()
        
        # Clean up markdown fences
        if repaired_clause.startswith("```sql"):
            repaired_clause = repaired_clause.split("```sql", 1)[1]
        if repaired_clause.startswith("```"):
            repaired_clause = repaired_clause.split("```", 1)[1]
        if repaired_clause.endswith("```"):
            repaired_clause = repaired_clause.rsplit("```", 1)[0]
            
        repaired_clause = repaired_clause.strip()
        logger.info(f"Received repaired clause from LLM: '{repaired_clause}'")

        # Step 4: Parse the corrected clause using a dummy query and surgically graft into AST
        dummy_query = f"SELECT * FROM dummy_table {repaired_clause}"
        try:
            parsed_dummy = sqlglot.parse_one(dummy_query)
        except Exception as pe:
            logger.error(f"Failed to parse dummy query with repaired clause: '{dummy_query}'. Err: {pe}")
            return None

        # Surgical graft using AST key setting
        if clause_type == "joins":
            joins = parsed_dummy.args.get("joins")
            if joins is not None:
                parsed.set("joins", joins)
            else:
                logger.error("No joins found in LLM join clause output.")
                return None
        else:
            node = parsed_dummy.args.get(clause_type)
            if node is not None:
                parsed.set(clause_type, node)
            else:
                logger.error(f"No '{clause_type}' node found in LLM clause output.")
                return None

        # Step 5: Compile corrected AST back to SQL
        repaired_sql = parsed.sql()
        logger.info(f"Successfully repaired SQL via AST graft:\n{repaired_sql}")
        return repaired_sql

    except Exception as e:
        logger.exception("Exception occurred during AST clause repair")
        return None
