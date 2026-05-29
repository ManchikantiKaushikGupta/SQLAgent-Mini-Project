import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.validation import SemanticValidationResult
from features.validation_correction.semantic_validator import (
    validate_sql_semantics,
    run_rule_based_semantic_checks
)

class MockAIMessage:
    """Mock of LangChain AIMessage response."""
    def __init__(self, content: str):
        self.content = content
        self.text = content


class TestSemanticValidatorHybrid(unittest.TestCase):

    def setUp(self):
        self.schema = "CREATE TABLE users (id INT PRIMARY KEY, first_name VARCHAR, is_premium BOOLEAN);"

    def test_rule_based_filter_mismatch(self):
        """Verify that a missing filter literal triggers a rule violation warning alert."""
        refined_query = "Show users in London"
        sql_query = "SELECT * FROM users;" # Missing WHERE city = 'London' filter
        results = [{"id": 1, "first_name": "Alice"}]
        
        alerts = run_rule_based_semantic_checks(sql_query, refined_query, results)
        self.assertEqual(len(alerts), 1)
        self.assertIn("references filter criteria 'london'", alerts[0])

    def test_rule_based_aggregation_mismatch(self):
        """Verify that missing AVG or SUM aggregate functions triggers a rule violation warning alert."""
        refined_query = "Calculate the average spent by users"
        sql_query = "SELECT spent FROM users;" # Missing AVG
        results = [{"spent": 50.00}]
        
        alerts = run_rule_based_semantic_checks(sql_query, refined_query, results)
        self.assertTrue(len(alerts) >= 1)
        self.assertTrue(any("AVG() aggregate function" in a for a in alerts))

    def test_rule_based_limit_mismatch(self):
        """Verify that missing LIMIT or ORDER BY on top-ranked intent triggers warning alerts."""
        refined_query = "Show top 5 premium users"
        sql_query = "SELECT * FROM users WHERE is_premium = true;" # Missing LIMIT and ORDER BY
        results = [{"id": 1, "first_name": "Alice"}]
        
        alerts = run_rule_based_semantic_checks(sql_query, refined_query, results)
        self.assertEqual(len(alerts), 2)
        self.assertTrue(any("LIMIT clause" in a for a in alerts))
        self.assertTrue(any("ORDER BY clause" in a for a in alerts))

    def test_rule_based_empty_results(self):
        """Verify that execution yielding exactly 0 rows triggers a warning alert for record-seeking queries."""
        refined_query = "List premium members"
        sql_query = "SELECT * FROM users WHERE is_premium = true;"
        results = [] # 0 rows
        
        alerts = run_rule_based_semantic_checks(sql_query, refined_query, results)
        self.assertEqual(len(alerts), 1)
        self.assertIn("returned 0 rows", alerts[0])

    @patch("features.validation_correction.semantic_validator.get_llm")
    def test_hybrid_llm_validation_passes_alerts(self, mock_get_llm):
        """Verify that validate_sql_semantics successfully passes computed alerts to the LLM."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        mock_response = MockAIMessage(
            content="""
            {
                "is_valid": false,
                "reason": "The query lacks the required LIMIT and ORDER BY clauses to show the top 5.",
                "suggested_fix": "Add ORDER BY signup_date DESC LIMIT 5"
            }
            """
        )
        mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = validate_sql_semantics(
            sql_query="SELECT * FROM users WHERE is_premium = true;",
            results=[{"id": 1, "first_name": "Alice"}],
            refined_query="Show top 5 premium users",
            schema=self.schema
        )
        
        # Assertions
        self.assertIsInstance(result, SemanticValidationResult)
        self.assertFalse(result.is_valid)
        self.assertIn("LIMIT and ORDER BY", result.reason)
        self.assertEqual(result.suggested_fix, "Add ORDER BY signup_date DESC LIMIT 5")
        
        # Verify that the LLM invocation system/human prompt was called
        self.assertTrue(mock_llm.invoke.called)
        human_msg = mock_llm.invoke.call_args[0][0][1].content
        self.assertIn("[ALERT]", human_msg)
        self.assertIn("lacks a LIMIT clause", human_msg)


if __name__ == "__main__":
    unittest.main()
