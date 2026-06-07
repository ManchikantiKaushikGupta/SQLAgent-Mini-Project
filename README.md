# SQLAgent-Mini-Project

A LangGraph-based modular NL2SQL orchestration framework that converts natural language queries into safe, executable SQL queries.

## 🚀 Key Features
- **Dynamic Schema Retrieval**: Dual-layer vector indexing (FAISS) filters relevant tables and columns, preserving key constraints.
- **Dynamic Model Routing**: Intelligently inspects agent stack calls at runtime to load customizable, task-specific models (e.g. planner vs. generator models).
- **Dual-Mode Deployments**: Fully compatible with cloud-hosted models (Gemini, OpenAI, Anthropic) and offline local engines (Ollama, vLLM, LM Studio).
- **Production Governance & Security**: Implements column-level RBAC, automated input PII redaction, SELECT-only safety AST guards, and result-set masking.
- **Observability Dashboard**: Streamlit-based workspace displaying timeline latencies, token consumption, query plans, and correction histories.

## 🛠️ LM Studio Local LLM Setup Guide
To configure SQLAgent to connect to LM Studio for private, offline database execution, follow these steps:

### 1. Launch LM Studio Server
1. Download and open [LM Studio](https://lmstudio.ai/).
2. Pull your chosen instruct models (e.g., `Qwen2.5-Coder-7B-Instruct` or similar).
3. Start the Local Server (standard endpoint: `http://localhost:1234`). Make sure it is hosting your selected model.

### 2. Configure Environment `.env`
Enable the LM Studio provider and set up agent-specific routing configurations in your `.env` file:
```env
# Enable LM Studio Provider
LLM_PROVIDER=lmstudio

# LM Studio API Configuration
LMSTUDIO_ENABLED=true
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_MODEL=qwen3-14b

# Agent-Specific Model Routing Overrides
PLANNER_MODEL=qwen3-14b
GENERATOR_MODEL=qwen3-8b
VALIDATOR_MODEL=qwen3-14b
```

### 3. YAML Configuration (`config/providers.yaml`)
Alternatively, configuration can be managed via the `config/providers.yaml` file:
```yaml
provider: lmstudio
air_gapped: true

planner_model: qwen3-14b
generator_model: qwen3-8b
validator_model: qwen3-14b

lmstudio:
  enabled: true
  base_url: http://localhost:1234/v1
  api_key: lm-studio
  model: qwen3-14b
  embeddings_model: text-embedding-3-small
```

### 4. Run the Application
1. Start the API backend:
   ```bash
   uvicorn api.app:app --reload
   ```
2. Start the Streamlit frontend dashboard:
   ```bash
   streamlit run frontend/app.py
   ```