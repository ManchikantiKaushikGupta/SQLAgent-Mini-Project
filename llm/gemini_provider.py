"""
Gemini LLM Provider Implementation

Configures ChatGoogleGenerativeAI and GoogleGenerativeAIEmbeddings.
"""

import os
from typing import Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider, resolve_callbacks


class GeminiProvider(LLMProvider):
    """
    Concrete provider implementation for Google Gemini.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please configure it in your .env file or configuration.")
        self.model = model

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatGoogleGenerativeAI with registered thread-local callbacks.
        """
        callbacks = resolve_callbacks(**kwargs)
        model_name = kwargs.pop("model", self.model)

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=self.api_key,
            callbacks=callbacks if callbacks else None,
            **kwargs
        )


    def get_embeddings(self, **kwargs: Any) -> Embeddings:
        """
        Instantiates GoogleGenerativeAIEmbeddings.
        """
        model_name = kwargs.pop("model", "models/gemini-embedding-2")
        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=self.api_key,
            **kwargs
        )
