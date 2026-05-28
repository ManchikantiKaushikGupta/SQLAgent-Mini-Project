import os
import threading
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
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

# Allow model to be overridden via environment variable
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def get_llm(model: str = DEFAULT_MODEL, temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """
    Returns a configured ChatGoogleGenerativeAI instance.

    Args:
        model: The Gemini model to use. Defaults to the GEMINI_MODEL env var,
               falling back to 'gemini-2.5-flash'.
        temperature: Sampling temperature. 0.0 for deterministic outputs.

    Returns:
        A ready-to-use LangChain LLM instance.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

    active_callbacks = get_active_callbacks()

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key,
        callbacks=active_callbacks if active_callbacks else None,
    )
