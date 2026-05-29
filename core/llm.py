import os
import threading
from typing import List, Optional, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.callbacks import BaseCallbackHandler
from dotenv import load_dotenv

load_dotenv(override=True)

# Thread-local storage for callbacks
_thread_locals = threading.local()

def get_active_callbacks() -> List[BaseCallbackHandler]:
    """Returns the list of active callbacks for the current thread."""
    if not hasattr(_thread_locals, "callbacks"):
        _thread_locals.callbacks = []
    return _thread_locals.callbacks

def register_thread_callbacks(callbacks: List[BaseCallbackHandler]):
    """Registers callbacks for the current thread."""
    _thread_locals.callbacks = callbacks

def clear_thread_callbacks():
    """Clears callbacks for the current thread."""
    if hasattr(_thread_locals, "callbacks"):
        _thread_locals.callbacks = []

# Retained for absolute backward compatibility
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def get_llm(model: Optional[str] = None, temperature: float = 0.0) -> BaseChatModel:
    """
    Returns a configured LangChain ChatModel instance from the active provider.

    Args:
        model: Optional model name to override the default.
        temperature: Sampling temperature. 0.0 for deterministic outputs.

    Returns:
        A ready-to-use LangChain BaseChatModel instance.
    """
    from llm.factory import get_provider
    from llm.base import apply_shared_retry

    provider = get_provider()
    
    kwargs = {}
    # Only pass model override if explicitly provided (and not DEFAULT_MODEL default check)
    if model and model != DEFAULT_MODEL:
        kwargs["model"] = model

    chat_model = provider.get_chat_model(temperature=temperature, **kwargs)
    
    # Apply standard exponential backoff retries to all providers
    return apply_shared_retry(chat_model)


def extract_text(response: Any) -> str:
    """
    Safely extracts string content from an LLM response or AIMessage.
    Handles standard string payloads and complex multi-part dictionary/list payloads.
    """
    if hasattr(response, "text") and response.text:
        return response.text.strip()
        
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
        
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        return "".join(text_parts).strip()
        
    return str(content).strip()
