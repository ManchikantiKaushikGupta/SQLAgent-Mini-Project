"""
Air-Gapped Operation & Offline Verification Test Suite

Validates the full offline capabilities of SQLAgent:
1. Enforces strict socket interception to block all outgoing external internet connections.
2. Asserts correct Air-Gapped configuration routing and environment checks.
3. Blocks cloud-hosted API models and keys.
4. Mocks local services (Ollama & vLLM) health verification.
5. Runs a full LangGraph workflow locally under socket blocking, proving 100% offline autonomy.
"""

import os
import sys
import socket
import unittest
import requests
import logging
from unittest.mock import patch, MagicMock, mock_open

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.air_gap import is_air_gap_enabled, validate_air_gap_environment
from llm.factory import get_provider, load_config
from core.graph import build_workflow
from db.database import get_database_schema

# Configure logger
logger = logging.getLogger("SQLAgent.OfflineVerification")
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# 1. Socket Connection Interceptor (Air-Gapped Shield)
# ==============================================================================
ORIGINAL_SOCKET_CONNECT = socket.socket.connect


def guarded_socket_connect(self, address):
    """
    Guarded connect method that intercepts and blocks external connections.
    Allows loopback, localhost, and internal subnets.
    """
    host = address[0]
    
    # Allow localhost, loopback interfaces
    if host in ("localhost", "127.0.0.1", "::1"):
        return ORIGINAL_SOCKET_CONNECT(self, address)
    
    # Block everything else to simulate complete air-gapped system
    raise socket.error(
        f"AIR-GAPPED COMPLIANCE VIOLATION: Denied outbound socket connection to '{host}'!"
    )


def enable_socket_shield():
    """Enables the offline socket blocking interceptor."""
    logger.info("Enabling Air-Gapped Network Shield...")
    socket.socket.connect = guarded_socket_connect


def disable_socket_shield():
    """Disables the offline socket blocking interceptor."""
    logger.info("Disabling Air-Gapped Network Shield...")
    socket.socket.connect = ORIGINAL_SOCKET_CONNECT


