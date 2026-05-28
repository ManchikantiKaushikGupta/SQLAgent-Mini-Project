"""
Execution Accuracy Engine

Executes generated SQL queries and reference SQL queries against the database
and compares their result sets using robust, semantic cell-by-cell matching,
handling alias names, key orders, and sorting differences.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from db.database import execute_sql_query

logger = logging.getLogger(__name__)

def normalize_results(
    rows: List[Dict[str, Any]], 
    order_sensitive: bool = False, 
    ignore_column_names: bool = True
) -> List[Tuple[Any, ...]]:
    """
    Normalizes the database result rows for semantic comparison.
    
    Args:
        rows: List of dicts representing rows returned by a query.
        order_sensitive: If True, maintains the returned row ordering.
                         If False, sorts rows in a consistent order.
        ignore_column_names: If True, compares only the values in each row rather than keys,
                             which makes the comparison independent of column aliasing (e.g. total vs sum_amount).
                             
    Returns:
        A normalized list of value tuples representing the rows.
    """
    if not rows:
        return []
        
    normalized = []
    for row in rows:
        if ignore_column_names:
            # Order values by key sorting to ensure consistent column mapping
            row_values = tuple(row[k] for k in sorted(row.keys()))
        else:
            row_values = tuple((k, row[k]) for k in sorted(row.keys()))
            
        # Float rounding for precision safety in comparisons
        rounded_row_values = tuple(
            round(val, 4) if isinstance(val, float) else val
            for val in row_values
        )
        normalized.append(rounded_row_values)
        
    if not order_sensitive:
        # Sort tuples so the collection of rows is order-insensitive.
        # Use str(x) as key to handle different types safely in Python 3.
        normalized.sort(key=lambda x: str(x))
        
    return normalized

def compare_results(
    generated_rows: List[Dict[str, Any]], 
    reference_rows: List[Dict[str, Any]], 
    order_sensitive: bool = False
) -> Tuple[bool, str]:
    """
    Compares the execution result set of generated SQL against the reference SQL.
    
    Args:
        generated_rows: Rows returned by the generated SQL query.
        reference_rows: Rows returned by the reference SQL query.
        order_sensitive: Whether ordering is critical.
        
    Returns:
        A tuple of (is_correct: bool, explanation: str).
    """
    # 1. Compare row count
    if len(generated_rows) != len(reference_rows):
        return False, f"Row count mismatch: generated returned {len(generated_rows)} rows, reference returned {len(reference_rows)} rows."
        
    if not generated_rows and not reference_rows:
        return True, "Both result sets are empty (equivalent)."
        
    # 2. Compare using column-independent normalization (ignore aliases but check exact cell values)
    gen_norm = normalize_results(generated_rows, order_sensitive=order_sensitive, ignore_column_names=True)
    ref_norm = normalize_results(reference_rows, order_sensitive=order_sensitive, ignore_column_names=True)
    
    if gen_norm == ref_norm:
        return True, "Execution results are semantically identical."
        
    # 3. If they don't match, check if they would match WITH column names (shouldn't happen, but good check)
    gen_norm_with_cols = normalize_results(generated_rows, order_sensitive=order_sensitive, ignore_column_names=False)
    ref_norm_with_cols = normalize_results(reference_rows, order_sensitive=order_sensitive, ignore_column_names=False)
    
    if gen_norm_with_cols == ref_norm_with_cols:
        return True, "Execution results match exactly (including column aliases)."
        
    # Build detailed mismatch helper
    return False, "Execution data cells or order do not match reference results."

def evaluate_execution_accuracy(
    generated_sql: Optional[str],
    reference_sql: str,
    order_sensitive: bool = False
) -> Tuple[bool, str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes both the generated SQL and reference SQL on the database, and compares results.
    
    Args:
        generated_sql: The agent-generated SQL.
        reference_sql: The golden ground truth SQL.
        order_sensitive: True if sorting is critical.
        
    Returns:
        A tuple of (success: bool, explanation: str, generated_rows: list, reference_rows: list)
    """
    reference_rows = []
    generated_rows = []
    
    # 1. Execute Reference SQL first
    try:
        reference_rows = execute_sql_query(reference_sql)
    except Exception as e:
        logger.error(f"Error executing reference SQL: '{reference_sql}'. Error: {str(e)}")
        return False, f"Broken reference SQL: {str(e)}", [], []
        
    # 2. Check if generated SQL is missing
    if not generated_sql:
        return False, "No generated SQL query provided.", [], reference_rows
        
    # 3. Execute Generated SQL
    try:
        generated_rows = execute_sql_query(generated_sql)
    except Exception as e:
        logger.info(f"Execution error on generated SQL: '{generated_sql}'. Error: {str(e)}")
        return False, f"Execution failed: {str(e)}", [], reference_rows
        
    # 4. Compare the result sets
    success, explanation = compare_results(generated_rows, reference_rows, order_sensitive)
    return success, explanation, generated_rows, reference_rows
