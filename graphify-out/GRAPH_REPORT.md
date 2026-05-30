# Graph Report - SQLAgent-Mini-Project  (2026-05-30)

## Corpus Check
- 77 files · ~136,273 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 859 nodes · 1438 edges · 76 communities (70 shown, 6 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 154 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0f905c27`
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
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 48 edges
2. `OllamaProvider` - 25 edges
3. `VLLMProvider` - 25 edges
4. `get_llm()` - 23 edges
5. `TestLLMProviders` - 23 edges
6. `init_metrics_state()` - 22 edges
7. `BenchmarkCase` - 21 edges
8. `SQLErrorClassification` - 21 edges
9. `BenchmarkResult` - 20 edges
10. `BenchmarkSummary` - 20 edges

## Surprising Connections (you probably didn't know these)
- `SQLCorrectionResult` --uses--> `SQLCorrectionResult`  [INFERRED]
  features/validation_correction/agent.py → schemas/validation.py
- `bool` --uses--> `VLLMProvider`  [INFERRED]
  core/air_gap.py → llm/vllm_provider.py
- `TestProductionSecurity` --uses--> `SecurityException`  [INFERRED]
  scratch/test_security.py → core/security.py
- `TestProductionSecurity` --uses--> `RolePermissions`  [INFERRED]
  scratch/test_security.py → core/security.py
- `SQLAgentState` --uses--> `QueryPlan`  [INFERRED]
  core/state.py → schemas/planner.py

## Communities (76 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (20): Observability Package Initialization, init_metrics_state(), Any, bool, int, str, Observability Metrics Tracking Framework  Implements reusable context managers,, Appends a detailed log of a query repair/correction attempt to the loop history. (+12 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (28): 1. Architectural Overview, 2. Step 1: Pre-downloading Model Weights & Software, 3. Step 2: On-Premises Local Model Infrastructure, 4. Step 3: SQLAgent Air-Gapped Configurations, 5. Step 4: Schema Reflection & Vector Indexing Cache, 6. Step 5: Startup Verification and Fail-Fast Guards, 7. Troubleshooting & Recovery, A. Environment Configuration (`.env`) (+20 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (20): ndarray, Retrieval Module Initialization, get_schema_retriever(), Any, bool, int, str, FAISS-Based Database Schema Retriever  Dynamically reflects database metadata us (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (20): get_llm(), BaseChatModel, float, Returns a configured LangChain ChatModel instance from the active provider., LangGraph State Definition  Represents the memory passed between nodes during ex, QueryPlan, str, QueryPlan (+12 more)

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

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (16): lifespan(), FastAPI Application Setup  Provides an entry point for running the API backend., is_air_gap_enabled(), Air-Gapped Deployment Mode Validation Engine  Validates the offline integrity of, Checks if Air-Gapped Deployment Mode is enabled via environment variables     or, Validates that the current environment complies with Air-Gapped Deployment Mode., validate_air_gap_environment(), FastAPI (+8 more)

### Community 23 - "Community 23"
Cohesion: 0.07
Nodes (28): Any, str, Structured response representing the semantic correctness verification of a gene, SemanticValidationResult, MockAIMessage, Verify that correct_sql handles a successful AST clause repair directly., Verify that correct_sql handles a successful AST clause repair directly., A clean, realistic mock of a LangChain AIMessage response. (+20 more)

### Community 24 - "Community 24"
Cohesion: 0.21
Nodes (22): BenchmarkResult, BenchmarkSummary, compile_failure_analysis(), main(), print_summary_dashboard(), Any, BenchmarkCase, BenchmarkResult (+14 more)

### Community 28 - "Community 28"
Cohesion: 0.10
Nodes (24): Any, bool, execute_sql_query(), get_db(), str, Database connection and utilities.  Handles PostgreSQL connection setup using SQ, Yields a database session., Executes a raw SQL SELECT query against the PostgreSQL database safely. (+16 more)

### Community 29 - "Community 29"
Cohesion: 0.07
Nodes (26): columns, fk_columns, pk_columns, db_metadata, categories, order_items, orders, products (+18 more)

### Community 31 - "Community 31"
Cohesion: 0.50
Nodes (4): Metrics Tracked, Objective, PRIORITY 2 — Evaluation Framework [COMPLETED], Status

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (11): Architecture & System Design, Completed, Core Pipeline, Correction Workflow, In Progress, Infrastructure, Optimization, Project Overview (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.33
Nodes (6): Backend, Core, Current Tech Stack, Frontend, LLM Providers, SQL Tooling

### Community 34 - "Community 34"
Cohesion: 0.50
Nodes (4): Implemented Specifications, Objective, PRIORITY 8 — Enterprise Local LLM Support [COMPLETED], Target Models

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 4 — Clause-Level SQL Repair, Status

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (6): Datasets, Goal, Metrics, Objective, PRIORITY 10 — Benchmark Expansion [COMPLETED], Status

### Community 37 - "Community 37"
Cohesion: 0.50
Nodes (4): Implemented Architecture, Objective, PRIORITY 7 — Provider-Agnostic LLM Layer [COMPLETED], Requirements Fulfilled

### Community 38 - "Community 38"
Cohesion: 0.40
Nodes (5): Error Categories, Goal, Objective, PRIORITY 9 — Formal Error Taxonomy Engine [COMPLETED], Status

### Community 39 - "Community 39"
Cohesion: 0.06
Nodes (39): bool, str, SQLErrorClassification, str, SQLErrorClassification, str, SQL Error Taxonomy Pydantic Schemas  Defines the formal representation of SQL sy, Structured classification of a SQL error within the formal error taxonomy. (+31 more)

### Community 40 - "Community 40"
Cohesion: 0.10
Nodes (12): disable_socket_shield(), enable_socket_shield(), Verify is_air_gap_enabled accurately checks env and yaml., Verify that cloud providers are rejected immediately in air-gapped mode., Verify cloud keys in env trigger warning logs but don't crash., Verify Ollama setup checks both chat model and embeddings model presence., Verify vLLM checks both chat model and embeddings model presence., 8. Run end-to-end SQLAgent graph while strict socket shield is ACTIVE. (+4 more)

### Community 43 - "Community 43"
Cohesion: 0.33
Nodes (6): Features, Features Met, Objective, PRIORITY 11 — Production Governance & Security, PRIORITY 11 — Production Governance & Security [COMPLETED], Status

### Community 44 - "Community 44"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 5 — Schema Retrieval Layer [COMPLETED], Status

### Community 45 - "Community 45"
Cohesion: 0.18
Nodes (22): AnthropicProvider, Concrete provider implementation for Anthropic Claude., LLMProviderFactory, Any, LLMProvider, str, LLM Provider Factory  Manages runtime config loading from yaml or env variables, Factory to construct and configure the globally selected LLMProvider. (+14 more)

### Community 46 - "Community 46"
Cohesion: 0.09
Nodes (21): 1. Quick Start (Configuring a Provider), 2. Setting Up Local / Private Deployment Mode, 3. Developer Notes, Anthropic Claude, code:env (GOOGLE_API_KEY=your-api-key), code:bash (python -m vllm.entrypoints.openai.api_server --model Qwen/Qw), code:yaml (provider: vllm), code:yaml (vllm:) (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.14
Nodes (11): Any, BaseChatModel, Embeddings, float, str, Instantiates ChatOpenAI pointed to vLLM's custom base URL.         Runs lazy hea, Instantiates ChatOpenAI pointed to vLLM's custom base URL.         Runs lazy hea, Instantiates OpenAIEmbeddings pointed to vLLM's custom base URL and runs validat (+3 more)

### Community 48 - "Community 48"
Cohesion: 0.11
Nodes (9): Verifies VLLMProvider pointed to OpenAI-compatible base URL., Verifies vLLM check_health passes when server responds with the matching model., Verifies vLLM check_health raises ConnectionError when server is offline., Verifies vLLM check_health raises RuntimeError when the configured model is abse, Verifies that shared retry policies wrap models successfully., Verifies factory correctly loads defaults from environment variables when YAML i, Verifies OpenAIProvider instantiates standard OpenAI classes., Verifies AnthropicProvider instantiates Anthropic classes and fallback embedding (+1 more)

### Community 49 - "Community 49"
Cohesion: 0.12
Nodes (8): 4. Verify column-level RBAC restrictions (e.g. Analyst accessing email)., 5. Verify SQL limits are clamped or injected based on role threshold., 6. Verify returned database records are masked for sensitive fields., 7. Verify security actions write clean events to observability/audit_log.json., 1. Verify PII in user questions is properly redacted before hitting LLMs., 2. Verify schema pruning removes unauthorized tables and columns by role., 3. Verify SELECT-only, system table protection, and table-level RBAC., TestProductionSecurity

### Community 50 - "Community 50"
Cohesion: 0.07
Nodes (24): get_active_callbacks(), Returns the list of active callbacks for the current thread., Any, BaseChatModel, Embeddings, float, str, Anthropic LLM Provider Implementation  Configures ChatAnthropic and handles fall (+16 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (17): 1. Design Philosophy, 2. Directory Layout, 3. Core Components, 4. Local LLM & Ollama Support (Priority 8), 5. Enterprise vLLM Support (Priority 8 Extension), Abstract Provider (`llm/base.py`), code:text (llm/), code:yaml (provider: gemini) (+9 more)

### Community 52 - "Community 52"
Cohesion: 0.09
Nodes (24): AuditLogger, PIIRedactor, Any, str, Production Governance and Security Module  Implements Role-Based Access Control, Handles regex-based scanning and redaction of PII from user inputs,     along wi, Redacts highly sensitive patterns like emails and phone numbers from user questi, Masks/redacts a specific PII data cell value according to its column type. (+16 more)

### Community 53 - "Community 53"
Cohesion: 0.09
Nodes (18): bool, OllamaProvider, Any, BaseChatModel, Embeddings, float, str, Instantiates ChatOllama with registered thread-local callbacks and streaming. (+10 more)

### Community 54 - "Community 54"
Cohesion: 0.67
Nodes (3): Current Maturity, Current Project Status, Main Focus Going Forward

### Community 55 - "Community 55"
Cohesion: 0.50
Nodes (4): SQLCorrectionResult, correct_sql(), Calls the LLM to fix a broken SQL query based on the schema and error message., Calls the LLM to fix a broken SQL query based on the schema and error message.

### Community 56 - "Community 56"
Cohesion: 0.16
Nodes (14): ask_database(), QueryRequest, QueryResponse, FastAPI Routes  Defines endpoints for the SQLAgent application., Takes a natural language query, runs it through the SQLAgent graph,     and retu, Takes a natural language query, runs it through the SQLAgent graph,     and retu, BaseModel, clear_thread_callbacks() (+6 more)

### Community 57 - "Community 57"
Cohesion: 0.14
Nodes (12): load_dataset(), BenchmarkCase, str, NL2SQL Dataset Loaders  Provides standardized loading methods for importing and, Loads and parses a specified benchmark dataset JSON file into a list of     vali, BenchmarkCase, Represents a single test case in the evaluation suite., Verify that write_dataset_reports successfully serializes JSON metrics and markd (+4 more)

### Community 58 - "Community 58"
Cohesion: 0.67
Nodes (3): DO, DO NOT, Important Development Rules

### Community 59 - "Community 59"
Cohesion: 0.26
Nodes (16): node_clarify_intent(), node_correct_sql(), node_execute_sql(), node_query_planning(), node_retrieve_schema(), node_semantic_validate(), node_sql_generation(), node_validate_sql() (+8 more)

### Community 60 - "Community 60"
Cohesion: 0.14
Nodes (11): ABC, apply_shared_retry(), Any, BaseChatModel, Embeddings, float, int, LLM Provider Base Interface  Defines the abstract contract for all model provide (+3 more)

### Community 64 - "Community 64"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 6 — Observability & Transparency [COMPLETED], Status

### Community 65 - "Community 65"
Cohesion: 0.18
Nodes (14): extract_text(), Any, str, Safely extracts string content from an LLM response or AIMessage.     Handles st, bool, str, clarify_intent(), get_matched_vague_terms() (+6 more)

### Community 66 - "Community 66"
Cohesion: 0.18
Nodes (12): build_workflow(), Compiles and returns the LangGraph application., Compiles and returns the LangGraph application., Compiles and returns the LangGraph application., get_database_schema(), Extracts table names, columns, and data types from the connected PostgreSQL data, NL2SQL Evaluation Benchmark Runner  Compiles and executes the LangGraph SQLAgent, Orchestrates the execution of all benchmark cases, captures metrics,     and log (+4 more)

### Community 67 - "Community 67"
Cohesion: 0.25
Nodes (7): action, details, error, sql, role, timestamp, username

### Community 68 - "Community 68"
Cohesion: 0.20
Nodes (6): BaseCallbackHandler, BaseCallbackHandler, LangChain Callback handler to transparently capture token usage., TokenUsageTracker, LangChain Callback handler to transparently capture token usage., TokenUsageTracker

### Community 69 - "Community 69"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates ChatGoogleGenerativeAI with registered thread-local callbacks., Instantiates GoogleGenerativeAIEmbeddings.

### Community 70 - "Community 70"
Cohesion: 0.40
Nodes (6): BenchmarkResult, BenchmarkSummary, Saves full run logs to file system and updates failed_queries.json, Prints a rich ANSI console dashboard summarizing the run., render_dashboard(), write_reports()

### Community 71 - "Community 71"
Cohesion: 0.50
Nodes (4): decide_after_execution(), Conditional Edge routing after executing SQL query., Conditional Edge routing after executing SQL query., Conditional Edge routing after executing SQL query.

### Community 72 - "Community 72"
Cohesion: 0.50
Nodes (4): decide_after_semantic_validation(), Conditional Edge routing after semantic verification., Conditional Edge routing after semantic verification., Conditional Edge routing after semantic verification.

### Community 73 - "Community 73"
Cohesion: 0.50
Nodes (4): decide_after_syntax_validation(), Conditional Edge routing after checking SQL syntax and safety., Conditional Edge routing after checking SQL syntax and safety., Conditional Edge routing after checking SQL syntax and safety.

### Community 74 - "Community 74"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 3 — Semantic Validation [COMPLETED], Status

### Community 75 - "Community 75"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 12 — Air-Gapped Deployment Mode [COMPLETED], Status

## Knowledge Gaps
- **157 isolated node(s):** `int`, `str`, `liveServer.settings.port`, `float`, `BaseChatModel` (+152 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm()` connect `Community 3` to `Community 65`, `Community 39`, `Community 10`, `Community 45`, `Community 50`, `Community 55`, `Community 23`, `Community 56`, `Community 60`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `build_workflow()` connect `Community 66` to `Community 40`, `Community 10`, `Community 56`, `Community 24`, `Community 59`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `Community 50` to `Community 69`, `Community 45`, `Community 47`, `Community 48`, `Community 53`, `Community 60`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LLMProvider` (e.g. with `AnthropicProvider` and `Any`) actually correct?**
  _`LLMProvider` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `OllamaProvider` (e.g. with `bool` and `LLMProviderFactory`) actually correct?**
  _`OllamaProvider` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `VLLMProvider` (e.g. with `bool` and `LLMProviderFactory`) actually correct?**
  _`VLLMProvider` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TestLLMProviders` (e.g. with `AnthropicProvider` and `LLMProvider`) actually correct?**
  _`TestLLMProviders` has 7 INFERRED edges - model-reasoned connections that need verification._