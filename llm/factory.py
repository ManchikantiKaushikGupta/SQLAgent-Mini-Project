"""
LLM Provider Factory

Manages runtime config loading from yaml or env variables and returns the
appropriate LLMProvider instance.
"""

import os
import yaml
import logging
from typing import Any, Dict, Optional
from contextvars import ContextVar

from llm.base import LLMProvider
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider
from llm.anthropic_provider import AnthropicProvider
from llm.ollama_provider import OllamaProvider
from llm.vllm_provider import VLLMProvider
from llm.lmstudio_provider import LMStudioProvider

logger = logging.getLogger("SQLAgent.LLM")

# Context variables to support request-scoped provider and model overrides
provider_override: ContextVar[Optional[str]] = ContextVar("provider_override", default=None)
model_override: ContextVar[Optional[str]] = ContextVar("model_override", default=None)



def load_config() -> Dict[str, Any]:
    """
    Loads configuration from 'config/providers.yaml' or 'llm_config.yaml',
    falling back to environment variables.
    """
    config = {}
    
    # 1. Load from config/providers.yaml if it exists
    providers_yaml_path = os.path.join("config", "providers.yaml")
    if os.path.exists(providers_yaml_path):
        try:
            with open(providers_yaml_path, "r") as f:
                yaml_content = yaml.safe_load(f)
                if isinstance(yaml_content, dict):
                    config.update(yaml_content)
                    logger.debug(f"Successfully loaded configuration from {providers_yaml_path}")
        except Exception as e:
            logger.warning(f"Error reading config file {providers_yaml_path}: {e}")

    # 2. Merge/fallback to llm_config.yaml if it exists
    llm_config_path = "llm_config.yaml"
    if os.path.exists(llm_config_path):
        try:
            with open(llm_config_path, "r") as f:
                yaml_content = yaml.safe_load(f)
                if isinstance(yaml_content, dict):
                    # Only insert keys if not already defined (gives providers.yaml precedence)
                    for k, v in yaml_content.items():
                        if k not in config:
                            config[k] = v
                        elif isinstance(v, dict) and isinstance(config[k], dict):
                            # Deep merge one level for provider sub-dictionaries
                            for pk, pv in v.items():
                                if pk not in config[k]:
                                    config[k][pk] = pv
                    logger.debug(f"Successfully merged configuration from {llm_config_path}")
        except Exception as e:
            logger.warning(f"Error reading config file {llm_config_path}: {e}")

    # 3. Apply Environment Variable overrides (highest priority)
    provider = os.getenv("LLM_PROVIDER", config.get("provider", "gemini")).lower()
    model = os.getenv("LLM_MODEL", config.get("model"))
    temperature_str = os.getenv("LLM_TEMPERATURE")
    if temperature_str is not None:
        try:
            temperature = float(temperature_str)
        except ValueError:
            temperature = float(config.get("temperature", 0.0))
    else:
        temperature = float(config.get("temperature", 0.0))

    air_gapped = os.getenv("AIR_GAPPED", "").lower() in ("true", "1", "yes") or config.get("air_gapped", False)

    # If LM Studio specific env variables are present, merge them into config['lmstudio']
    lmstudio_config = config.get("lmstudio", {})
    if not isinstance(lmstudio_config, dict):
        lmstudio_config = {}
    
    lmstudio_enabled = os.getenv("LMSTUDIO_ENABLED")
    if lmstudio_enabled is not None:
        lmstudio_config["enabled"] = lmstudio_enabled.lower() in ("true", "1", "yes")
        # If explicitly enabled via env, and provider is not set in env, we can switch active provider
        if lmstudio_config["enabled"] and not os.getenv("LLM_PROVIDER"):
            provider = "lmstudio"
            
    lmstudio_base_url = os.getenv("LMSTUDIO_BASE_URL")
    if lmstudio_base_url:
        lmstudio_config["base_url"] = lmstudio_base_url
        
    lmstudio_api_key = os.getenv("LMSTUDIO_API_KEY")
    if lmstudio_api_key is not None:
        lmstudio_config["api_key"] = lmstudio_api_key

    lmstudio_model = os.getenv("LMSTUDIO_MODEL")
    if lmstudio_model:
        lmstudio_config["model"] = lmstudio_model
        if provider == "lmstudio" and not model:
            model = lmstudio_model

    config["lmstudio"] = lmstudio_config
    config["provider"] = provider
    config["temperature"] = temperature
    config["air_gapped"] = air_gapped
    if model:
        config["model"] = model

    # Load routing environment variables
    for env_var, config_key in [
        ("PLANNER_MODEL", "planner_model"),
        ("GENERATOR_MODEL", "generator_model"),
        ("VALIDATOR_MODEL", "validator_model"),
        ("CLARIFICATION_MODEL", "clarification_model"),
        ("CLASSIFIER_MODEL", "classifier_model"),
        ("REPAIR_MODEL", "repair_model")
    ]:
        val = os.getenv(env_var)
        if val:
            config[config_key] = val

    # Apply request-scoped context overrides if present
    active_prov = provider_override.get()
    if active_prov:
        config["provider"] = active_prov
        active_mod = model_override.get()
        
        # Determine the target model for this overridden provider
        if active_mod:
            target_model = active_mod
        else:
            provider_specific = config.get(active_prov)
            if isinstance(provider_specific, dict) and "model" in provider_specific:
                target_model = provider_specific["model"]
            else:
                target_model = None
                
        if target_model:
            config["model"] = target_model
            # Force all dynamic routing keys to match the new provider's model to avoid mismatched models
            for key in ["planner_model", "generator_model", "validator_model", "clarification_model", "classifier_model", "repair_model"]:
                config[key] = target_model
        else:
            config.pop("model", None)
            for key in ["planner_model", "generator_model", "validator_model", "clarification_model", "classifier_model", "repair_model"]:
                config.pop(key, None)
    else:
        # If provider is not overridden but model is, set the model globally and for all roles
        active_mod = model_override.get()
        if active_mod:
            config["model"] = active_mod
            for key in ["planner_model", "generator_model", "validator_model", "clarification_model", "classifier_model", "repair_model"]:
                config[key] = active_mod

    # Validate using LLMConfigSettings to ensure everything conforms
    try:
        from schemas.settings import LLMConfigSettings
        validated = LLMConfigSettings(**config)
        # Convert Pydantic object back to dict so callers get standard dict
        return validated.model_dump()
    except Exception as validation_err:
        logger.warning(f"Configuration validation failed: {validation_err}. Returning raw dictionary.")

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
                "In air-gapped mode, only local/self-hosted providers ('ollama', 'vllm', 'lmstudio') are permitted."
            )

        # Extrapolate provider-specific configs if nested in the YAML config
        provider_specific = config.get(provider_name, {})

        if provider_name == "gemini":
            return GeminiProvider(
                api_key=provider_specific.get("api_key"),
                model=model or provider_specific.get("model", os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"))
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
        elif provider_name == "lmstudio":
            return LMStudioProvider(
                base_url=provider_specific.get("base_url"),
                model=model or provider_specific.get("model", "qwen3-14b"),
                api_key=provider_specific.get("api_key"),
                embeddings_model=provider_specific.get("embeddings_model")
            )
        else:
            raise ValueError(
                f"Unsupported LLM provider name: '{provider_name}'. "
                f"Must be one of: gemini, openai, anthropic, ollama, vllm, lmstudio."
            )


def get_provider() -> LLMProvider:
    """
    Convenience function returning the globally configured provider.
    Re-loads config on call to allow live runtime switching.
    """
    return LLMProviderFactory.create_provider()

