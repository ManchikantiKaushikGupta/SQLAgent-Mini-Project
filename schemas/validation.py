"""
Validation & Correction Pydantic Schemas

Defines structural models for SQL semantic checks and LLM-driven query corrections.
"""

from pydantic import BaseModel, Field
from typing import Optional

class SemanticValidationResult(BaseModel):
    """
    Structured response representing the semantic correctness verification of a generated SQL query.
    """
    is_valid: bool = Field(
        ..., 
        description="Whether the SQL query is semantically correct and accurately answers the user's intent."
    )
    reason: str = Field(
        ..., 
        description="Detailed explanation of why the query is correct or incorrect (logical bugs, missing joins, wrong filters)."
    )
    suggested_fix: Optional[str] = Field(
        None, 
        description="If invalid, a suggestion of how to fix the query (e.g., 'Use LEFT JOIN instead of INNER JOIN')."
    )


from schemas.error_taxonomy import SQLErrorClassification

class SQLCorrectionResult(BaseModel):
    """
    Structured response representing the output of the query correction agent.
    """
    thought_process: str = Field(
        ..., 
        description="Chain-of-thought analysis describing what syntax or logical error occurred and how it is being repaired."
    )
    corrected_sql: str = Field(
        ..., 
        description="The finalized, fully corrected raw SELECT SQL statement."
    )
    error_classification: Optional[SQLErrorClassification] = None

