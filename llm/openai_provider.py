"""
OpenAI LLM Provider Implementation

Configures ChatOpenAI and OpenAIEmbeddings.
"""

import os
from typing import Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider, resolve_callbacks


class OpenAIProvider(LLMProvider):
    """
    Concrete provider implementation for OpenAI.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found. Please configure it in your .env file or configuration.")
        self.model = model

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatOpenAI with registered thread-local callbacks.
        """
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain-openai is not installed. Please install it using:\n"
                "pip install langchain-openai"
            )

        callbacks = resolve_callbacks(**kwargs)
        model_name = kwargs.pop("model", self.model)

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=self.api_key,
            callbacks=callbacks if callbacks else None,
            **kwargs
        )


    def get_embeddings(self, **kwargs: Any) -> Embeddings:
        """
        Instantiates OpenAIEmbeddings.
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
            api_key=self.api_key,
            **kwargs
        )
