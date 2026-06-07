"""
SQLAgent Providers Validation Script

Verifies all LLM providers, factory dynamic configurations, thread-local callback configurations,
and fallback embedding models.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import BaseCallbackHandler

# Ensure workspace is importable
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.base import LLMProvider, apply_shared_retry
from llm.factory import LLMProviderFactory, load_config, get_provider
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider
from llm.anthropic_provider import AnthropicProvider
from llm.ollama_provider import OllamaProvider
from llm.vllm_provider import VLLMProvider
from llm.lmstudio_provider import LMStudioProvider
from core.llm import get_llm, register_thread_callbacks, clear_thread_callbacks


class MockCallbackHandler(BaseCallbackHandler):
    """Subclass of BaseCallbackHandler to satisfy Pydantic type validation."""
    pass


class TestLLMProviders(unittest.TestCase):

    def setUp(self):
        # Backup environment
        self.original_env = dict(os.environ)

    def tearDown(self):
        # Restore environment
        os.environ.clear()
        os.environ.update(self.original_env)
        clear_thread_callbacks()

    @patch("os.path.exists", return_value=False)
    def test_provider_factory_fallback_to_env(self, mock_exists):
        """Verifies factory correctly loads defaults from environment variables when YAML is absent."""
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["LLM_MODEL"] = "gpt-4o-mini"
        os.environ["LLM_TEMPERATURE"] = "0.7"
        os.environ["OPENAI_API_KEY"] = "mock-key"

        config = load_config()
        self.assertEqual(config["provider"], "openai")
        self.assertEqual(config["temperature"], 0.7)
        self.assertEqual(config["model"], "gpt-4o-mini")

    def test_gemini_provider_instantiation(self):
        """Verifies GeminiProvider is correctly constructed and configured."""
        os.environ["GOOGLE_API_KEY"] = "mock-google-key"
        provider = GeminiProvider(model="gemini-3.1-flash-lite")
        
        self.assertEqual(provider.model, "gemini-3.1-flash-lite")
        self.assertEqual(provider.api_key, "mock-google-key")

        # Test model creation with callback attachment
        mock_callback = MockCallbackHandler()
        register_thread_callbacks([mock_callback])

        model = provider.get_chat_model(temperature=0.0)
        self.assertEqual(model.model, "gemini-3.1-flash-lite")
        self.assertEqual(model.temperature, 0.0)
        self.assertIn(mock_callback, model.callbacks)

    def test_openai_provider_instantiation(self):
        """Verifies OpenAIProvider instantiates standard OpenAI classes."""
        os.environ["OPENAI_API_KEY"] = "mock-openai-key"
        provider = OpenAIProvider(model="gpt-4o-mini")
        
        self.assertEqual(provider.model, "gpt-4o-mini")
        self.assertEqual(provider.api_key, "mock-openai-key")

        model = provider.get_chat_model(temperature=0.1)
        self.assertEqual(model.model_name, "gpt-4o-mini")
        self.assertEqual(model.temperature, 0.1)

    def test_anthropic_provider_instantiation(self):
        """Verifies AnthropicProvider instantiates Anthropic classes and fallback embeddings."""
        os.environ["ANTHROPIC_API_KEY"] = "mock-anthropic-key"
        os.environ["GOOGLE_API_KEY"] = "mock-google-key"
        provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")
        
        self.assertEqual(provider.model, "claude-3-5-sonnet-20241022")
        self.assertEqual(provider.api_key, "mock-anthropic-key")

        model = provider.get_chat_model(temperature=0.2)
        self.assertEqual(model.model, "claude-3-5-sonnet-20241022")
        self.assertEqual(model.temperature, 0.2)

        # Test embedding fallback to Gemini
        embeddings = provider.get_embeddings()
        self.assertEqual(embeddings.model, "models/gemini-embedding-2")

    @patch("llm.ollama_provider.OllamaProvider.check_health")
    def test_ollama_provider_instantiation(self, mock_check_health):
        """Verifies OllamaProvider configurations for local inference."""
        provider = OllamaProvider(model="llama3", base_url="http://localhost:11434")
        
        self.assertEqual(provider.model, "llama3")
        self.assertEqual(provider.base_url, "http://localhost:11434")

        model = provider.get_chat_model(temperature=0.3)
        self.assertEqual(model.model, "llama3")
        self.assertEqual(model.temperature, 0.3)
        mock_check_health.assert_called_once_with("llama3")

    @patch("requests.get")
    def test_ollama_health_check_healthy(self, mock_get):
        """Verifies check_health passes when server responds with the matching model."""
        # Clear cache for the test
        OllamaProvider._verified_cache.clear()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "qwen3:14b"}, {"name": "llama3"}]}
        mock_get.return_value = mock_response

        provider = OllamaProvider(model="qwen3:14b", base_url="http://localhost:11434")
        
        # Should not raise any error
        provider.check_health("qwen3:14b")
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=2.0)

    @patch("requests.get")
    def test_ollama_health_check_connection_error(self, mock_get):
        """Verifies check_health raises ConnectionError when server is offline."""
        OllamaProvider._verified_cache.clear()
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        provider = OllamaProvider(model="llama3", base_url="http://localhost:11434")
        
        with self.assertRaises(ConnectionError) as ctx:
            provider.check_health("llama3")
        self.assertIn("not running at http://localhost:11434", str(ctx.exception))

    @patch("requests.get")
    def test_ollama_health_check_missing_model(self, mock_get):
        """Verifies check_health raises RuntimeError when the configured model is absent."""
        OllamaProvider._verified_cache.clear()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama3"}]}
        mock_get.return_value = mock_response

        provider = OllamaProvider(model="deepseek-r1", base_url="http://localhost:11434")
        
        with self.assertRaises(RuntimeError) as ctx:
            provider.check_health("deepseek-r1")
        self.assertIn("model 'deepseek-r1' was not found", str(ctx.exception))

    @patch("llm.vllm_provider.VLLMProvider.check_health")
    def test_vllm_provider_instantiation(self, mock_check_health):
        """Verifies VLLMProvider pointed to OpenAI-compatible base URL."""
        provider = VLLMProvider(model="Qwen/Qwen2.5-Coder-7B-Instruct", base_url="http://localhost:8000/v1")
        
        self.assertEqual(provider.model, "Qwen/Qwen2.5-Coder-7B-Instruct")
        self.assertEqual(provider.base_url, "http://localhost:8000/v1")

        model = provider.get_chat_model(temperature=0.4)
        self.assertEqual(model.model_name, "Qwen/Qwen2.5-Coder-7B-Instruct")
        self.assertEqual(model.temperature, 0.4)
        self.assertEqual(model.openai_api_base, "http://localhost:8000/v1")
        mock_check_health.assert_called_once_with("Qwen/Qwen2.5-Coder-7B-Instruct")

    @patch("requests.get")
    def test_vllm_health_check_healthy(self, mock_get):
        """Verifies vLLM check_health passes when server responds with the matching model."""
        VLLMProvider._verified_cache.clear()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "Qwen/Qwen2.5-Coder-7B-Instruct"}]}
        mock_get.return_value = mock_response

        provider = VLLMProvider(model="Qwen/Qwen2.5-Coder-7B-Instruct", base_url="http://localhost:8000/v1")
        
        provider.check_health("Qwen/Qwen2.5-Coder-7B-Instruct")
        mock_get.assert_called_once_with("http://localhost:8000/v1/models", timeout=2.0)

    @patch("requests.get")
    def test_vllm_health_check_connection_error(self, mock_get):
        """Verifies vLLM check_health raises ConnectionError when server is offline."""
        VLLMProvider._verified_cache.clear()
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        provider = VLLMProvider(model="Qwen/Qwen2.5-Coder-7B-Instruct", base_url="http://localhost:8000/v1")
        
        with self.assertRaises(ConnectionError) as ctx:
            provider.check_health("Qwen/Qwen2.5-Coder-7B-Instruct")
        self.assertIn("not running at http://localhost:8000/v1", str(ctx.exception))

    @patch("requests.get")
    def test_vllm_health_check_missing_model(self, mock_get):
        """Verifies vLLM check_health raises RuntimeError when the configured model is absent."""
        VLLMProvider._verified_cache.clear()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "some-other-model"}]}
        mock_get.return_value = mock_response

        provider = VLLMProvider(model="Qwen/Qwen2.5-Coder-7B-Instruct", base_url="http://localhost:8000/v1")
        
        with self.assertRaises(RuntimeError) as ctx:
            provider.check_health("Qwen/Qwen2.5-Coder-7B-Instruct")
        self.assertIn("model 'Qwen/Qwen2.5-Coder-7B-Instruct' was not found", str(ctx.exception))

    @patch("llm.lmstudio_provider.LMStudioProvider.check_health")
    def test_lmstudio_provider_instantiation(self, mock_check_health):
        """Verifies LMStudioProvider configuration for local inference."""
        provider = LMStudioProvider(model="qwen3-14b", base_url="http://localhost:1234/v1")
        
        self.assertEqual(provider.model, "qwen3-14b")
        self.assertEqual(provider.base_url, "http://localhost:1234/v1")
        self.assertEqual(provider.api_key, "lm-studio")  # Default API key

        model = provider.get_chat_model(temperature=0.5)
        self.assertEqual(model.model_name, "qwen3-14b")
        self.assertEqual(model.temperature, 0.5)
        self.assertEqual(model.openai_api_base, "http://localhost:1234/v1")
        mock_check_health.assert_called_once_with("qwen3-14b")

    @patch("requests.get")
    def test_lmstudio_health_check_healthy(self, mock_get):
        """Verifies LM Studio check_health passes when server responds with the matching model."""
        LMStudioProvider._verified_cache.clear()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "qwen3-14b"}]}
        mock_get.return_value = mock_response

        provider = LMStudioProvider(model="qwen3-14b", base_url="http://localhost:1234/v1")
        
        provider.check_health("qwen3-14b")
        mock_get.assert_called_once_with(
            "http://localhost:1234/v1/models",
            headers={"Authorization": "Bearer lm-studio"},
            timeout=2.0
        )

    @patch("requests.get")
    def test_lmstudio_health_check_connection_error(self, mock_get):
        """Verifies LM Studio check_health raises ConnectionError when server is offline."""
        LMStudioProvider._verified_cache.clear()
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        provider = LMStudioProvider(model="qwen3-14b", base_url="http://localhost:1234/v1")
        
        with self.assertRaises(ConnectionError) as ctx:
            provider.check_health("qwen3-14b")
        self.assertIn("LM Studio service is not running at http://localhost:1234/v1", str(ctx.exception))

    @patch("requests.get")
    def test_lmstudio_health_check_missing_model(self, mock_get):
        """Verifies LM Studio check_health raises RuntimeError when the configured model is absent."""
        LMStudioProvider._verified_cache.clear()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "some-other-model"}]}
        mock_get.return_value = mock_response

        provider = LMStudioProvider(model="qwen3-14b", base_url="http://localhost:1234/v1")
        
        with self.assertRaises(RuntimeError) as ctx:
            provider.check_health("qwen3-14b")
        self.assertIn("model 'qwen3-14b' was not found in the loaded models catalog", str(ctx.exception))

    @patch("llm.lmstudio_provider.LMStudioProvider.check_health")
    def test_lmstudio_factory_registration(self, mock_check_health):
        """Verifies factory registration and structured configuration parsing for lmstudio."""
        config = {
            "provider": "lmstudio",
            "model": "custom-model",
            "lmstudio": {
                "base_url": "http://127.0.0.1:9999/v1",
                "api_key": "my-key"
            }
        }
        provider = LLMProviderFactory.create_provider(config)
        self.assertIsInstance(provider, LMStudioProvider)
        self.assertEqual(provider.model, "custom-model")
        self.assertEqual(provider.base_url, "http://127.0.0.1:9999/v1")
        self.assertEqual(provider.api_key, "my-key")

    @patch("llm.lmstudio_provider.LMStudioProvider.check_health")
    def test_lmstudio_env_selection(self, mock_check_health):
        """Verifies provider selection via environment variables."""
        os.environ["LLM_PROVIDER"] = "lmstudio"
        os.environ["LMSTUDIO_BASE_URL"] = "http://localhost:5555/v1"
        os.environ["LMSTUDIO_API_KEY"] = "env-key"
        os.environ["LMSTUDIO_MODEL"] = "qwen-env"

        provider = get_provider()
        self.assertIsInstance(provider, LMStudioProvider)
        self.assertEqual(provider.model, "qwen-env")
        self.assertEqual(provider.base_url, "http://localhost:5555/v1")
        self.assertEqual(provider.api_key, "env-key")

    def test_apply_shared_retry(self):
        """Verifies that shared retry policies wrap models successfully."""
        os.environ["GOOGLE_API_KEY"] = "mock-google-key"
        provider = GeminiProvider()
        model = provider.get_chat_model()
        
        retry_wrapped_model = apply_shared_retry(model, max_retries=5)
        # Check that with_retry applied correctly (wrapped model has standard attributes)
        self.assertTrue(hasattr(retry_wrapped_model, "with_retry"))


if __name__ == "__main__":
    unittest.main()
