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

## 4. Local LLM & Ollama Support (Priority 8)

The system includes specialized support for local private deployments via Ollama, enabling fully private offline database schema retrieval and query planning.

### Models Supported
- **`qwen3:14b`** (Highly performant local NL2SQL model, recommended default)
- **`deepseek-r1`** (Advanced reasoning model executing detailed chain-of-thought plans)
- **`llama3`** (General purpose chat and coding assistant)

### Dynamic Health Checks & Model Verification
To prevent cascading system failures, the `OllamaProvider` executes lazy endpoint and model verification:
1. **Lazy Endpoint Ping**: Pings Ollama tags API `/api/tags` with a 2-second timeout. If the local Ollama server is offline, it halts execution immediately raising a descriptive instruction to start Ollama.
2. **Model Verification**: Validates if the selected local model (e.g. `qwen3:14b`) is present in the local pulled models catalog. If the model is missing, it raises a clean error specifying: `Please run 'ollama pull qwen3:14b' inside your terminal`.
3. **Session Caching**: Health check outcomes (successes or raised exceptions) are cached in-memory per provider base URL and model name. Subsequent agent executions bypass network calls entirely, yielding sub-millisecond execution times.

### Streaming Support
Every chat model instantiated through `OllamaProvider` is configured with `streaming=True` parameters standardly, enabling native token-by-token processing compatible with LangChain's `.stream()` and `.astream()` hooks for modern interactive user interfaces.

## 5. Enterprise vLLM Support (Priority 8 Extension)

The system includes enterprise-grade, high-throughput private local server support via vLLM clusters. It fully implements the `VLLMProvider` interface to leverage OpenAI-compatible APIs deployed in corporate datacenters.

### Key Characteristics

- **OpenAI-Compatible Endpoint Integration**: Seamlessly maps standard endpoints using LangChain's OpenAI interfaces.
- **Dynamic `/v1/models` Checking**: Automatically runs lazy verification against the OpenAI-compatible `/v1/models` endpoint with a 2.0-second timeout to confirm the vLLM server is online and hosting the correct model name (e.g. `Qwen/Qwen2.5-Coder-7B-Instruct`).
- **Descriptive Fallbacks**: If the server is offline or unreachable, the provider interrupts the execution pipeline gracefully, raising actionable terminal setup instructions.
- **Dynamic Session-level Caching**: Employs in-memory caching to guarantee health checks are ran exactly once per runtime process, bypassing subsequent calls to run at sub-millisecond execution times.
- **Observability & Streaming**: Merges thread-local token tracker callbacks dynamically to support real-time token tracking (`TokenAccumulatorCallback`) and enforces standard `streaming=True` configurations.
- **Standardized Retry Wrappers**: Automatically wraps the instantiated vLLM model with exponential-backoff tenacious retries to ensure pipeline resiliency.


