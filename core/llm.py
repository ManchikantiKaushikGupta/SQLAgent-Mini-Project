import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def get_llm(model: str = "gemini-2.0-flash", temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """
    Returns a configured ChatGoogleGenerativeAI instance.

    Args:
        model: The Gemini model to use. Defaults to 'gemini-2.0-flash'.
        temperature: Sampling temperature. 0.0 for deterministic outputs.

    Returns:
        A ready-to-use LangChain LLM instance.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key,
    )