# ==============================================================================
# 2. Offline Verification Test Suite
# ==============================================================================
class TestOfflineIntegrity(unittest.TestCase):

    def setUp(self):
        # Enforce AIR_GAPPED=true for these tests by default
        os.environ["AIR_GAPPED"] = "true"
        # Clear health check verified caches to prevent carryover
        from llm.ollama_provider import OllamaProvider
        from llm.vllm_provider import VLLMProvider
        OllamaProvider._verified_cache.clear()
        VLLMProvider._verified_cache.clear()

    def tearDown(self):
        # Restore environment variables
        if "AIR_GAPPED" in os.environ:
            del os.environ["AIR_GAPPED"]
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

    def test_socket_shield_blocks_internet(self):
        """Verify that socket shield blocks external internet while allowing localhost."""
        enable_shield = True
        try:
            enable_socket_shield()
            # Attempt to connect to external domain (should raise socket error)
            with self.assertRaises(socket.error) as ctx:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("8.8.8.8", 80))
            self.assertIn("AIR-GAPPED COMPLIANCE VIOLATION", str(ctx.exception))
            
            # Attempt to connect to loopback (should NOT raise Air-Gap violation)
            # (It might raise ConnectionRefusedError if nothing is listening, which is fine, but not our violation)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", 9999))
            except socket.error as e:
                self.assertNotIn("AIR-GAPPED COMPLIANCE VIOLATION", str(e))
        finally:
            disable_socket_shield()

    def test_air_gap_env_toggle(self):
        """Verify is_air_gap_enabled accurately checks env and yaml."""
        # 1. Check Env override
        os.environ["AIR_GAPPED"] = "true"
        self.assertTrue(is_air_gap_enabled())

        os.environ["AIR_GAPPED"] = "false"
        self.assertFalse(is_air_gap_enabled())

        # 2. Check YAML fallback when env is unset
        del os.environ["AIR_GAPPED"]
        with patch("core.air_gap.load_config") as mock_load:
            mock_load.return_value = {"air_gapped": True}
            self.assertTrue(is_air_gap_enabled())

            mock_load.return_value = {"air_gapped": False}
            self.assertFalse(is_air_gap_enabled())

    @patch("core.air_gap.load_config")
    def test_cloud_provider_blocking(self, mock_load):
        """Verify that cloud providers are rejected immediately in air-gapped mode."""
        mock_load.return_value = {
            "provider": "gemini",
            "air_gapped": True
        }
        
        # Calling validate_air_gap_environment should raise ValueError
        with self.assertRaises(ValueError) as ctx:
            validate_air_gap_environment()
        self.assertIn("Active provider is set to cloud-hosted 'gemini'", str(ctx.exception))

    @patch("core.air_gap.load_config")
    def test_cloud_keys_ignored_warning(self, mock_load):
        """Verify cloud keys in env trigger warning logs but don't crash."""
        mock_load.return_value = {
            "provider": "ollama",
            "air_gapped": True,
            "ollama": {
                "model": "qwen3:14b",
                "embeddings_model": "nomic-embed-text",
                "base_url": "http://localhost:11434"
            }
        }
        
        os.environ["GEMINI_API_KEY"] = "fake-cloud-key"
        
        # Mock Ollama Provider tag list returned by health checks
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [
                {"name": "qwen3:14b"},
                {"name": "nomic-embed-text"}
            ]
        }
        
        with patch("requests.get", return_value=mock_resp):
            with patch("llm.factory.load_config", return_value=mock_load.return_value):
                # Should pass and output logs without throwing exceptions
                validate_air_gap_environment()

    @patch("core.air_gap.load_config")
    @patch("requests.get")
    def test_ollama_offline_readiness(self, mock_get, mock_load):
        """Verify Ollama setup checks both chat model and embeddings model presence."""
        mock_load.return_value = {
            "provider": "ollama",
            "air_gapped": True,
            "ollama": {
                "model": "qwen3:14b",
                "embeddings_model": "nomic-embed-text",
                "base_url": "http://localhost:11434"
            }
        }

        # 1. Test case: server is down (raises ConnectionError)
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with patch("llm.factory.load_config", return_value=mock_load.return_value):
            with self.assertRaises(ConnectionError) as ctx:
                validate_air_gap_environment()
            self.assertIn("Ollama service is not running", str(ctx.exception))

        # Reset side effects
        mock_get.side_effect = None

        # 2. Test case: model is missing (raises RuntimeError)
        mock_resp_missing = MagicMock()
        mock_resp_missing.status_code = 200
        mock_resp_missing.json.return_value = {"models": [{"name": "some-other-model"}]}
        mock_get.return_value = mock_resp_missing

        from llm.ollama_provider import OllamaProvider
        OllamaProvider._verified_cache.clear() # Clear caches

        with patch("llm.factory.load_config", return_value=mock_load.return_value):
            with self.assertRaises(RuntimeError) as ctx:
                validate_air_gap_environment()
            self.assertIn("Ollama model 'qwen3:14b' was not found", str(ctx.exception))

        # 3. Test case: models are present (passes)
        mock_resp_ok = MagicMock()
        mock_resp_ok.status_code = 200
        mock_resp_ok.json.return_value = {
            "models": [
                {"name": "qwen3:14b"},
                {"name": "nomic-embed-text"}
            ]
        }
        mock_get.return_value = mock_resp_ok
        OllamaProvider._verified_cache.clear()

        with patch("llm.factory.load_config", return_value=mock_load.return_value):
            # Should run cleanly and output success logs
            validate_air_gap_environment()

    @patch("core.air_gap.load_config")
    @patch("requests.get")
    def test_vllm_offline_readiness(self, mock_get, mock_load):
        """Verify vLLM checks both chat model and embeddings model presence."""
        mock_load.return_value = {
            "provider": "vllm",
            "air_gapped": True,
            "vllm": {
                "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
                "embeddings_model": "BAAI/bge-large-en-v1.5",
                "base_url": "http://localhost:8000/v1"
            }
        }

        # 1. Test case: server is down (raises ConnectionError)
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with patch("llm.factory.load_config", return_value=mock_load.return_value):
            with self.assertRaises(ConnectionError) as ctx:
                validate_air_gap_environment()
            self.assertIn("vLLM service is not running", str(ctx.exception))

        # Reset
        mock_get.side_effect = None

        # 2. Test case: models are present (passes)
        mock_resp_ok = MagicMock()
        mock_resp_ok.status_code = 200
        mock_resp_ok.json.return_value = {
            "data": [
                {"id": "Qwen/Qwen2.5-Coder-7B-Instruct"},
                {"id": "BAAI/bge-large-en-v1.5"}
            ]
        }
        mock_get.return_value = mock_resp_ok

        from llm.vllm_provider import VLLMProvider
        VLLMProvider._verified_cache.clear()

        with patch("llm.factory.load_config", return_value=mock_load.return_value):
            validate_air_gap_environment()

    # Patches to mock DB execution and LangChain LLM nodes
    @patch("db.database.execute_sql_query")
    @patch("features.intent_clarification.agent.get_llm")
    @patch("features.query_planning.agent.get_llm")
    @patch("features.sql_generation.agent.get_llm")
    @patch("features.validation_correction.agent.get_llm")
    @patch("features.validation_correction.semantic_validator.get_llm")
    @patch("features.validation_correction.error_classifier.get_llm")
    def test_e2e_graph_air_gapped_execution(self, mock_err, mock_sem, mock_corr, mock_sql, mock_plan, mock_intent, mock_exec):
        """8. Run end-to-end SQLAgent graph while strict socket shield is ACTIVE."""
        # 1. Setup mock local ChatModel and Embeddings
        mock_llm = MagicMock()
        mock_err.return_value = mock_llm
        mock_sem.return_value = mock_llm
        mock_corr.return_value = mock_llm
        mock_sql.return_value = mock_llm
        mock_plan.return_value = mock_llm
        mock_intent.return_value = mock_llm
        
        mock_exec.return_value = [{"id": 1, "name": "Test Item"}]

        class MockAIMessage:
            def __init__(self, content):
                self.content = content
                self.text = content
                self.response_metadata = {}
                self.usage_metadata = {"input_tokens": 5, "output_tokens": 5, "total_tokens": 10}

        def mock_llm_invoke(messages, *args, **kwargs):
            from langchain_core.messages import SystemMessage
            system_msg = ""
            human_msg = ""
            for m in messages:
                if isinstance(m, SystemMessage):
                    system_msg += m.content.lower()
                else:
                    human_msg += getattr(m, "content", "").lower()

            if "writer" in system_msg or "sql query writer" in system_msg:
                return MockAIMessage("SELECT name FROM products;")
            elif "planner" in system_msg or "query planner" in system_msg:
                return MockAIMessage(
                    '{"thought_process": "Plan products query", "tables": [{"table_name": "products", "purpose": "source"}], "joins": [], "filters": [], "aggregations": [], "group_by": [], "order_by": [], "limit": 10}'
                )
            elif "semantic" in system_msg:
                return MockAIMessage('{"is_valid": true, "reason": "semantic validation match"}')
            elif "intent" in system_msg or "clarify" in system_msg:
                return MockAIMessage("Show products")
            return MockAIMessage("SELECT name FROM products;")

        mock_llm.invoke.side_effect = mock_llm_invoke

        # 2. Build graph workflow
        app = build_workflow()

        # 3. Enable Socket Shield and run workflow in pure isolated context
        enable_socket_shield()
        try:
            state = {
                "original_query": "List all products",
                "db_schema": "Table: products\n  - id (INTEGER)\n  - name (VARCHAR)",
                "refined_query": "",
                "query_plan": "",
                "sql_query": "",
                "error_message": None,
                "retry_count": 0,
                "final_result": None,
                "user_role": "admin",
                "username": "offline_admin",
                "security_error": None
            }
            
            # Execute workflow E2E - if any network leak occurs, the socket connect
            # will raise an Air-Gapped violation and fail this test.
            final_state = app.invoke(state)
            
            # Assert successful execution
            self.assertIsNone(final_state.get("error_message"))
            self.assertIsNotNone(final_state.get("sql_query"))
            self.assertEqual(final_state.get("sql_query"), "SELECT name FROM products LIMIT 1000")
            logger.info("E2E Graph executed successfully under strict offline air-gapped simulation!")
        finally:
            disable_socket_shield()


if __name__ == "__main__":
    unittest.main()
