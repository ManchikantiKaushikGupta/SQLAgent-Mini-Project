"""
Ollama LLM Provider Implementation

Configures ChatOllama and OllamaEmbeddings for local model inference.
"""

import os
from typing import Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Concrete provider implementation for Ollama local models.
    """

    def __init__(self, model: str = "llama3", base_url: Optional[str] = None):
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatOllama with registered thread-local callbacks.
        Supports both modern langchain-ollama and legacy community packages.
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

        from core.llm import get_active_callbacks

        active_callbacks = get_active_callbacks()
        callbacks = kwargs.pop("callbacks", [])
        if active_callbacks:
            callbacks.extend(active_callbacks)

        model_name = kwargs.pop("model", self.model)

        return ChatOllama(
            model=model_name,
            temperature=temperature,
            base_url=self.base_url,
            callbacks=callbacks if callbacks else None,
            **kwargs
        )

    def get_embeddings(self, **kwargs: Any) -> Embeddings:
        """
        Instantiates OllamaEmbeddings.
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
        return OllamaEmbeddings(
            model=model_name,
            base_url=self.base_url,
            **kwargs
        )
