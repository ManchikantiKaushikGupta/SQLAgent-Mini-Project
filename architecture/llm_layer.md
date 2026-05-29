# Provider-Agnostic LLM Layer Architecture

This document describes the design and components of the **Provider-Agnostic LLM Layer** introduced in SQLAgent.

## 1. Design Philosophy
The system is built to support different LLM model providers seamlessly at runtime without duplicating or changing reasoning agent logic. This ensures SQLAgent can be deployed in diverse environments:
- **Cloud-hosted development**: Google Gemini, OpenAI ChatGPT, Anthropic Claude.
- **Self-hosted private servers**: Local Ollama instances, high-throughput enterprise vLLM clusters.

## 2. Directory Layout
All LLM-related providers and factory components are encapsulated under the `llm/` directory at the project root:

```text
llm/
├── base.py                 # Abstract LLMProvider interface and shared retries
├── gemini_provider.py      # Google Gemini provider (ChatGoogleGenerativeAI)
├── openai_provider.py      # OpenAI provider (ChatOpenAI)
├── anthropic_provider.py   # Anthropic provider (ChatAnthropic)
├── ollama_provider.py      # Ollama local provider (ChatOllama)
├── vllm_provider.py        # vLLM OpenAI-compatible provider (ChatOpenAI)
└── factory.py              # LLMProviderFactory and configuration loader
```

## 3. Core Components

### Abstract Provider (`llm/base.py`)
Defines the `LLMProvider` contract:
- `get_chat_model(temperature, **kwargs) -> BaseChatModel`
- `get_embeddings(**kwargs) -> Embeddings`

Also implements `apply_shared_retry(model, max_retries)`, wrapping chat model instances in standard LangChain exponential backoff retry wrappers for resilience.

### Configuration (`llm_config.yaml`)
A single, human-readable configuration file that governs model selection at runtime:
```yaml
provider: gemini
temperature: 0.0

gemini:
  model: gemini-2.5-flash
openai:
  model: gpt-4o
```
If `llm_config.yaml` is absent, the system falls back to environment variables (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_TEMPERATURE`).

### Factory (`llm/factory.py`)
Dynamically parses `llm_config.yaml` on each invocation, allowing **live model switching** without application restarts.

### Embedding Decoupling (`retrieval/schema_retriever.py`)
The vector-store schema retriever fetches its active embeddings model directly via `get_provider().get_embeddings()`. If `anthropic` is selected (which doesn't have a native LangChain embeddings model), it automatically falls back to `gemini` or `openai` depending on which API credentials are set in `.env`.

### Token Accounting & Observability (`core/llm.py`)
Maintains perfect compatibility with the thread-local token tracker (`TokenAccumulatorCallback`). Each concrete provider merges active thread-local callbacks dynamically during instantiation, ensuring that latency, token metrics, and execution steps are tracked flawlessly across OpenAI, Anthropic, Gemini, Ollama, and vLLM.
