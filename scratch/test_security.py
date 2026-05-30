"""
Security and Governance Test Suite

Validates all security, safety, and RBAC requirements outlined in Priority 11:
1. Input PII Redaction
2. Dynamic Schema Pruning by Role
3. SQL AST RBAC (Table and Column permissions)
4. SELECT-only and System Table Protection
5. LIMIT Clamping / Injection
6. Result Set PII Masking
7. Structured JSON Audit Logging
8. E2E LangGraph Secure Executions
"""

import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.security import get_security_manager, SecurityException, RolePermissions
from core.graph import build_workflow
from db.database import get_database_schema

class TestProductionSecurity(unittest.TestCase):
    def setUp(self):
        self.sec_mgr = get_security_manager()
        self.audit_log_path = os.path.abspath("observability/audit_log.json")
        # Clean audit log for absolute test isolation
        if os.path.exists(self.audit_log_path):
            try:
                os.remove(self.audit_log_path)
            except Exception:
                with open(self.audit_log_path, "w") as f:
                    f.write("")

    def test_pii_input_redaction(self):
        """1. Verify PII in user questions is properly redacted before hitting LLMs."""
        redactor = self.sec_mgr.redactor
        
        # Test Email Redaction
        q_email = "Find orders for user john.doe@example.com immediately"
        redacted_email = redactor.redact_text(q_email)
        self.assertNotIn("john.doe@example.com", redacted_email)
        self.assertIn("<EMAIL>", redacted_email)

        # Test Phone Redaction
        q_phone = "Look up customer with phone +1-555-0199 or 5550299"
        redacted_phone = redactor.redact_text(q_phone)
        self.assertNotIn("555-0199", redacted_phone)
        self.assertIn("<PHONE_NUMBER>", redacted_phone)

    def test_dynamic_schema_pruning(self):
        """2. Verify schema pruning removes unauthorized tables and columns by role."""
        raw_schema = (
            "Table: users\n"
            "  - id (INTEGER) [PRIMARY KEY]\n"
            "  - first_name (VARCHAR)\n"
            "  - last_name (VARCHAR)\n"
            "  - email (VARCHAR)\n\n"
            "Table: products\n"
            "  - id (INTEGER) [PRIMARY KEY]\n"
            "  - name (VARCHAR)\n"
            "  - price (FLOAT)"
        )

        # Restricted role can only see 'products', not 'users'
        pruned_restricted = self.sec_mgr.prune_schema_for_role(raw_schema, "restricted_user")
        self.assertNotIn("Table: users", pruned_restricted)
        self.assertNotIn("email", pruned_restricted)
        self.assertIn("Table: products", pruned_restricted)

        # Analyst can see 'users' but NOT sensitive columns (first_name, last_name, email)
        pruned_analyst = self.sec_mgr.prune_schema_for_role(raw_schema, "analyst")
        self.assertIn("Table: users", pruned_analyst)
        self.assertNotIn("email", pruned_analyst)
        self.assertNotIn("first_name", pruned_analyst)
        self.assertIn("id (INTEGER)", pruned_analyst)

        # Admin can see everything
        pruned_admin = self.sec_mgr.prune_schema_for_role(raw_schema, "admin")
        self.assertIn("Table: users", pruned_admin)
        self.assertIn("email", pruned_admin)
        self.assertIn("Table: products", pruned_admin)

    def test_sql_ast_rbac_and_safety(self):
        """3. Verify SELECT-only, system table protection, and table-level RBAC."""
        
        # Test SELECT-only block
        delete_sql = "DELETE FROM products WHERE id = 1"
        with self.assertRaises(SecurityException) as ctx:
            self.sec_mgr.validate_sql_security(delete_sql, "admin")
        self.assertIn("Only SELECT statements are allowed", str(ctx.exception))

        # Test System Table Protection
        sys_sql = "SELECT * FROM sqlite_master"
        with self.assertRaises(SecurityException) as ctx:
            self.sec_mgr.validate_sql_security(sys_sql, "admin")
        self.assertIn("metadata table access is forbidden", str(ctx.exception))

        # Test Table access rejection for restricted user
        unauth_table_sql = "SELECT * FROM users"
        with self.assertRaises(SecurityException) as ctx:
            self.sec_mgr.validate_sql_security(unauth_table_sql, "restricted_user")
        self.assertIn("Unauthorized table access", str(ctx.exception))

        # Test Allowed table access for restricted user
        auth_table_sql = "SELECT id, name FROM products"
        safe_sql = self.sec_mgr.validate_sql_security(auth_table_sql, "restricted_user")
        self.assertIn("SELECT", safe_sql)

    def test_sql_ast_column_rbac(self):
        """4. Verify column-level RBAC restrictions (e.g. Analyst accessing email)."""
        
        # Analyst queries allowed columns
        allowed_sql = "SELECT id FROM users"
        safe_sql = self.sec_mgr.validate_sql_security(allowed_sql, "analyst")
        self.assertIn("SELECT", safe_sql)

        # Analyst queries restricted column email
        denied_sql = "SELECT email FROM users"
        with self.assertRaises(SecurityException) as ctx:
            self.sec_mgr.validate_sql_security(denied_sql, "analyst")
        self.assertIn("Unauthorized column access", str(ctx.exception))

        # Analyst queries implicit restricted column via SELECT *
        denied_star_sql = "SELECT * FROM users"
        with self.assertRaises(SecurityException) as ctx:
            self.sec_mgr.validate_sql_security(denied_star_sql, "analyst")
        self.assertIn("SELECT * is not allowed", str(ctx.exception))

    def test_limit_enforcement(self):
        """5. Verify SQL limits are clamped or injected based on role threshold."""
        
        # No LIMIT clause: Verify injection
        sql_no_limit = "SELECT * FROM products"
        safe_sql = self.sec_mgr.validate_sql_security(sql_no_limit, "restricted_user")
        self.assertIn("LIMIT 50", safe_sql)

        # Excessive LIMIT clause: Verify clamping
        sql_high_limit = "SELECT * FROM products LIMIT 500"
        safe_sql = self.sec_mgr.validate_sql_security(sql_high_limit, "restricted_user")
        self.assertIn("LIMIT 50", safe_sql)
        self.assertNotIn("LIMIT 500", safe_sql)

        # Allow valid limits under threshold
        sql_valid_limit = "SELECT * FROM products LIMIT 10"
        safe_sql = self.sec_mgr.validate_sql_security(sql_valid_limit, "restricted_user")
        self.assertIn("LIMIT 10", safe_sql)

    def test_result_pii_masking(self):
        """6. Verify returned database records are masked for sensitive fields."""
        results = [
            {"id": 1, "first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "price": 99.9},
            {"id": 2, "first_name": "Bob", "last_name": "Jones", "email": "bob@example.com", "price": 149.9}
        ]

        # Admin gets raw results
        admin_perms = self.sec_mgr.get_role_permissions("admin")
        admin_res = self.sec_mgr.redactor.redact_results(results, admin_perms)
        self.assertEqual(admin_res[0]["email"], "alice@example.com")
        self.assertEqual(admin_res[0]["first_name"], "Alice")

        # Manager gets masked results
        manager_perms = self.sec_mgr.get_role_permissions("manager")
        manager_res = self.sec_mgr.redactor.redact_results(results, manager_perms)
        self.assertNotEqual(manager_res[0]["email"], "alice@example.com")
        self.assertIn("****", manager_res[0]["email"])
        self.assertEqual(manager_res[0]["first_name"], "A***")
        self.assertEqual(manager_res[0]["last_name"], "S***")
        self.assertEqual(manager_res[0]["price"], 99.9) # Non-PII unchanged

    def test_structured_audit_logging(self):
        """7. Verify security actions write clean events to observability/audit_log.json."""
        # Trigger some validations to write events
        try:
            self.sec_mgr.validate_sql_security("SELECT * FROM users", "restricted_user", username="test_hacker")
        except SecurityException:
            pass

        self.sec_mgr.validate_sql_security("SELECT * FROM products LIMIT 5", "restricted_user", username="test_guest")

        self.assertTrue(os.path.exists(self.audit_log_path))
        
        events = []
        with open(self.audit_log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))

        # Check that we recorded violations and passes
        actions = [e["action"] for e in events]
        self.assertIn("security_violation", actions)
        self.assertIn("sql_validation_passed", actions)

        # Inspect a violation event
        violation = next(e for e in events if e["action"] == "security_violation")
        self.assertEqual(violation["username"], "test_hacker")
        self.assertEqual(violation["role"], "restricted_user")

    @patch("db.database.execute_sql_query")
    @patch("features.intent_clarification.agent.get_llm")
    @patch("features.query_planning.agent.get_llm")
    @patch("features.sql_generation.agent.get_llm")
    @patch("features.validation_correction.agent.get_llm")
    @patch("features.validation_correction.semantic_validator.get_llm")
    @patch("features.validation_correction.error_classifier.get_llm")
    def test_e2e_graph_security(self, mock_err_llm, mock_sem_llm, mock_corr_llm, mock_sql_llm, mock_plan_llm, mock_intent_llm, mock_execute_sql):
        """8. Run end-to-end security scenarios through the LangGraph workflow."""
        # Setup mock LLM for local E2E simulation to avoid hitting API rate limits
        mock_llm = MagicMock()
        mock_err_llm.return_value = mock_llm
        mock_sem_llm.return_value = mock_llm
        mock_corr_llm.return_value = mock_llm
        mock_sql_llm.return_value = mock_llm
        mock_plan_llm.return_value = mock_llm
        mock_intent_llm.return_value = mock_llm
        
        # Setup mock database execution so it always succeeds without a live connection
        mock_execute_sql.return_value = [{"id": 1, "name": "Model A", "price": 99.9}]

        class MockAIMessage:
            def __init__(self, content):
                self.content = content
                self.text = content
                self.response_metadata = {}
                self.usage_metadata = {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20}
                
        def mock_llm_invoke(messages, *args, **kwargs):
            from langchain_core.messages import SystemMessage
            system_msg = ""
            human_msg = ""
            for m in messages:
                if isinstance(m, SystemMessage):
                    system_msg += m.content.lower()
                else:
                    human_msg += getattr(m, "content", "").lower()
            
            # 1. SQL Generator Agent
            if "writer" in system_msg or "sql query writer" in system_msg:
                if "users" in human_msg or "emails" in human_msg:
                    return MockAIMessage("SELECT email FROM users;")
                return MockAIMessage("SELECT id, name FROM products LIMIT 3;")

            # 2. Query Planner Agent
            elif "planner" in system_msg or "query planner" in system_msg:
                if "emails" in human_msg or "users" in human_msg:
                    return MockAIMessage(json.dumps({
                        "thought_process": "Planning query to get user emails.",
                        "tables": [{"table_name": "users", "purpose": "source of emails"}],
                        "joins": [],
                        "filters": [],
                        "aggregations": [],
                        "group_by": [],
                        "order_by": [],
                        "limit": None
                    }))
                else:
                    return MockAIMessage(json.dumps({
                        "thought_process": "Planning query to list products.",
                        "tables": [{"table_name": "products", "purpose": "source of products"}],
                        "joins": [],
                        "filters": [],
                        "aggregations": [],
                        "group_by": [],
                        "order_by": [],
                        "limit": 3
                    }))

            # 3. Semantic Validator Agent
            elif "semantic" in system_msg:
                return MockAIMessage(json.dumps({
                    "is_valid": True,
                    "reason": "The query is semantically correct."
                }))

            # 4. SQL Correction Agent / Error Classifier
            elif "correction" in system_msg or "repair" in system_msg or "taxonomy" in system_msg:
                return MockAIMessage(json.dumps({
                    "thought_process": "Mocking correction.",
                    "corrected_sql": "SELECT id, name FROM products LIMIT 3;"
                }))
            
            # 5. Intent Clarification Agent
            elif "intent" in system_msg or "clarify" in system_msg:
                if "emails" in human_msg or "users" in human_msg:
                    return MockAIMessage("Give me emails from users table")
                return MockAIMessage("List 3 products")
                
            # Fallback
            return MockAIMessage("SELECT id, name FROM products LIMIT 3;")
            
        mock_llm.invoke.side_effect = mock_llm_invoke

        app = build_workflow()

        # E2E Case 1: Restricted user tries to query users (Should fail with security exception terminal block)
        state_violation = {
            "original_query": "Give me emails from users table",
            "db_schema": get_database_schema(),
            "refined_query": "",
            "query_plan": "",
            "sql_query": "SELECT email FROM users", # Injected to trigger validation directly
            "error_message": None,
            "retry_count": 0,
            "final_result": None,
            "user_role": "restricted_user",
            "username": "alice_guest",
            "security_error": None
        }

        final_state = app.invoke(state_violation)
        self.assertIsNotNone(final_state.get("error_message"))
        self.assertIn("Security Exception", final_state["error_message"])
        self.assertIsNotNone(final_state.get("security_error"))
        # Verify it terminated immediately and did NOT try to correct/retry
        self.assertEqual(final_state["retry_count"], 3) # MAX_RETRIES = 3

        # E2E Case 2: Restricted user querying products (Should succeed with schema retriever pruned)
        state_success = {
            "original_query": "List 3 products",
            "db_schema": get_database_schema(),
            "refined_query": "",
            "query_plan": "",
            "sql_query": "",
            "error_message": None,
            "retry_count": 0,
            "final_result": None,
            "user_role": "restricted_user",
            "username": "bob_restricted",
            "security_error": None
        }

        final_state_success = app.invoke(state_success)
        # Check that the pruned schema hid users
        self.assertNotIn("Table: users", final_state_success.get("db_schema", ""))
        self.assertIn("Table: products", final_state_success.get("db_schema", ""))
        self.assertIsNone(final_state_success.get("error_message"))
        self.assertIsNotNone(final_state_success.get("sql_query"))
        # Verify LIMIT clamped/injected to 50 because user didn't specify, or top 3 is preserved (LIMIT 3 is < 50)
        self.assertIn("LIMIT", final_state_success.get("sql_query"))

if __name__ == "__main__":
    unittest.main()
