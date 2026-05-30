"""
vLLM LLM Provider Implementation

Configures ChatOpenAI and OpenAIEmbeddings pointed to a local/private vLLM server.
Includes dynamic connection health checks, hosted model verification,
and lazy outcome caching.
"""

import os
import requests
import logging
from typing import Any, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider, resolve_callbacks

logger = logging.getLogger("SQLAgent.LLM")


class VLLMProvider(LLMProvider):
    """
    Concrete provider implementation for private vLLM servers.
    vLLM provides an OpenAI-compatible API interface.
    """

    # Class-level cache to hold health check outcomes: (base_url, model_name) -> True or Exception
    _verified_cache: Dict[tuple[str, str], Any] = {}

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
        api_key: Optional[str] = None,
        embeddings_model: Optional[str] = None
    ):
        self.base_url = base_url or os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
        self.model = model
        self.api_key = api_key or os.getenv("VLLM_API_KEY", "dummy-key")
        self.embeddings_model = embeddings_model

    def check_health(self, model_name: str) -> None:
        """
        Pings the vLLM local endpoint and checks if the configured model is hosted.
        Caches the health check outcome to ensure subsequent calls incur zero latency.

        Raises:
            ConnectionError: If the vLLM server is offline.
            RuntimeError: If the server returns errors or the model is not found.
        """
        cache_key = (self.base_url, model_name)
        if cache_key in VLLMProvider._verified_cache:
            status = VLLMProvider._verified_cache[cache_key]
            if status is True:
                return
            else:
                raise status

        logger.info(f"Performing lazy health check for vLLM at {self.base_url} (model: {model_name})...")
        models_url = f"{self.base_url.rstrip('/')}/models"

        try:
            response = requests.get(models_url, timeout=2.0)
            if response.status_code != 200:
                err = RuntimeError(
                    f"vLLM server returned an invalid response (HTTP {response.status_code}) "
                    f"at {models_url}. Please ensure vLLM is running correctly."
                )
                VLLMProvider._verified_cache[cache_key] = err
                raise err

            data = response.json()
            models_list = data.get("data", [])
            hosted_names = {m.get("id") for m in models_list}
            
            # Match exact name, final path segment, or generic match
            model_found = False
            for hm in hosted_names:
                if hm == model_name or hm.split("/")[-1] == model_name or model_name.endswith(hm):
                    model_found = True
                    break

            if not model_found:
                err = RuntimeError(
                    f"Local vLLM model '{model_name}' was not found in the hosted models catalog. "
                    f"Available hosted models: {list(hosted_names)}. "
                    f"Please verify that your vLLM server is hosting the correct model."
                )
                VLLMProvider._verified_cache[cache_key] = err
                raise err

            logger.info(f"vLLM health check passed: server is alive and '{model_name}' is available.")
            VLLMProvider._verified_cache[cache_key] = True

        except requests.exceptions.ConnectionError:
            err = ConnectionError(
                f"vLLM service is not running at {self.base_url}. "
                f"Please start your private vLLM endpoint before running the SQLAgent pipeline."
            )
            VLLMProvider._verified_cache[cache_key] = err
            raise err
        except Exception as e:
            if isinstance(e, (ConnectionError, RuntimeError)):
                raise e
            err = RuntimeError(f"vLLM health check failed due to unexpected error: {e}")
            VLLMProvider._verified_cache[cache_key] = err
            raise err

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatOpenAI pointed to vLLM's custom base URL.
        Runs lazy health and model validation checks.
        """
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain-openai is not installed. Please install it using:\n"
                "pip install langchain-openai"
            )

        model_name = kwargs.pop("model", self.model)

        # Run health check to verify endpoint and model presence
        self.check_health(model_name)

        callbacks = resolve_callbacks(**kwargs)

        # Support streaming parameters standardly
        kwargs.setdefault("streaming", True)

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_base=self.base_url,
            openai_api_key=self.api_key,
            callbacks=callbacks if callbacks else None,
            **kwargs
        )

    def get_embeddings(self, **kwargs: Any) -> Embeddings:
        """
        Instantiates OpenAIEmbeddings pointed to vLLM's custom base URL and runs validation checks.
        """
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-openai is not installed. Please install it using:\n"
                "pip install langchain-openai"
            )

        model_name = kwargs.pop("model", self.embeddings_model or "text-embedding-3-small")
        
        # Run health check
        self.check_health(self.model)

        return OpenAIEmbeddings(
            model=model_name,
            openai_api_base=self.base_url,
            openai_api_key=self.api_key,
            **kwargs
        )
