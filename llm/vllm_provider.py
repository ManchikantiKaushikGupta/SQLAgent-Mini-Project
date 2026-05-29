"""
vLLM LLM Provider Implementation

Configures ChatOpenAI and OpenAIEmbeddings pointed to a local/private vLLM server.
"""

import os
from typing import Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider


class VLLMProvider(LLMProvider):
    """
    Concrete provider implementation for vLLM servers.
    vLLM provides an OpenAI-compatible API interface.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
        api_key: Optional[str] = None
    ):
        self.base_url = base_url or os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
        self.model = model
        self.api_key = api_key or os.getenv("VLLM_API_KEY", "dummy-key")

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatOpenAI pointed to vLLM's custom base URL.
        """
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain-openai is not installed. Please install it using:\n"
                "pip install langchain-openai"
            )

        from core.llm import get_active_callbacks

        active_callbacks = get_active_callbacks()
        callbacks = kwargs.pop("callbacks", [])
        if active_callbacks:
            callbacks.extend(active_callbacks)

        model_name = kwargs.pop("model", self.model)

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
        Instantiates OpenAIEmbeddings pointed to vLLM's custom base URL.
        """
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-openai is not installed. Please install it using:\n"
                "pip install langchain-openai"
            )

        model_name = kwargs.pop("model", "text-embedding-3-small")
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_base=self.base_url,
            openai_api_key=self.api_key,
            **kwargs
        )
