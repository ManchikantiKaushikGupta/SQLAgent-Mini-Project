"""
Unit test suite using mock LLM responses to verify SQL validation,
correction, and telemetry recording without reaching the live API.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.validation import SemanticValidationResult, SQLCorrectionResult
from schemas.error_taxonomy import SQLErrorClassification
from features.validation_correction.semantic_validator import validate_sql_semantics
from features.validation_correction.agent import correct_sql, validate_sql_safety
from observability.metrics import record_correction, init_metrics_state


class MockAIMessage:
    """A clean, realistic mock of a LangChain AIMessage response."""
    def __init__(self, content: str):
        self.content = content
        self.text = content



class TestValidationAndCorrectionMock(unittest.TestCase):

    def setUp(self):
        self.schema = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR, email VARCHAR);"
        self.original_query = "Show all users named John"
        self.failed_sql = "SELECT id, name, email FROM users WHERE name = John;"
        self.error_message = "SQL Syntax Error: column 'John' does not exist"

    @patch("features.validation_correction.semantic_validator.get_llm")
    def test_semantic_validation_parsing(self, mock_get_llm):
        """Verify that validate_sql_semantics correctly parses and validates a JSON response using SemanticValidationResult."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        # Mock JSON response from the LLM
        mock_response = MockAIMessage(
            content="""
            ```json
            {
                "is_valid": false,
                "reason": "The query uses an unquoted string literal for the filter value.",
                "suggested_fix": "Change John to 'John'"
            }
            ```
            """
        )
        mock_llm.invoke.return_value = mock_response

        # Execute
        result = validate_sql_semantics(
            sql_query=self.failed_sql,
            results=[],
            refined_query=self.original_query,
            schema=self.schema
        )

        # Assertions
        self.assertIsInstance(result, SemanticValidationResult)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "The query uses an unquoted string literal for the filter value.")
        self.assertEqual(result.suggested_fix, "Change John to 'John'")

    @patch("features.validation_correction.agent.classify_sql_error")
    @patch("features.validation_correction.agent.repair_sql_clause")
    @patch("features.validation_correction.agent.get_llm")
    def test_sql_correction_fallback_to_json(self, mock_get_llm, mock_repair_sql_clause, mock_classify):
        """Verify that correct_sql falls back to LLM JSON parsing on AST repair failure."""
        mock_classify.return_value = SQLErrorClassification(
            category="FilterError",
            subcategory="Invalid literal",
            description="Testing fallback mock",
            failing_clause="where",
            suggested_fix="Fix literal"
        )
        # AST clause repair returns None to trigger fallback
        mock_repair_sql_clause.return_value = None

        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        # Mock structured JSON response matching SQLCorrectionResult
        mock_response = MockAIMessage(
            content="""
            {
                "thought_process": "Quoting the string literal 'John' inside the WHERE filter condition.",
                "corrected_sql": "SELECT id, name, email FROM users WHERE name = 'John';"
            }
            """
        )
        mock_llm.invoke.return_value = mock_response

        # Execute
        result = correct_sql(
            failed_sql=self.failed_sql,
            error_message=self.error_message,
            schema=self.schema,
            original_query=self.original_query
        )

        # Assertions
        self.assertIsInstance(result, SQLCorrectionResult)
        self.assertEqual(result.thought_process, "Quoting the string literal 'John' inside the WHERE filter condition.")
        self.assertEqual(result.corrected_sql, "SELECT id, name, email FROM users WHERE name = 'John';")


    @patch("features.validation_correction.agent.classify_sql_error")
    @patch("features.validation_correction.agent.repair_sql_clause")
    def test_sql_correction_ast_success(self, mock_repair_sql_clause, mock_classify):
        """Verify that correct_sql handles a successful AST clause repair directly."""
        mock_classify.return_value = SQLErrorClassification(
            category="FilterError",
            subcategory="Invalid literal",
            description="Testing AST success mock",
            failing_clause="where",
            suggested_fix="Fix literal"
        )
        expected_sql = "SELECT id, name, email FROM users WHERE name = 'John';"
        mock_repair_sql_clause.return_value = expected_sql

        # Execute
        result = correct_sql(
            failed_sql=self.failed_sql,
            error_message=self.error_message,
            schema=self.schema,
            original_query=self.original_query
        )

        # Assertions
        self.assertIsInstance(result, SQLCorrectionResult)
        self.assertEqual(result.thought_process, "Surgically repaired SQL using clause-level AST grafting.")
        self.assertEqual(result.corrected_sql, expected_sql)

    def test_record_correction_telemetry(self):
        """Verify that record_correction telemetry captures the thought process."""
        state = {}
        init_metrics_state(state)

        record_correction(
            state=state,
            attempt_number=1,
            failed_sql=self.failed_sql,
            error_message=self.error_message,
            corrected_sql="SELECT id, name, email FROM users WHERE name = 'John';",
            thought_process="Wrap 'John' in single quotes to fix string literal syntax error."
        )

        history = state["metrics"]["correction_history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["attempt"], 1)
        self.assertEqual(history[0]["failed_sql"], self.failed_sql)
        self.assertEqual(history[0]["error_message"], self.error_message)
        self.assertEqual(history[0]["corrected_sql"], "SELECT id, name, email FROM users WHERE name = 'John';")
        self.assertEqual(history[0]["thought_process"], "Wrap 'John' in single quotes to fix string literal syntax error.")
        self.assertIn("timestamp", history[0])


if __name__ == "__main__":
    unittest.main()
