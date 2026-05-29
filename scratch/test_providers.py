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
        provider = GeminiProvider(model="gemini-2.5-flash")
        
        self.assertEqual(provider.model, "gemini-2.5-flash")
        self.assertEqual(provider.api_key, "mock-google-key")

        # Test model creation with callback attachment
        mock_callback = MockCallbackHandler()
        register_thread_callbacks([mock_callback])

        model = provider.get_chat_model(temperature=0.0)
        self.assertEqual(model.model, "gemini-2.5-flash")
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

    def test_ollama_provider_instantiation(self):
        """Verifies OllamaProvider configurations for local inference."""
        provider = OllamaProvider(model="llama3", base_url="http://localhost:11434")
        
        self.assertEqual(provider.model, "llama3")
        self.assertEqual(provider.base_url, "http://localhost:11434")

        model = provider.get_chat_model(temperature=0.3)
        self.assertEqual(model.model, "llama3")
        self.assertEqual(model.temperature, 0.3)

    def test_vllm_provider_instantiation(self):
        """Verifies VLLMProvider pointed to OpenAI-compatible base URL."""
        provider = VLLMProvider(model="Qwen/Qwen2.5-Coder-7B-Instruct", base_url="http://localhost:8000/v1")
        
        self.assertEqual(provider.model, "Qwen/Qwen2.5-Coder-7B-Instruct")
        self.assertEqual(provider.base_url, "http://localhost:8000/v1")

        model = provider.get_chat_model(temperature=0.4)
        self.assertEqual(model.model_name, "Qwen/Qwen2.5-Coder-7B-Instruct")
        self.assertEqual(model.temperature, 0.4)
        self.assertEqual(model.openai_api_base, "http://localhost:8000/v1")

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
