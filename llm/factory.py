"""
LLM Provider Factory

Manages runtime config loading from yaml or env variables and returns the
appropriate LLMProvider instance.
"""

import os
import yaml
import logging
from typing import Any, Dict, Optional

from llm.base import LLMProvider
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider
from llm.anthropic_provider import AnthropicProvider
from llm.ollama_provider import OllamaProvider
from llm.vllm_provider import VLLMProvider

logger = logging.getLogger("SQLAgent.LLM")


def load_config() -> Dict[str, Any]:
    """
    Loads configuration from 'llm_config.yaml' at the project root if it exists,
    falling back to environment variables.

    Returns:
        A dictionary containing LLM config parameter mappings.
    """
    config_path = "llm_config.yaml"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if isinstance(config, dict):
                    logger.debug(f"Successfully loaded configuration from {config_path}")
                    return config
        except Exception as e:
            logger.warning(f"Error reading config file {config_path}: {e}. Falling back to env variables.")

    # Fallback to standard environment variables
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model = os.getenv("LLM_MODEL")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    air_gapped = os.getenv("AIR_GAPPED", "false").lower() in ("true", "1", "yes")

    config = {
        "provider": provider,
        "temperature": temperature,
        "air_gapped": air_gapped,
    }
    if model:
        config["model"] = model

    return config


class LLMProviderFactory:
    """
    Factory to construct and configure the globally selected LLMProvider.
    """

    @staticmethod
    def create_provider(config: Optional[Dict[str, Any]] = None) -> LLMProvider:
        """
        Builds the concrete LLMProvider from configuration.

        Args:
            config: Optional config dict. If None, loaded dynamically.

        Returns:
            An configured instance of LLMProvider.
        """
        if config is None:
            config = load_config()

        provider_name = config.get("provider", "gemini").lower()
        model = config.get("model")
        
        # Enforce Air-Gapped checks
        air_gapped = config.get("air_gapped", False)
        if os.getenv("AIR_GAPPED", "").lower() in ("true", "1", "yes"):
            air_gapped = True

        if air_gapped and provider_name in ("gemini", "openai", "anthropic"):
            raise ValueError(
                f"Cannot load cloud LLM provider '{provider_name}' in Air-Gapped Deployment Mode. "
                "In air-gapped mode, only local/self-hosted providers ('ollama', 'vllm') are permitted."
            )

        # Extrapolate provider-specific configs if nested in the YAML config
        provider_specific = config.get(provider_name, {})

        if provider_name == "gemini":
            return GeminiProvider(
                api_key=provider_specific.get("api_key"),
                model=model or provider_specific.get("model", os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
            )
        elif provider_name == "openai":
            return OpenAIProvider(
                api_key=provider_specific.get("api_key"),
                model=model or provider_specific.get("model", "gpt-4o")
            )
        elif provider_name == "anthropic":
            return AnthropicProvider(
                api_key=provider_specific.get("api_key"),
                model=model or provider_specific.get("model", "claude-3-5-sonnet-20241022")
            )
        elif provider_name == "ollama":
            return OllamaProvider(
                model=model or provider_specific.get("model", "llama3"),
                base_url=provider_specific.get("base_url"),
                embeddings_model=provider_specific.get("embeddings_model")
            )
        elif provider_name == "vllm":
            return VLLMProvider(
                base_url=provider_specific.get("base_url"),
                model=model or provider_specific.get("model", "Qwen/Qwen2.5-Coder-7B-Instruct"),
                api_key=provider_specific.get("api_key"),
                embeddings_model=provider_specific.get("embeddings_model")
            )
        else:
            raise ValueError(
                f"Unsupported LLM provider name: '{provider_name}'. "
                f"Must be one of: gemini, openai, anthropic, ollama, vllm."
            )


def get_provider() -> LLMProvider:
    """
    Convenience function returning the globally configured provider.
    Re-loads config on call to allow live runtime switching.
    """
    return LLMProviderFactory.create_provider()
