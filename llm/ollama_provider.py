"""
Ollama LLM Provider Implementation

Configures ChatOllama and OllamaEmbeddings for local model inference.
Includes dynamic connection health checks, pulled model verification,
and lazy outcome caching.
"""

import os
import requests
import logging
from typing import Any, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider

logger = logging.getLogger("SQLAgent.LLM")


class OllamaProvider(LLMProvider):
    """
    Concrete provider implementation for Ollama local models.
    Supports cached connection verification and streaming configurations.
    """

    # Class-level cache to hold health check outcomes: (base_url, model_name) -> True or Exception
    _verified_cache: Dict[tuple[str, str], Any] = {}

    def __init__(self, model: str = "llama3", base_url: Optional[str] = None):
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def check_health(self, model_name: str) -> None:
        """
        Pings the Ollama local endpoint and checks if the configured model is already pulled.
        Caches the health check outcome to ensure subsequent node calls incur zero latency.

        Raises:
            ConnectionError: If the Ollama server is offline.
            RuntimeError: If the server returns errors or the model is not found.
        """
        cache_key = (self.base_url, model_name)
        if cache_key in OllamaProvider._verified_cache:
            status = OllamaProvider._verified_cache[cache_key]
            if status is True:
                return
            else:
                raise status

        logger.info(f"Performing lazy health check for Ollama at {self.base_url} (model: {model_name})...")
        tags_url = f"{self.base_url.rstrip('/')}/api/tags"

        try:
            response = requests.get(tags_url, timeout=2.0)
            if response.status_code != 200:
                err = RuntimeError(
                    f"Ollama server returned an invalid response (HTTP {response.status_code}) "
                    f"at {tags_url}. Please ensure Ollama is running correctly."
                )
                OllamaProvider._verified_cache[cache_key] = err
                raise err

            data = response.json()
            models_list = data.get("models", [])
            pulled_names = {m.get("name") for m in models_list}
            
            # Match exact name or base name (e.g. "qwen3:14b" vs "qwen3:14b-instruct")
            model_found = False
            for pm in pulled_names:
                if pm == model_name or pm.split(":")[0] == model_name or model_name.startswith(pm):
                    model_found = True
                    break

            if not model_found:
                err = RuntimeError(
                    f"Local Ollama model '{model_name}' was not found in the pulled models list. "
                    f"Available pulled models: {list(pulled_names)}. "
                    f"Please run 'ollama pull {model_name}' inside your terminal before executing SQLAgent queries."
                )
                OllamaProvider._verified_cache[cache_key] = err
                raise err

            logger.info(f"Ollama health check passed: server is alive and '{model_name}' is available.")
            OllamaProvider._verified_cache[cache_key] = True

        except requests.exceptions.ConnectionError:
            err = ConnectionError(
                f"Ollama service is not running at {self.base_url}. "
                f"Please start Ollama locally on your machine before running the SQLAgent pipeline."
            )
            OllamaProvider._verified_cache[cache_key] = err
            raise err
        except Exception as e:
            if isinstance(e, (ConnectionError, RuntimeError)):
                raise e
            err = RuntimeError(f"Ollama health check failed due to unexpected error: {e}")
            OllamaProvider._verified_cache[cache_key] = err
            raise err

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatOllama with registered thread-local callbacks and streaming.
        Runs lazy health and model validation checks.
        """
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            try:
                from langchain_community.chat_models import ChatOllama
            except ImportError:
                raise ImportError(
                    "Neither langchain-ollama nor langchain-community is installed. "
                    "Please install langchain-ollama using:\n"
                    "pip install langchain-ollama"
                )

        model_name = kwargs.pop("model", self.model)

        # Run health check to verify endpoint and model presence
        self.check_health(model_name)

        from core.llm import get_active_callbacks

        active_callbacks = get_active_callbacks()
        callbacks = kwargs.pop("callbacks", [])
        if active_callbacks:
            callbacks.extend(active_callbacks)

        # Support streaming parameters
        kwargs.setdefault("streaming", True)

        return ChatOllama(
            model=model_name,
            temperature=temperature,
            base_url=self.base_url,
            callbacks=callbacks if callbacks else None,
            **kwargs
        )

    def get_embeddings(self, **kwargs: Any) -> Embeddings:
        """
        Instantiates OllamaEmbeddings and runs validation checks.
        """
        try:
            from langchain_ollama import OllamaEmbeddings
        except ImportError:
            try:
                from langchain_community.embeddings import OllamaEmbeddings
            except ImportError:
                raise ImportError(
                    "Neither langchain-ollama nor langchain-community is installed. "
                    "Please install langchain-ollama using:\n"
                    "pip install langchain-ollama"
                )

        model_name = kwargs.pop("model", self.model)
        
        # Run health check
        self.check_health(model_name)

        return OllamaEmbeddings(
            model=model_name,
            base_url=self.base_url,
            **kwargs
        )
