# LLM Provider Migration Guide

This guide describes how to configure, switch, and migrate between LLM providers in the SQLAgent NL2SQL orchestration framework.

---

## 1. Quick Start (Configuring a Provider)

To select a provider, edit the `llm_config.yaml` file at the root of the project.

### Google Gemini (Default)
1. Ensure your `.env` contains:
   ```env
   GOOGLE_API_KEY=your-api-key
   ```
2. Set the provider in `llm_config.yaml`:
   ```yaml
   provider: gemini
   ```

### OpenAI
1. Set your OpenAI key in `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   ```
2. Set the provider in `llm_config.yaml`:
   ```yaml
   provider: openai
   ```

### Anthropic Claude
1. Set your Anthropic key in `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   ```
2. Set the provider in `llm_config.yaml`:
   ```yaml
   provider: anthropic
   ```

---

## 2. Setting Up Local / Private Deployment Mode

To perform fully private, offline database indexing and query planning inside your corporate network:

### Ollama (Local LLM)
1. Install Ollama and pull your model:
   ```bash
   ollama pull llama3
   ```
2. Verify Ollama is running locally (usually on port `11434`).
3. Set the provider in `llm_config.yaml`:
   ```yaml
   provider: ollama
   ```
4. Verify that Ollama configurations point to the correct endpoint in `llm_config.yaml`:
   ```yaml
   ollama:
     model: llama3
     base_url: http://localhost:11434
   ```

### vLLM (Enterprise GPU Cluster)
1. Spin up a vLLM server with your selected instruct model:
   ```bash
   python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-Coder-7B-Instruct
   ```
2. Set the provider in `llm_config.yaml`:
   ```yaml
   provider: vllm
   ```
3. Configure the address of your cluster:
   ```yaml
   vllm:
     model: Qwen/Qwen2.5-Coder-7B-Instruct
     base_url: http://localhost:8000/v1
   ```

---

## 3. Developer Notes

- **Zero Agent Code Changes**: All agents retrieve their model instance by calling `from core.llm import get_llm` followed by `llm = get_llm()`. Agent code never needs modification when switching models.
- **Shared Observability & Retries**: All models are automatically configured with thread-local callback telemetry and exponential backoff retry wrappers under the hood.
- **Dynamic Live Switches**: Configuration updates in `llm_config.yaml` are loaded dynamically per call. You can change providers on the fly without restarting the FastAPI backend or web server.
