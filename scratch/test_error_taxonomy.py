import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.error_taxonomy import SQLErrorClassification
from schemas.validation import SQLCorrectionResult
from features.validation_correction.error_classifier import (
    classify_sql_error,
    fallback_classify_error
)
from features.validation_correction.repair_engine import repair_sql_clause
from features.validation_correction.agent import correct_sql
from observability.metrics import record_correction, init_metrics_state


class MockAIMessage:
    """Mock of LangChain AIMessage response."""
    def __init__(self, content: str):
        self.content = content
        self.text = content


class TestErrorTaxonomyEngine(unittest.TestCase):

    def setUp(self):
        self.schema = "CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR, price DECIMAL, category_id INT);"
        self.original_query = "List high-priced products sorted by name"
        self.failed_sql = "SELECT id, name, price FROM products WHERE price > 'expensive' ORDER BY name;"
        self.error_message = "SQL Syntax Error: invalid input syntax for type decimal: 'expensive'"

    def test_fallback_classification_matching(self):
        """Verify rule-based taxonomy heuristics on common SQL failures."""
        # 1. Aggregation error
        res1 = fallback_classify_error(
            "SELECT category_id, SUM(price) FROM products",
            "column 'category_id' must appear in the GROUP BY clause or be used in an aggregate function",
            "..."
        )
        self.assertEqual(res1.category, "AggregationError")
        self.assertEqual(res1.failing_clause, "group")

        # 2. Join error
        res2 = fallback_classify_error(
            "SELECT * FROM products JOIN categories",
            "cannot join products and categories: ON clause is missing",
            "..."
        )
        self.assertEqual(res2.category, "JoinError")
        self.assertEqual(res2.failing_clause, "joins")

        # 3. Filter error
        res3 = fallback_classify_error(
            self.failed_sql,
            self.error_message,
            self.original_query
        )
        self.assertEqual(res3.category, "FilterError")
        self.assertEqual(res3.failing_clause, "where")

        # 4. Limit error
        res4 = fallback_classify_error(
            "SELECT * FROM products LIMIT -5",
            "LIMIT value must be a non-negative integer",
            "..."
        )
        self.assertEqual(res4.category, "LimitError")
        self.assertEqual(res4.failing_clause, "limit")

        # 5. Schema error
        res5 = fallback_classify_error(
            "SELECT quantity FROM products",
            "column 'quantity' does not exist in relation 'products'",
            "..."
        )
        self.assertEqual(res5.category, "SchemaError")
        self.assertEqual(res5.failing_clause, "unknown")

    @patch("features.validation_correction.error_classifier.get_llm")
    def test_llm_based_error_classification(self, mock_get_llm):
        """Verify LLM-driven structured error classification parsing."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        mock_response = MockAIMessage(
            content="""
            {
                "category": "FilterError",
                "subcategory": "Invalid filter literal type",
                "description": "Filtering a decimal column with a string literal 'expensive'.",
                "failing_clause": "where",
                "suggested_fix": "Change the literal comparison value to a decimal number like 100.0"
            }
            """
        )
        mock_llm.invoke.return_value = mock_response

        classification = classify_sql_error(
            self.failed_sql,
            self.error_message,
            self.schema,
            self.original_query
        )

        self.assertIsInstance(classification, SQLErrorClassification)
        self.assertEqual(classification.category, "FilterError")
        self.assertEqual(classification.subcategory, "Invalid filter literal type")
        self.assertEqual(classification.failing_clause, "where")
        self.assertEqual(classification.suggested_fix, "Change the literal comparison value to a decimal number like 100.0")

    @patch("features.validation_correction.repair_engine.get_llm")
    def test_taxonomy_aware_clause_repair(self, mock_get_llm):
        """Verify AST clause repair with taxonomy classification context."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        mock_response = MockAIMessage(
            content="WHERE products.price > 100.00"
        )
        mock_llm.invoke.return_value = mock_response

        classification = SQLErrorClassification(
            category="FilterError",
            subcategory="Invalid filter literal type",
            description="Comparing decimal column to string",
            failing_clause="where",
            suggested_fix="Compare against decimal 100.00"
        )

        repaired_sql = repair_sql_clause(
            failed_sql=self.failed_sql,
            error_message=self.error_message,
            schema=self.schema,
            original_query=self.original_query,
            classification=classification
        )

        self.assertIsNotNone(repaired_sql)
        self.assertIn("WHERE products.price > 100.00", repaired_sql)
        self.assertTrue("ORDER BY products.name" in repaired_sql or "ORDER BY name" in repaired_sql)

    @patch("features.validation_correction.agent.classify_sql_error")
    @patch("features.validation_correction.agent.repair_sql_clause")
    def test_correct_sql_integration_ast(self, mock_repair_sql_clause, mock_classify):
        """Verify taxonomy integration in correct_sql when AST repair succeeds."""
        classification = SQLErrorClassification(
            category="FilterError",
            subcategory="Invalid literal",
            description="Decimal vs string literal error",
            failing_clause="where",
            suggested_fix="Compare with decimal"
        )
        mock_classify.return_value = classification

        repaired_sql = "SELECT id, name, price FROM products WHERE price > 100.0 ORDER BY name;"
        mock_repair_sql_clause.return_value = repaired_sql

        result = correct_sql(
            failed_sql=self.failed_sql,
            error_message=self.error_message,
            schema=self.schema,
            original_query=self.original_query
        )

        self.assertIsInstance(result, SQLCorrectionResult)
        self.assertEqual(result.corrected_sql, repaired_sql)
        self.assertEqual(result.error_classification, classification)

    @patch("features.validation_correction.agent.classify_sql_error")
    @patch("features.validation_correction.agent.repair_sql_clause")
    @patch("features.validation_correction.agent.get_llm")
    def test_correct_sql_integration_fallback(self, mock_get_llm, mock_repair, mock_classify):
        """Verify taxonomy integration in correct_sql when AST fails and falls back to full LLM correction."""
        classification = SQLErrorClassification(
            category="SchemaError",
            subcategory="Invalid column",
            description="Column does not exist",
            failing_clause="unknown",
            suggested_fix="Query valid columns"
        )
        mock_classify.return_value = classification
        mock_repair.return_value = None

        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_response = MockAIMessage(
            content="""
            {
                "thought_process": "Fallback full correction based on SchemaError.",
                "corrected_sql": "SELECT id, name, price FROM products ORDER BY name;"
            }
            """
        )
        mock_llm.invoke.return_value = mock_response

        result = correct_sql(
            failed_sql=self.failed_sql,
            error_message=self.error_message,
            schema=self.schema,
            original_query=self.original_query
        )

        self.assertIsInstance(result, SQLCorrectionResult)
        self.assertEqual(result.corrected_sql, "SELECT id, name, price FROM products ORDER BY name;")
        self.assertEqual(result.error_classification, classification)

    def test_telemetry_taxonomy_storage(self):
        """Verify record_correction stores taxonomy metadata correctly inside metrics."""
        state = {}
        init_metrics_state(state)

        classification = SQLErrorClassification(
            category="JoinError",
            subcategory="Missing join",
            description="ON clause missing on categories table",
            failing_clause="joins",
            suggested_fix="Add ON products.category_id = categories.id"
        )

        record_correction(
            state=state,
            attempt_number=1,
            failed_sql="SELECT * FROM products JOIN categories",
            error_message="Missing join condition",
            corrected_sql="SELECT * FROM products JOIN categories ON products.category_id = categories.id",
            thought_process="Add ON condition to connect foreign key.",
            error_classification=classification
        )

        history = state["metrics"]["correction_history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["attempt"], 1)
        self.assertIsNotNone(history[0]["error_taxonomy"])
        self.assertEqual(history[0]["error_taxonomy"]["category"], "JoinError")
        self.assertEqual(history[0]["error_taxonomy"]["subcategory"], "Missing join")
        self.assertEqual(history[0]["error_taxonomy"]["failing_clause"], "joins")


if __name__ == "__main__":
    unittest.main()
