import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from features.validation_correction.repair_engine import (
    detect_failing_clause,
    repair_sql_clause,
)

class TestASTRepairEngine(unittest.TestCase):
    
    def test_clause_detection(self):
        # 1. GROUP BY error
        self.assertEqual(detect_failing_clause("column 'users.id' must appear in the GROUP BY clause or be used in an aggregate function"), "group")
        self.assertEqual(detect_failing_clause("non-aggregated column 'amount' in SELECT"), "group")
        
        # 2. JOIN error
        self.assertEqual(detect_failing_clause("cannot join users and orders: ON clause is missing"), "joins")
        self.assertEqual(detect_failing_clause("ambiguous column reference: id"), "joins")
        
        # 3. WHERE error
        self.assertEqual(detect_failing_clause("where clause error: column status does not exist"), "where")
        self.assertEqual(detect_failing_clause("no such column: active in filter"), "where")
        
        # 4. LIMIT error
        self.assertEqual(detect_failing_clause("LIMIT value must be a non-negative integer"), "limit")
        
        # 5. ORDER BY error
        self.assertEqual(detect_failing_clause("invalid ORDER BY sorting column name"), "order")
        
        # 6. Unknown error
        self.assertIsNone(detect_failing_clause("mismatched parenthesis at line 1"))

    @patch("features.validation_correction.repair_engine.get_llm")
    def test_surgical_where_clause_repair(self, mock_get_llm):
        # Mock LLM invoke return
        mock_response = MagicMock()
        mock_response.content = "WHERE orders.status = 'completed'"
        
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        failed_sql = "SELECT users.name FROM users JOIN orders ON users.id = orders.user_id WHERE orders.status = 'broken' GROUP BY users.name"
        schema = "Table: users\n  - id (INTEGER)\n  - name (VARCHAR)\nTable: orders\n  - id (INTEGER)\n  - user_id (INTEGER)\n  - status (VARCHAR)"
        error_msg = "where clause has invalid value 'broken' in filter"
        original_query = "Show user names for completed orders"
        
        repaired_sql = repair_sql_clause(
            failed_sql=failed_sql,
            error_message=error_msg,
            schema=schema,
            original_query=original_query
        )
        
        # Verify the surgical WHERE patch occurred, preserving JOIN and GROUP BY
        self.assertIsNotNone(repaired_sql)
        self.assertIn("WHERE orders.status = 'completed'", repaired_sql)
        self.assertIn("GROUP BY users.name", repaired_sql)
        self.assertIn("JOIN orders ON users.id = orders.user_id", repaired_sql)

    @patch("features.validation_correction.repair_engine.get_llm")
    def test_surgical_group_by_repair(self, mock_get_llm):
        mock_response = MagicMock()
        mock_response.content = "GROUP BY users.id, users.name"
        
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        failed_sql = "SELECT users.id, users.name, SUM(orders.amount) FROM users JOIN orders ON users.id = orders.user_id GROUP BY users.id"
        schema = "..."
        error_msg = "column 'users.name' must appear in the GROUP BY clause or be used in an aggregate function"
        original_query = "..."
        
        repaired_sql = repair_sql_clause(
            failed_sql=failed_sql,
            error_message=error_msg,
            schema=schema,
            original_query=original_query
        )
        
        self.assertIsNotNone(repaired_sql)
        self.assertIn("GROUP BY users.id, users.name", repaired_sql)

if __name__ == "__main__":
    unittest.main()
