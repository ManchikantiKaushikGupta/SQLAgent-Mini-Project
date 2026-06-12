"""
LM Studio LLM Provider Implementation

Configures ChatOpenAI and OpenAIEmbeddings pointed to a local LM Studio server.
Includes connection health checks, loaded model verification, and lazy caching.
"""

import os
import requests
import logging
from typing import Any, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider, resolve_callbacks

logger = logging.getLogger("SQLAgent.LLM")


class LMStudioProvider(LLMProvider):
    """
    Concrete provider implementation for LM Studio.
    LM Studio provides an OpenAI-compatible API interface.
    """

    # Class-level cache to hold health check outcomes: (base_url, model_name) -> True or Exception
    _verified_cache: Dict[tuple[str, str], Any] = {}

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "qwen3-14b",
        api_key: Optional[str] = None,
        embeddings_model: Optional[str] = None
    ):
        self.base_url = base_url or os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        self.model = model
        # Default to "lm-studio" as configured/optional API key, check if empty
        self.api_key = api_key if api_key is not None else os.getenv("LMSTUDIO_API_KEY", "lm-studio")
        if self.api_key == "":
            self.api_key = None
        self.embeddings_model = embeddings_model

    def check_health(self, model_name: str) -> None:
        """
        Pings the LM Studio local endpoint and checks if the configured model is loaded.
        Caches the health check outcome to ensure subsequent calls incur zero latency.

        Raises:
            ConnectionError: If the LM Studio server is offline.
            RuntimeError: If the server returns errors or the model is not found.
        """
        cache_key = (self.base_url, model_name)
        if cache_key in LMStudioProvider._verified_cache:
            status = LMStudioProvider._verified_cache[cache_key]
            if status is True:
                return
            else:
                raise status

        logger.info(f"Performing lazy health check for LM Studio at {self.base_url} (model: {model_name})...")
        models_url = f"{self.base_url.rstrip('/')}/models"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.get(models_url, headers=headers, timeout=2.0)
            if response.status_code != 200:
                err = RuntimeError(
                    f"LM Studio server returned an invalid response (HTTP {response.status_code}) "
                    f"at {models_url}. Please ensure LM Studio is running correctly."
                )
                LMStudioProvider._verified_cache[cache_key] = err
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
                    f"Local LM Studio model '{model_name}' was not found in the loaded models catalog. "
                    f"Available loaded models: {list(hosted_names)}. "
                    f"Please verify that your LM Studio server has loaded the correct model."
                )
                LMStudioProvider._verified_cache[cache_key] = err
                raise err

            logger.info(f"LM Studio health check passed: server is alive and '{model_name}' is available.")
            LMStudioProvider._verified_cache[cache_key] = True

        except requests.exceptions.ConnectionError:
            err = ConnectionError(
                f"LM Studio service is not running at {self.base_url}. "
                f"Please start your LM Studio server before running the SQLAgent pipeline."
            )
            LMStudioProvider._verified_cache[cache_key] = err
            raise err
        except Exception as e:
            if isinstance(e, (ConnectionError, RuntimeError)):
                raise e
            err = RuntimeError(f"LM Studio health check failed due to unexpected error: {e}")
            LMStudioProvider._verified_cache[cache_key] = err
            raise err

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatOpenAI pointed to LM Studio's custom base URL.
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
        Instantiates LMStudioEmbeddings pointed to LM Studio's custom base URL and runs validation checks.
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

        class LMStudioEmbeddings(OpenAIEmbeddings):
            """
            Subclass of OpenAIEmbeddings that bypasses tiktoken tokenization,
            sending raw text strings to LM Studio's embeddings endpoint.
            """
            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                response = self.client.create(input=texts, model=self.model)
                return [data.embedding for data in response.data]

            def embed_query(self, text: str) -> list[float]:
                return self.embed_documents([text])[0]

        return LMStudioEmbeddings(
            model=model_name,
            openai_api_base=self.base_url,
            openai_api_key=self.api_key,
            **kwargs
        )
