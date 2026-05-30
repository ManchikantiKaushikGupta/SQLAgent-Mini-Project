# SQLAgent: Enterprise Air-Gapped Deployment Workflow

This guide details the architecture, configuration, and step-by-step procedures for deploying the SQLAgent NL2SQL orchestration framework in highly secure, fully isolated **Air-Gapped environments**.

Air-gapped deployment guarantees that **zero outbound data or metadata** leaks from your database environment. All model inferences, embeddings, and query analysis nodes are executed 100% inside your organization's self-hosted boundaries.

---

## 1. Architectural Overview

In an Air-Gapped Deployment, all external API services (such as Google Gemini, OpenAI, or Anthropic Claude) are completely blocked. Instead, SQLAgent interacts with self-hosted instances of **Ollama** or **vLLM** hosted on local GPUs.

```mermaid
graph TD
    User([User Request]) --> IC[Intent Clarifier]
    IC --> QP[Query Planner]
    QP --> SG[SQL Generator]
    SG --> SV[Semantic Validator]
    SV --> CL[Correction Loop]
    
    subgraph Enterprise Secure Boundary (Local VPC)
        IC & QP & SG & SV & CL --> |Local Inference| LLM_Host{Local Model Server}
        LLM_Host -->|Ollama / vLLM API| Local_GPU[On-Prem GPU Cluster]
        
        SR[Schema Retriever] -->|Offline Search| FAISS[(FAISS Index Cache)]
        SR -.->|No Internet API| Embed_Host[Local Embeddings]
    end
    
    subgraph Network Shield (Blocked)
        Cloud_API[Google / OpenAI / Anthropic APIs] x.-> |Strict Socket Rejections| Network_Boundary((Blocked Outgoing))
    end
```

### Core Integrity Guarantees:
* **Zero External Calls**: Overridden socket connection methods intercept and reject any non-loopback or non-subnet routing attempts immediately.
* **Metadata Protection**: Database schemas reflected via SQLAlchemy are strictly compiled and indexed inside local FAISS caches (`retrieval/index_cache/`).
* **Cloud API Disablement**: Any attempt to load cloud providers throws a fatal error at startup.

---

## 2. Step 1: Pre-downloading Model Weights & Software

Before moving into the air-gapped system, download all required models and dependencies on an internet-connected staging machine.

### A. Ollama Model Downloads
Pull the recommended high-performance chat reasoning models and embeddings model:
```bash
# Pull General / Coding Reasoning Chat Model (Recommended: Qwen 2.5 Coder 14B or Qwen 3 14B)
ollama pull qwen3:14b

# Pull Local Embeddings Model
ollama pull nomic-embed-text
```

### B. Hugging Face Models for vLLM
If deploying via **vLLM** on a dedicated enterprise GPU cluster (e.g., A100 or H100), clone the weights from Hugging Face:
```bash
# Create local weights directory
mkdir -p /opt/models/huggingface

# Clone Chat Model weights
git lfs install
git clone https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct /opt/models/huggingface/Qwen2.5-Coder-7B-Instruct

# Clone Embeddings Model weights
git clone https://huggingface.co/BAAI/bge-large-en-v1.5 /opt/models/huggingface/bge-large-en-v1.5
```

### C. System Packaging
Archive the virtual environment and package caches:
```bash
# Package dependency caches
pip wheel -r requirements.txt -w ./wheelhouse
tar -czvf sqlagent-dependencies.tar.gz ./wheelhouse
```

---

## 3. Step 2: On-Premises Local Model Infrastructure

Once inside the air-gapped boundary, extract the models and launch your serving endpoints.

### Option A: Ollama Launch (Workstation / Single Node)
Start the Ollama daemon and verify local status:
```bash
# Start Ollama service
ollama serve

# Verify local models are cached and available
ollama list
```

### Option B: vLLM Cluster Serving (High Availability / Production)
Launch dual vLLM containers pointing to the pre-downloaded local weights:

