"""
LLM Configuration and Provider Settings Schemas

Defines Pydantic models for verifying LLM config setups, API details,
and agent model routing overrides.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class LMStudioProviderSettings(BaseModel):
    """Configuration settings specific to LM Studio local server."""
    enabled: bool = Field(True, description="Whether LM Studio is active/enabled.")
    base_url: str = Field("http://localhost:1234/v1", description="OpenAI-compatible local server URL.")
    api_key: Optional[str] = Field("lm-studio", description="Optional API key for request headers.")
    model: str = Field("qwen3-14b", description="Default model loaded on the server.")
    embeddings_model: Optional[str] = Field(None, description="Optional local embedding model name.")

class LLMConfigSettings(BaseModel):
    """Global configuration settings for SQLAgent LLM Layer."""
    provider: str = Field("gemini", description="Active LLM provider (gemini, openai, anthropic, ollama, vllm, lmstudio).")
    air_gapped: bool = Field(False, description="Enforces offline mode, disabling cloud routing.")
    temperature: float = Field(0.0, description="Sampling reasoning temperature.")
    model: Optional[str] = Field(None, description="Global model override name.")
    
    # Model routing settings for reasoning agents
    planner_model: Optional[str] = Field(None, description="Custom model name for Query Planner.")
    generator_model: Optional[str] = Field(None, description="Custom model name for SQL Generator.")
    validator_model: Optional[str] = Field(None, description="Custom model name for Semantic Validator.")
    clarification_model: Optional[str] = Field(None, description="Custom model name for Intent Clarification.")
    classifier_model: Optional[str] = Field(None, description="Custom model name for Error Classifier.")
    repair_model: Optional[str] = Field(None, description="Custom model name for SQL Repair Engine.")

    # Provider specific settings
    lmstudio: Optional[LMStudioProviderSettings] = Field(default_factory=LMStudioProviderSettings)
