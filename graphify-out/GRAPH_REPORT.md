# Graph Report - SQLAgent-Mini-Project  (2026-06-15)

## Corpus Check
- 85 files · ~126,095 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1005 nodes · 1650 edges · 83 communities (75 shown, 8 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 179 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d60082a3`
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
- [[_COMMUNITY_Community 20|Community 20]]
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
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 55 edges
2. `TestLLMProviders` - 30 edges
3. `GeminiProvider` - 27 edges
4. `LMStudioProvider` - 27 edges
5. `get_llm()` - 26 edges
6. `OllamaProvider` - 26 edges
7. `VLLMProvider` - 26 edges
8. `init_metrics_state()` - 22 edges
9. `BenchmarkCase` - 21 edges
10. `load_config()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `SQLErrorClassification` --uses--> `SQLErrorClassification`  [INFERRED]
  features/validation_correction/repair_engine.py → schemas/error_taxonomy.py
- `TestProductionSecurity` --uses--> `SecurityException`  [INFERRED]
  scratch/test_security.py → core/security.py
- `TestProductionSecurity` --uses--> `RolePermissions`  [INFERRED]
  scratch/test_security.py → core/security.py
- `SQLAgentState` --uses--> `QueryPlan`  [INFERRED]
  core/state.py → schemas/planner.py
- `str` --uses--> `QueryPlan`  [INFERRED]
  features/query_planning/agent.py → schemas/planner.py

## Communities (83 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (55): decide_after_execution(), decide_after_semantic_validation(), decide_after_syntax_validation(), node_clarify_intent(), node_correct_sql(), node_execute_sql(), node_query_planning(), node_retrieve_schema() (+47 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (28): 1. Architectural Overview, 2. Step 1: Pre-downloading Model Weights & Software, 3. Step 2: On-Premises Local Model Infrastructure, 4. Step 3: SQLAgent Air-Gapped Configurations, 5. Step 4: Schema Reflection & Vector Indexing Cache, 6. Step 5: Startup Verification and Fail-Fast Guards, 7. Troubleshooting & Recovery, A. Environment Configuration (`.env`) (+20 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (23): int, str, int, ndarray, Retrieval Module Initialization, Any, bool, int (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates and returns a configured LangChain ChatModel.          Args:, Instantiates and returns a configured LangChain Embeddings model.          Args:

### Community 4 - "Community 4"
Cohesion: 0.36
Nodes (8): Base, Category, Order, OrderItem, Product, Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema, Review, User

### Community 5 - "Community 5"
Cohesion: 0.20
Nodes (9): Architecture Philosophy, Current Architecture, Enterprise Architecture Vision, Final Vision, High Priority Roadmap, Objective, PRIORITY 4 — Clause-Level SQL Repair, Recommended Future Architecture (+1 more)

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (6): 1. Intent Clarification Agent, 2. Query Planning Agent, 3. SQL Generation Agent, 4. Validation & Correction Agent, Multi-Agent System Design, System Flow

### Community 8 - "Community 8"
Cohesion: 0.22
Nodes (9): Logger, LogRecord, ColoredFormatter, int, str, Observability Structured Logger  Defines a custom structured logging setup that, Custom formatter to inject console colors depending on log levels and names., Sets up a colored structured logger instance.          Args:         name: Name (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (21): 1. Unstructured LLM Outputs, 2. Full SQL Regeneration During Correction, 3. Validation Is Mostly Syntax-Level, 4. No Real Schema Retrieval Layer, 5. Limited Observability, Critical Weaknesses To Address, Current Problem, Current Validation (+13 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (38): categories, department, id, name, order_items, id, order_id, product_id (+30 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (11): 1. Launch LM Studio Server, 2. Configure Environment `.env`, 3. YAML Configuration (`config/providers.yaml`), 4. Run the Application, code:env (# Enable LM Studio Provider), code:yaml (provider: lmstudio), code:bash (uvicorn api.app:app --reload), code:bash (streamlit run frontend/app.py) (+3 more)

### Community 20 - "Community 20"
Cohesion: 0.17
Nodes (13): ask_database(), get_benchmark(), get_config(), str, QueryRequest, QueryResponse, FastAPI Routes  Defines endpoints for the SQLAgent application., Returns the current LLM configurations and dynamic schema settings. (+5 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (18): Any, str, Structured response representing the semantic correctness verification of a gene, SemanticValidationResult, MockAIMessage, str, Mock of LangChain AIMessage response., Verify that a missing filter literal triggers a rule violation warning alert. (+10 more)

### Community 24 - "Community 24"
Cohesion: 0.06
Nodes (60): BaseCallbackHandler, BenchmarkCase, clear_thread_callbacks(), BaseCallbackHandler, Registers callbacks for the current thread., Clears callbacks for the current thread., register_thread_callbacks(), BenchmarkResult (+52 more)

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (19): bool, clear_schema_cache(), execute_sql_query(), get_db(), str, Database connection and utilities.  Handles PostgreSQL connection setup using SQ, Yields a database session., Clears the reflected database schema cache to force re-reflection on next access (+11 more)

### Community 29 - "Community 29"
Cohesion: 0.05
Nodes (43): activeEngineBadge, activeUserBadge, appState, benchDataView, benchDifficultyBars, benchErrorBars, benchFailuresTable, benchKpis (+35 more)

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
Cohesion: 0.07
Nodes (26): columns, fk_columns, pk_columns, db_metadata, categories, order_items, orders, products (+18 more)

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
Cohesion: 0.12
Nodes (18): SQLErrorClassification, str, SQL Error Taxonomy Pydantic Schemas  Defines the formal representation of SQL sy, Structured classification of a SQL error within the formal error taxonomy., SQLErrorClassification, MockAIMessage, str, Verify AST clause repair with taxonomy classification context. (+10 more)

### Community 40 - "Community 40"
Cohesion: 0.09
Nodes (13): disable_socket_shield(), enable_socket_shield(), Verify is_air_gap_enabled accurately checks env and yaml., Verify that cloud providers are rejected immediately in air-gapped mode., Verify cloud keys in env trigger warning logs but don't crash., Verify Ollama setup checks both chat model and embeddings model presence., Verify vLLM checks both chat model and embeddings model presence., Verify LM Studio checks both chat model and embeddings model presence. (+5 more)

### Community 43 - "Community 43"
Cohesion: 0.50
Nodes (4): Features Met, Objective, PRIORITY 11 — Production Governance & Security [COMPLETED], Status

### Community 44 - "Community 44"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 5 — Schema Retrieval Layer [COMPLETED], Status

### Community 45 - "Community 45"
Cohesion: 0.14
Nodes (34): is_air_gap_enabled(), bool, Air-Gapped Deployment Mode Validation Engine  Validates the offline integrity of, Checks if Air-Gapped Deployment Mode is enabled via environment variables     or, Validates that the current environment complies with Air-Gapped Deployment Mode., validate_air_gap_environment(), AnthropicProvider, Concrete provider implementation for Anthropic Claude. (+26 more)

### Community 46 - "Community 46"
Cohesion: 0.09
Nodes (21): 1. Quick Start (Configuring a Provider), 2. Setting Up Local / Private Deployment Mode, 3. Developer Notes, Anthropic Claude, code:env (GOOGLE_API_KEY=your-api-key), code:bash (python -m vllm.entrypoints.openai.api_server --model Qwen/Qw), code:yaml (provider: vllm), code:yaml (vllm:) (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (8): Any, BaseChatModel, Embeddings, float, str, Instantiates ChatOpenAI pointed to vLLM's custom base URL.         Runs lazy hea, Instantiates OpenAIEmbeddings pointed to vLLM's custom base URL and runs validat, Pings the vLLM local endpoint and checks if the configured model is hosted.

### Community 48 - "Community 48"
Cohesion: 0.06
Nodes (18): Verifies OllamaProvider configurations for local inference., Verifies check_health passes when server responds with the matching model., Verifies check_health raises ConnectionError when server is offline., Verifies check_health raises RuntimeError when the configured model is absent., Verifies VLLMProvider pointed to OpenAI-compatible base URL., Verifies vLLM check_health passes when server responds with the matching model., Verifies vLLM check_health raises ConnectionError when server is offline., Verifies vLLM check_health raises RuntimeError when the configured model is abse (+10 more)

### Community 49 - "Community 49"
Cohesion: 0.08
Nodes (29): ABC, get_active_callbacks(), Returns the list of active callbacks for the current thread., Any, BaseChatModel, Embeddings, float, Anthropic LLM Provider Implementation  Configures ChatAnthropic and handles fall (+21 more)

### Community 50 - "Community 50"
Cohesion: 0.67
Nodes (3): Current Maturity, Current Project Status, Main Focus Going Forward

### Community 51 - "Community 51"
Cohesion: 0.10
Nodes (19): 1. Design Philosophy, 2. Directory Layout, 3. Core Components, 4. Local LLM & Ollama Support (Priority 8), 5. Enterprise vLLM Support (Priority 8 Extension), 6. Local LM Studio Support (Priority 8 Extension), Abstract Provider (`llm/base.py`), code:text (llm/) (+11 more)

### Community 52 - "Community 52"
Cohesion: 0.13
Nodes (13): AuditLogger, PIIRedactor, Any, str, Handles regex-based scanning and redaction of PII from user inputs,     along wi, Redacts highly sensitive patterns like emails and phone numbers from user questi, Masks/redacts a specific PII data cell value according to its column type., Scans execution rows and masks values in columns that are registered as PII (+5 more)

### Community 53 - "Community 53"
Cohesion: 0.18
Nodes (8): Any, BaseChatModel, Embeddings, float, str, Instantiates ChatOllama with registered thread-local callbacks and streaming., Instantiates OllamaEmbeddings and runs validation checks., Pings the Ollama local endpoint and checks if the configured model is already pu

### Community 54 - "Community 54"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 1 — Structured Outputs, Tasks

### Community 55 - "Community 55"
Cohesion: 0.14
Nodes (16): bool, str, Validation & Correction Pydantic Schemas  Defines structural models for SQL sema, Structured response representing the output of the query correction agent., Structured response representing the output of the query correction agent., SQLCorrectionResult, Unit test suite using mock LLM responses to verify SQL validation, correction, a, Verify taxonomy integration in correct_sql when AST repair succeeds. (+8 more)

### Community 56 - "Community 56"
Cohesion: 0.21
Nodes (9): SQLErrorClassification, str, TestASTRepairEngine, detect_failing_clause(), Surgically repairs a specific failing clause in a SQL query using SQLGlot AST ma, Parses the error message string to detect which clause is failing.     Returns:, Surgically repairs a specific failing clause in a SQL query using SQLGlot AST ma, Parses the error message string to detect which clause is failing.     Returns: (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.13
Nodes (11): MockAIMessage, str, Verify that correct_sql handles a successful AST clause repair directly., Verify that correct_sql handles a successful AST clause repair directly., A clean, realistic mock of a LangChain AIMessage response., A clean, realistic mock of a LangChain AIMessage response., Verify that validate_sql_semantics correctly parses and validates a JSON respons, Verify that validate_sql_semantics correctly parses and validates a JSON respons (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.67
Nodes (3): DO, DO NOT, Important Development Rules

### Community 59 - "Community 59"
Cohesion: 0.33
Nodes (6): appendMessage(), handleQuerySubmit(), hideWelcome(), loadBackendConfig(), syncEngineBadge(), syncUserBadges()

### Community 64 - "Community 64"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 6 — Observability & Transparency [COMPLETED], Status

### Community 65 - "Community 65"
Cohesion: 0.11
Nodes (17): Embeddings, GeminiProvider, Any, Embeddings, str, Concrete provider implementation for Google Gemini., Instantiates GoogleGenerativeAIEmbeddings., Any (+9 more)

### Community 67 - "Community 67"
Cohesion: 0.25
Nodes (7): action, details, error, sql, role, timestamp, username

### Community 68 - "Community 68"
Cohesion: 0.29
Nodes (7): build_workflow(), Compiles and returns the LangGraph application., get_database_schema(), Extracts table names, columns, and data types from the connected PostgreSQL data, test_e2e_pipeline(), Security and Governance Test Suite  Validates all security, safety, and RBAC req, 8. Run end-to-end security scenarios through the LangGraph workflow.

### Community 71 - "Community 71"
Cohesion: 0.20
Nodes (10): BaseChatModel, extract_text(), get_llm(), Any, BaseChatModel, float, str, Safely extracts string content from an LLM response or AIMessage.     Handles st (+2 more)

### Community 73 - "Community 73"
Cohesion: 0.13
Nodes (16): LangGraph State Definition  Represents the memory passed between nodes during ex, QueryPlan, str, QueryPlan, str, generate_query_plan(), Query Planning Agent  Converts a refined natural language query into a structure, Generates a structured, step-by-step SQL query plan from a refined     natural l (+8 more)

### Community 74 - "Community 74"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 3 — Semantic Validation [COMPLETED], Status

### Community 75 - "Community 75"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 12 — Air-Gapped Deployment Mode [COMPLETED], Status

### Community 76 - "Community 76"
Cohesion: 0.50
Nodes (4): loadBenchmarkData(), renderBenchmarkMetrics(), renderObservability(), switchPage()

### Community 77 - "Community 77"
Cohesion: 0.12
Nodes (8): 4. Verify column-level RBAC restrictions (e.g. Analyst accessing email)., 5. Verify SQL limits are clamped or injected based on role threshold., 6. Verify returned database records are masked for sensitive fields., 7. Verify security actions write clean events to observability/audit_log.json., 1. Verify PII in user questions is properly redacted before hitting LLMs., 2. Verify schema pruning removes unauthorized tables and columns by role., 3. Verify SELECT-only, system table protection, and table-level RBAC., TestProductionSecurity

### Community 78 - "Community 78"
Cohesion: 0.50
Nodes (3): lifespan(), FastAPI Application Setup (Gemini Active)  Provides an entry point for running t, FastAPI

### Community 79 - "Community 79"
Cohesion: 0.33
Nodes (4): apply_shared_retry(), int, Wraps the ChatModel with a robust, standardized exponential-backoff retry policy, Verifies that shared retry policies wrap models successfully.

### Community 80 - "Community 80"
Cohesion: 0.17
Nodes (10): BaseModel, AggregationRequirement, FilterRequirement, JoinRequirement, OrderByRequirement, Any, TableRequirement, LMStudioProviderSettings (+2 more)

### Community 81 - "Community 81"
Cohesion: 0.16
Nodes (11): Production Governance and Security Module  Implements Role-Based Access Control, Global coordinator for database governance, RBAC enforcement, PII scrubbing,, Exception raised when a security policy or validation check is violated., Fetches the permissions mapping for a given role, falling back securely., Removes unauthorized tables and columns from the database schema context., Parses generated SQL, performs static AST verification for RBAC,         prevent, Pydantic model representing the global enterprise security policy configuration., SecurityConfig (+3 more)

## Knowledge Gaps
- **241 isolated node(s):** `int`, `str`, `liveServer.settings.port`, `str`, `float` (+236 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm()` connect `Community 71` to `Community 0`, `Community 39`, `Community 73`, `Community 45`, `Community 79`, `Community 49`, `Community 23`, `Community 55`, `Community 56`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `Community 49` to `Community 65`, `Community 3`, `Community 45`, `Community 47`, `Community 48`, `Community 82`, `Community 53`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `load_config()` connect `Community 45` to `Community 71`, `Community 79`, `Community 48`, `Community 20`, `Community 24`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `LLMProvider` (e.g. with `AnthropicProvider` and `Any`) actually correct?**
  _`LLMProvider` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `TestLLMProviders` (e.g. with `AnthropicProvider` and `LLMProvider`) actually correct?**
  _`TestLLMProviders` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `GeminiProvider` (e.g. with `LLMProviderFactory` and `Any`) actually correct?**
  _`GeminiProvider` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `LMStudioProvider` (e.g. with `bool` and `bool`) actually correct?**
  _`LMStudioProvider` has 11 INFERRED edges - model-reasoned connections that need verification._