```bash
# 1. Start the Chat Reasoning model server on GPU 0
docker run -d --gpus '"device=0"' \
  -v /opt/models/huggingface:/models \
  -p 8000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model /models/Qwen2.5-Coder-7B-Instruct \
  --port 8000

# 2. Start the Embeddings model server on GPU 1
docker run -d --gpus '"device=1"' \
  -v /opt/models/huggingface:/models \
  -p 8001:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model /models/bge-large-en-v1.5 \
  --port 8000
```

---

## 4. Step 3: SQLAgent Air-Gapped Configurations

### A. Environment Configuration (`.env`)
Configure the system to block external paths and use local resources:
```ini
# Enforce Air-Gapped Mode
AIR_GAPPED=true

# Database Connection (Local Postgres / SQLite)
DATABASE_URL=postgresql://postgres:localpassword@localhost:5432/enterprise_db

# Audit logs destination
AUDIT_LOG_PATH=observability/audit_log.json
```

### B. Provider Configuration (`llm_config.yaml`)
Toggle `air_gapped: true` and specify your local endpoints and local embedding models:
```yaml
provider: ollama
air_gapped: true
temperature: 0.0

ollama:
  model: qwen3:14b
  embeddings_model: nomic-embed-text
  base_url: http://localhost:11434

vllm:
  model: Qwen/Qwen2.5-Coder-7B-Instruct
  embeddings_model: BAAI/bge-large-en-v1.5
  base_url: http://localhost:8000/v1
```

---

## 5. Step 4: Schema Reflection & Vector Indexing Cache

To run 100% offline schema retrieval, pre-generate the local vector indices. The indices will be saved as compact flat binary files (`.bin` and `.json`) under `retrieval/index_cache/` so they require zero runtime API expenses or external loads.

```bash
# Run SQLAgent schema building to reflect database structures offline
.venv\Scripts\python -c "from retrieval.schema_retriever import SchemaRetriever; SchemaRetriever().build_and_cache()"
```
This generates:
* `retrieval/index_cache/table_index.bin` (FAISS indexing binary)
* `retrieval/index_cache/metadata.json` (Table/column database relationships)
* `retrieval/index_cache/column_embeddings.json` (Precomputed column description vectors)

---

## 6. Step 5: Startup Verification and Fail-Fast Guards

Before opening the user application, run the automated verification script. It will test local port bindings, check if the models are loaded correctly, mock network connections, and simulate isolated graph executions.

```bash
# Execute the offline integrity tests
.venv\Scripts\python scratch/verify_offline.py
```

Expected output:
```text
INFO:SQLAgent.AirGap:Initializing Air-Gapped Environment Verification...
INFO:SQLAgent.AirGap:Validating local provider 'ollama'...
INFO:SQLAgent.AirGap:Checking Ollama chat model: 'qwen3:14b' at http://localhost:11434
INFO:SQLAgent.LLM:Ollama health check passed: server is alive and 'qwen3:14b' is available.
INFO:SQLAgent.AirGap:Checking Ollama embeddings model: 'nomic-embed-text' at http://localhost:11434
INFO:SQLAgent.LLM:Ollama health check passed: server is alive and 'nomic-embed-text' is available.
INFO:SQLAgent.AirGap:Air-Gapped Environment Verification PASSED! System is 100% offline-ready.

Ran 7 tests in 2.279s

OK
```

The FastAPI backend automatically hooks this check onto startup. Launching the backend:
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```
If your local Ollama or vLLM server is unreachable, or if models are missing, the server will **fail immediately** on start, outputting descriptive troubleshooting steps to prevent runtime issues.

---

## 7. Troubleshooting & Recovery

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| `ConnectionError: Ollama service is not running` | The Ollama background service crashed or isn't started. | Run `ollama serve` or check service logs using `systemctl status ollama`. |
| `RuntimeError: Local Ollama model 'qwen3:14b' was not found` | The model was never pulled into Ollama's local catalog. | Verify your model name or pull it manually: `ollama pull qwen3:14b`. |
| `ValueError: Violation of Air-Gapped deployment constraints!` | Cloud provider (e.g. `gemini`) is configured while `AIR_GAPPED=true`. | Update `llm_config.yaml` to change the `provider` to `ollama` or `vllm`. |
| `socket.error: Denied outbound socket connection` | A component tried to route a request to the internet. | The system successfully intercepted a network leak. Check if fallback logic tried to query public embeddings. |
