"""
LLM Provider Base Interface

Defines the abstract contract for all model providers and implements
shared retry policies and callback configurations.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional
import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

logger = logging.getLogger("SQLAgent.LLM")


class LLMProvider(ABC):
    """
    Abstract interface defining the contract for provider-agnostic model creation.
    Every supported provider must implement get_chat_model and get_embeddings.
    """

    @abstractmethod
    def get_chat_model(self, temperature: float = 0.0, **kwargs: Any) -> BaseChatModel:
        """
        Instantiates and returns a configured LangChain ChatModel.

        Args:
            temperature: Sampling temperature (0.0 for maximum determinism).
            **kwargs: Provider-specific arguments or model overrides.

        Returns:
            A ready-to-use BaseChatModel instance.
        """
        pass

    @abstractmethod
    def get_embeddings(self, **kwargs: Any) -> Embeddings:
        """
        Instantiates and returns a configured LangChain Embeddings model.

        Args:
            **kwargs: Provider-specific arguments or model overrides.

        Returns:
            A ready-to-use Embeddings instance.
        """
        pass


def apply_shared_retry(model: BaseChatModel, max_retries: int = 3) -> BaseChatModel:
    """
    Wraps the ChatModel with a robust, standardized exponential-backoff retry policy
    for resiliency against temporary API failures or rate limits.

    Args:
        model: The base LangChain ChatModel instance.
        max_retries: Maximum number of delivery attempts.

    Returns:
        The wrapped retry-enabled ChatModel instance.
    """
    try:
        if hasattr(model, "with_retry"):
            logger.debug(f"Wrapping ChatModel with standard exponential retry (attempts={max_retries})")
            return model.with_retry(
                stop_after_attempt=max_retries,
                wait_exponential_jitter=True
            )
    except Exception as e:
        logger.warning(f"Failed to apply standard LangChain retry wrapper: {e}. Returning raw model.")
    
    return model
