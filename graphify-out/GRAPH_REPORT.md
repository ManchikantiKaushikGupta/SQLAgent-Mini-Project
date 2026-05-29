# Graph Report - SQLAgent-Mini-Project  (2026-05-29)

## Corpus Check
- 61 files · ~119,705 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 588 nodes · 941 edges · 56 communities (49 shown, 7 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f31cbb46`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 48 edges
2. `get_llm()` - 23 edges
3. `init_metrics_state()` - 20 edges
4. `GeminiProvider` - 18 edges
5. `AnthropicProvider` - 17 edges
6. `OllamaProvider` - 17 edges
7. `OpenAIProvider` - 17 edges
8. `VLLMProvider` - 17 edges
9. `TestLLMProviders` - 17 edges
10. `track_latency()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `SQLAgentState` --uses--> `QueryPlan`  [INFERRED]
  core/state.py → schemas/planner.py
- `str` --uses--> `QueryPlan`  [INFERRED]
  features/query_planning/agent.py → schemas/planner.py
- `QueryPlan` --uses--> `QueryPlan`  [INFERRED]
  features/query_planning/agent.py → schemas/planner.py
- `str` --uses--> `QueryPlan`  [INFERRED]
  features/sql_generation/agent.py → schemas/planner.py
- `QueryPlan` --uses--> `QueryPlan`  [INFERRED]
  features/sql_generation/agent.py → schemas/planner.py

## Communities (56 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (40): decide_after_execution(), decide_after_semantic_validation(), decide_after_syntax_validation(), node_clarify_intent(), node_correct_sql(), node_execute_sql(), node_query_planning(), node_retrieve_schema() (+32 more)

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (6): str, TestASTRepairEngine, detect_failing_clause(), Parses the error message string to detect which clause is failing.     Returns:, Surgically repairs a specific failing clause in a SQL query using SQLGlot AST ma, repair_sql_clause()

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (24): ndarray, Retrieval Module Initialization, Any, bool, int, str, FAISS-Based Database Schema Retriever  Dynamically reflects database metadata us, Extracts DB metadata, generates semantic documents, computes embeddings, (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (37): ChatGoogleGenerativeAI, extract_text(), get_llm(), Any, BaseChatModel, float, str, Returns a configured LangChain ChatModel instance from the active provider. (+29 more)

### Community 4 - "Community 4"
Cohesion: 0.36
Nodes (8): Base, Category, Order, OrderItem, Product, Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema, Review, User

### Community 5 - "Community 5"
Cohesion: 0.20
Nodes (9): Architecture Philosophy, Current Architecture, Enterprise Architecture Vision, Final Vision, High Priority Roadmap, Objective, PRIORITY 1 — Structured Outputs, Recommended Future Architecture (+1 more)

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (6): 1. Intent Clarification Agent, 2. Query Planning Agent, 3. SQL Generation Agent, 4. Validation & Correction Agent, Multi-Agent System Design, System Flow

### Community 7 - "Community 7"
Cohesion: 0.36
Nodes (7): int, str, int, extract_offline(), label_communities(), load_detection(), main()

### Community 8 - "Community 8"
Cohesion: 0.22
Nodes (9): Logger, LogRecord, ColoredFormatter, int, str, Observability Structured Logger  Defines a custom structured logging setup that, Custom formatter to inject console colors depending on log levels and names., Sets up a colored structured logger instance.          Args:         name: Name (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (21): 1. Unstructured LLM Outputs, 2. Full SQL Regeneration During Correction, 3. Validation Is Mostly Syntax-Level, 4. No Real Schema Retrieval Layer, 5. Limited Observability, Critical Weaknesses To Address, Current Problem, Current Validation (+13 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (26): bool, str, Any, str, Validation & Correction Pydantic Schemas  Defines structural models for SQL sema, Structured response representing the semantic correctness verification of a gene, Structured response representing the output of the query correction agent., SemanticValidationResult (+18 more)

### Community 24 - "Community 24"
Cohesion: 0.08
Nodes (35): ask_database(), QueryRequest, QueryResponse, FastAPI Routes  Defines endpoints for the SQLAgent application., Takes a natural language query, runs it through the SQLAgent graph,     and retu, BenchmarkResult, BenchmarkSummary, build_workflow() (+27 more)

### Community 28 - "Community 28"
Cohesion: 0.10
Nodes (25): Any, BaseModel, bool, execute_sql_query(), get_db(), str, Database connection and utilities.  Handles PostgreSQL connection setup using SQ, Yields a database session. (+17 more)

### Community 29 - "Community 29"
Cohesion: 0.07
Nodes (26): columns, fk_columns, pk_columns, db_metadata, categories, order_items, orders, products (+18 more)

### Community 31 - "Community 31"
Cohesion: 0.29
Nodes (7): Metrics Tracked, Objective, Objective, PRIORITY 2 — Evaluation Framework [COMPLETED], PRIORITY 3 — Semantic Validation, Status, Status

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (11): Architecture & System Design, Completed, Core Pipeline, Correction Workflow, In Progress, Infrastructure, Optimization, Project Overview (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.33
Nodes (6): Backend, Core, Current Tech Stack, Frontend, LLM Providers, SQL Tooling

### Community 34 - "Community 34"
Cohesion: 0.33
Nodes (6): Deployment Backends, Enterprise Benefit, Objective, PRIORITY 8 — Enterprise Local LLM Support, Requirements, Target Models

### Community 35 - "Community 35"
Cohesion: 0.40
Nodes (6): Objective, Objective, PRIORITY 4 — Clause-Level SQL Repair, PRIORITY 6 — Observability & Transparency [COMPLETED], Status, Status

### Community 36 - "Community 36"
Cohesion: 0.40
Nodes (5): Datasets, Goal, Metrics, Objective, PRIORITY 10 — Benchmark Expansion

### Community 37 - "Community 37"
Cohesion: 0.40
Nodes (5): Objective, PRIORITY 7 — Provider-Agnostic LLM Layer, Required Architecture, Requirements, Success Criteria

### Community 38 - "Community 38"
Cohesion: 0.50
Nodes (4): Error Categories, Goal, Objective, PRIORITY 9 — Formal Error Taxonomy Engine

### Community 39 - "Community 39"
Cohesion: 0.67
Nodes (3): Current Maturity, Current Project Status, Main Focus Going Forward

### Community 40 - "Community 40"
Cohesion: 0.67
Nodes (3): DO, DO NOT, Important Development Rules

### Community 43 - "Community 43"
Cohesion: 0.67
Nodes (3): Features, Objective, PRIORITY 11 — Production Governance & Security

### Community 44 - "Community 44"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 5 — Schema Retrieval Layer [COMPLETED], Status

### Community 45 - "Community 45"
Cohesion: 0.20
Nodes (25): AnthropicProvider, Concrete provider implementation for Anthropic Claude., get_provider(), LLMProviderFactory, load_config(), Any, LLMProvider, str (+17 more)

### Community 46 - "Community 46"
Cohesion: 0.09
Nodes (21): 1. Quick Start (Configuring a Provider), 2. Setting Up Local / Private Deployment Mode, 3. Developer Notes, Anthropic Claude, code:env (GOOGLE_API_KEY=your-api-key), code:bash (python -m vllm.entrypoints.openai.api_server --model Qwen/Qw), code:yaml (provider: vllm), code:yaml (vllm:) (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.12
Nodes (13): Any, BaseChatModel, Embeddings, float, str, Instantiates ChatAnthropic with registered thread-local callbacks., Anthropic does not offer a native text embeddings API in LangChain.         We f, LLMProvider (+5 more)

### Community 48 - "Community 48"
Cohesion: 0.12
Nodes (8): Verifies OllamaProvider configurations for local inference., Verifies VLLMProvider pointed to OpenAI-compatible base URL., Verifies that shared retry policies wrap models successfully., Verifies factory correctly loads defaults from environment variables when YAML i, Verifies GeminiProvider is correctly constructed and configured., Verifies OpenAIProvider instantiates standard OpenAI classes., Verifies AnthropicProvider instantiates Anthropic classes and fallback embedding, TestLLMProviders

### Community 49 - "Community 49"
Cohesion: 0.14
Nodes (11): ABC, apply_shared_retry(), Any, BaseChatModel, Embeddings, float, int, LLM Provider Base Interface  Defines the abstract contract for all model provide (+3 more)

### Community 50 - "Community 50"
Cohesion: 0.15
Nodes (8): get_active_callbacks(), BaseCallbackHandler, Returns the list of active callbacks for the current thread., Anthropic LLM Provider Implementation  Configures ChatAnthropic and handles fall, Gemini LLM Provider Implementation  Configures ChatGoogleGenerativeAI and Google, Ollama LLM Provider Implementation  Configures ChatOllama and OllamaEmbeddings f, OpenAI LLM Provider Implementation  Configures ChatOpenAI and OpenAIEmbeddings., vLLM LLM Provider Implementation  Configures ChatOpenAI and OpenAIEmbeddings poi

### Community 51 - "Community 51"
Cohesion: 0.17
Nodes (11): 1. Design Philosophy, 2. Directory Layout, 3. Core Components, Abstract Provider (`llm/base.py`), code:text (llm/), code:yaml (provider: gemini), Configuration (`llm_config.yaml`), Embedding Decoupling (`retrieval/schema_retriever.py`) (+3 more)

### Community 52 - "Community 52"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates ChatGoogleGenerativeAI with registered thread-local callbacks., Instantiates GoogleGenerativeAIEmbeddings.

### Community 53 - "Community 53"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates ChatOllama with registered thread-local callbacks.         Supports, Instantiates OllamaEmbeddings.

### Community 54 - "Community 54"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates ChatOpenAI with registered thread-local callbacks., Instantiates OpenAIEmbeddings.

### Community 55 - "Community 55"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates ChatOpenAI pointed to vLLM's custom base URL., Instantiates OpenAIEmbeddings pointed to vLLM's custom base URL.

## Knowledge Gaps
- **130 isolated node(s):** `int`, `str`, `liveServer.settings.port`, `float`, `BaseChatModel` (+125 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm()` connect `Community 3` to `Community 1`, `Community 45`, `Community 49`, `Community 50`, `Community 23`, `Community 24`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `Community 47` to `Community 45`, `Community 48`, `Community 49`, `Community 50`, `Community 52`, `Community 53`, `Community 54`, `Community 55`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `get_provider()` connect `Community 45` to `Community 24`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LLMProvider` (e.g. with `AnthropicProvider` and `Any`) actually correct?**
  _`LLMProvider` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `GeminiProvider` (e.g. with `LLMProviderFactory` and `Any`) actually correct?**
  _`GeminiProvider` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `AnthropicProvider` (e.g. with `LLMProvider` and `LLMProviderFactory`) actually correct?**
  _`AnthropicProvider` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `int`, `str`, `Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema` to the rest of the system?**
  _263 weakly-connected nodes found - possible documentation gaps or missing edges._