"""
Air-Gapped Deployment Mode Validation Engine

Validates the offline integrity of the SQLAgent system, blocking all external
cloud provider routing and running proactive startup health checks against
local model endpoints (Ollama/vLLM) to verify offline readiness.
"""

import os
import logging
from typing import Dict, Any

from llm.factory import load_config, get_provider
from llm.ollama_provider import OllamaProvider
from llm.vllm_provider import VLLMProvider

logger = logging.getLogger("SQLAgent.AirGap")
logger.setLevel(logging.INFO)


def is_air_gap_enabled() -> bool:
    """
    Checks if Air-Gapped Deployment Mode is enabled via environment variables
    or top-level llm_config.yaml settings.

    Returns:
        True if air-gapped mode is enabled, False otherwise.
    """
    # 1. Environment Variable check (highest priority)
    env_air_gap = os.getenv("AIR_GAPPED")
    if env_air_gap is not None:
        return env_air_gap.lower() in ("true", "1", "yes")

    # 2. Config YAML check
    try:
        config = load_config()
        return config.get("air_gapped", False)
    except Exception as e:
        logger.debug(f"Failed to read air_gapped flag from config: {e}")
        return False


def validate_air_gap_environment() -> None:
    """
    Validates that the current environment complies with Air-Gapped Deployment Mode.

    Checks:
    1. Provider is strictly local (ollama or vllm).
    2. Cloud provider API keys are warned/ignored.
    3. Selected local endpoints (Ollama or vLLM hosts) are active and reachable.
    4. Required local Chat and Embedding models are fully loaded/pulled.

    Raises:
        ValueError: If a cloud provider is active.
        ConnectionError: If local LLM endpoints are unreachable.
        RuntimeError: If local LLM models are not loaded.
    """
    if not is_air_gap_enabled():
        return

    logger.info("Initializing Air-Gapped Environment Verification...")

    # Load configuration
    config = load_config()
    provider_name = config.get("provider", "gemini").lower()

    # 1. Reject cloud providers immediately
    if provider_name in ("gemini", "openai", "anthropic"):
        raise ValueError(
            f"Violation of Air-Gapped deployment constraints! "
            f"Active provider is set to cloud-hosted '{provider_name}'. "
            f"In Air-Gapped mode, only local/self-hosted providers ('ollama', 'vllm') are allowed."
        )

    # 2. Check and warn about cloud API keys in the environment
    cloud_keys = ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    present_keys = [k for k in cloud_keys if os.getenv(k)]
    if present_keys:
        logger.warning(
            f"Air-Gapped warning: Cloud API keys are present in the environment: {present_keys}. "
            f"These keys will be strictly ignored to prevent unintended cloud leakage."
        )

    # 3. Instantiate local provider and execute health checks
    logger.info(f"Validating local provider '{provider_name}'...")
    provider = get_provider()

    if isinstance(provider, OllamaProvider):
        # Validate Ollama service and chat model
        logger.info(f"Checking Ollama chat model: '{provider.model}' at {provider.base_url}")
        provider.check_health(provider.model)
        
        # Validate Ollama embeddings model
        embeddings_model = provider.embeddings_model or provider.model
        logger.info(f"Checking Ollama embeddings model: '{embeddings_model}' at {provider.base_url}")
        provider.check_health(embeddings_model)

    elif isinstance(provider, VLLMProvider):
        # Validate vLLM service and chat model
        logger.info(f"Checking vLLM chat model: '{provider.model}' at {provider.base_url}")
        provider.check_health(provider.model)
        
        # Validate vLLM embeddings model if present
        if provider.embeddings_model:
            logger.info(f"Checking vLLM embeddings model: '{provider.embeddings_model}' at {provider.base_url}")
            provider.check_health(provider.embeddings_model)
    else:
        raise ValueError(
            f"Unknown or unsupported local LLM provider '{type(provider).__name__}' "
            f"loaded during air-gapped verification."
        )

    logger.info("Air-Gapped Environment Verification PASSED! System is 100% offline-ready.")
