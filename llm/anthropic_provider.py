"""
Anthropic LLM Provider Implementation

Configures ChatAnthropic and handles fallback embeddings.
"""

import os
import logging
from typing import Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from llm.base import LLMProvider, resolve_callbacks

logger = logging.getLogger("SQLAgent.LLM")


class AnthropicProvider(LLMProvider):
    """
    Concrete provider implementation for Anthropic Claude.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please configure it in your .env file or configuration.")
        self.model = model

    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates ChatAnthropic with registered thread-local callbacks.
        """
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError(
                "langchain-anthropic is not installed. Please install it using:\n"
                "pip install langchain-anthropic"
            )

        callbacks = resolve_callbacks(**kwargs)
        model_name = kwargs.pop("model", self.model)

        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            api_key=self.api_key,
            callbacks=callbacks if callbacks else None,
            **kwargs
        )


    def get_embeddings(self, **kwargs: Any) -> Embeddings:
        """
        Anthropic does not offer a native text embeddings API in LangChain.
        We fall back to Gemini or OpenAI embeddings depending on available keys.
        """
        logger.warning(
            "Anthropic does not offer a native embeddings model. "
            "Attempting fallback to Gemini or OpenAI embeddings."
        )

        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                logger.info("Using Google Gemini embeddings as fallback.")
                return GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-2",
                    google_api_key=google_key,
                    **kwargs
                )
            except Exception as e:
                logger.warning(f"Failed to load Google Generative AI embeddings fallback: {e}")

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from langchain_openai import OpenAIEmbeddings
                logger.info("Using OpenAI embeddings as fallback.")
                return OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=openai_key,
                    **kwargs
                )
            except Exception as e:
                logger.warning(f"Failed to load OpenAI embeddings fallback: {e}")

        raise ValueError(
            "Anthropic does not support native embeddings and no Google API key or OpenAI API key was found "
            "for fallback embeddings. Please configure a valid API key for one of these fallback providers."
        )
