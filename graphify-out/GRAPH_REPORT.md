# Graph Report - SQLAgent-Mini-Project  (2026-05-29)

## Corpus Check
- 71 files · ~129,935 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 706 nodes · 1197 edges · 65 communities (58 shown, 7 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 141 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `775d176f`
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

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 48 edges
2. `get_llm()` - 23 edges
3. `TestLLMProviders` - 23 edges
4. `init_metrics_state()` - 22 edges
5. `OllamaProvider` - 21 edges
6. `VLLMProvider` - 21 edges
7. `SQLErrorClassification` - 21 edges
8. `BenchmarkCase` - 19 edges
9. `BenchmarkResult` - 18 edges
10. `BenchmarkSummary` - 18 edges

## Surprising Connections (you probably didn't know these)
- `SemanticValidationResult` --uses--> `SemanticValidationResult`  [INFERRED]
  features/validation_correction/semantic_validator.py → schemas/validation.py
- `str` --uses--> `SemanticValidationResult`  [INFERRED]
  scratch/test_semantic_validator.py → schemas/validation.py
- `SQLErrorClassification` --uses--> `SQLErrorClassification`  [INFERRED]
  features/validation_correction/repair_engine.py → schemas/error_taxonomy.py
- `str` --uses--> `SemanticValidationResult`  [INFERRED]
  features/validation_correction/semantic_validator.py → schemas/validation.py
- `Any` --uses--> `SemanticValidationResult`  [INFERRED]
  features/validation_correction/semantic_validator.py → schemas/validation.py

## Communities (65 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (59): decide_after_execution(), decide_after_semantic_validation(), decide_after_syntax_validation(), node_clarify_intent(), node_correct_sql(), node_execute_sql(), node_query_planning(), node_retrieve_schema() (+51 more)

### Community 1 - "Community 1"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates ChatAnthropic with registered thread-local callbacks., Anthropic does not offer a native text embeddings API in LangChain.         We f

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (20): ndarray, Retrieval Module Initialization, get_schema_retriever(), Any, bool, int, str, FAISS-Based Database Schema Retriever  Dynamically reflects database metadata us (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (33): extract_text(), get_llm(), Any, BaseChatModel, float, str, Returns a configured LangChain ChatModel instance from the active provider., Safely extracts string content from an LLM response or AIMessage.     Handles st (+25 more)

### Community 4 - "Community 4"
Cohesion: 0.36
Nodes (8): Base, Category, Order, OrderItem, Product, Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema, Review, User

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (6): Architecture Philosophy, Current Architecture, Enterprise Architecture Vision, Final Vision, High Priority Roadmap, Recommended Future Architecture

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
Cohesion: 0.11
Nodes (16): Any, str, MockAIMessage, str, Mock of LangChain AIMessage response., Verify that a missing filter literal triggers a rule violation warning alert., Verify that missing AVG or SUM aggregate functions triggers a rule violation war, Verify that missing LIMIT or ORDER BY on top-ranked intent triggers warning aler (+8 more)

### Community 24 - "Community 24"
Cohesion: 0.06
Nodes (65): ask_database(), QueryRequest, QueryResponse, FastAPI Routes  Defines endpoints for the SQLAgent application., Takes a natural language query, runs it through the SQLAgent graph,     and retu, BaseCallbackHandler, BaseModel, BenchmarkResult (+57 more)

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (18): Any, bool, compare_results(), evaluate_execution_accuracy(), normalize_results(), Any, bool, str (+10 more)

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
Cohesion: 0.14
Nodes (9): MockAIMessage, str, Verify AST clause repair with taxonomy classification context., Verify taxonomy integration in correct_sql when AST repair succeeds., Verify taxonomy integration in correct_sql when AST fails and falls back to full, Mock of LangChain AIMessage response., Verify rule-based taxonomy heuristics on common SQL failures., Verify LLM-driven structured error classification parsing. (+1 more)

### Community 40 - "Community 40"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 1 — Structured Outputs, Tasks

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
Cohesion: 0.18
Nodes (8): Any, BaseChatModel, Embeddings, float, str, Instantiates ChatOpenAI pointed to vLLM's custom base URL.         Runs lazy hea, Instantiates OpenAIEmbeddings pointed to vLLM's custom base URL and runs validat, Pings the vLLM local endpoint and checks if the configured model is hosted.

### Community 48 - "Community 48"
Cohesion: 0.07
Nodes (14): Verifies OllamaProvider configurations for local inference., Verifies check_health passes when server responds with the matching model., Verifies check_health raises ConnectionError when server is offline., Verifies check_health raises RuntimeError when the configured model is absent., Verifies VLLMProvider pointed to OpenAI-compatible base URL., Verifies vLLM check_health passes when server responds with the matching model., Verifies vLLM check_health raises ConnectionError when server is offline., Verifies vLLM check_health raises RuntimeError when the configured model is abse (+6 more)

### Community 49 - "Community 49"
Cohesion: 0.25
Nodes (7): Validation & Correction Pydantic Schemas  Defines structural models for SQL sema, Structured response representing the semantic correctness verification of a gene, SemanticValidationResult, MockAIMessage, str, A clean, realistic mock of a LangChain AIMessage response., A clean, realistic mock of a LangChain AIMessage response.

### Community 50 - "Community 50"
Cohesion: 0.08
Nodes (20): ABC, get_active_callbacks(), Returns the list of active callbacks for the current thread., str, Anthropic LLM Provider Implementation  Configures ChatAnthropic and handles fall, LLMProvider, LLM Provider Base Interface  Defines the abstract contract for all model provide, Abstract interface defining the contract for provider-agnostic model creation. (+12 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (17): 1. Design Philosophy, 2. Directory Layout, 3. Core Components, 4. Local LLM & Ollama Support (Priority 8), 5. Enterprise vLLM Support (Priority 8 Extension), Abstract Provider (`llm/base.py`), code:text (llm/), code:yaml (provider: gemini) (+9 more)

### Community 52 - "Community 52"
Cohesion: 0.25
Nodes (6): Any, BaseChatModel, Embeddings, float, Instantiates ChatGoogleGenerativeAI with registered thread-local callbacks., Instantiates GoogleGenerativeAIEmbeddings.

### Community 53 - "Community 53"
Cohesion: 0.18
Nodes (8): Any, BaseChatModel, Embeddings, float, str, Instantiates ChatOllama with registered thread-local callbacks and streaming., Instantiates OllamaEmbeddings and runs validation checks., Pings the Ollama local endpoint and checks if the configured model is already pu

### Community 54 - "Community 54"
Cohesion: 0.67
Nodes (3): Current Maturity, Current Project Status, Main Focus Going Forward

### Community 55 - "Community 55"
Cohesion: 0.18
Nodes (14): bool, str, Structured response representing the output of the query correction agent., Structured response representing the output of the query correction agent., SQLCorrectionResult, Unit test suite using mock LLM responses to verify SQL validation, correction, a, SQLCorrectionResult, correct_sql() (+6 more)

### Community 56 - "Community 56"
Cohesion: 0.21
Nodes (9): SQLErrorClassification, str, TestASTRepairEngine, detect_failing_clause(), Surgically repairs a specific failing clause in a SQL query using SQLGlot AST ma, Parses the error message string to detect which clause is failing.     Returns:, Surgically repairs a specific failing clause in a SQL query using SQLGlot AST ma, Parses the error message string to detect which clause is failing.     Returns: (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.26
Nodes (10): SQLErrorClassification, str, SQL Error Taxonomy Pydantic Schemas  Defines the formal representation of SQL sy, Structured classification of a SQL error within the formal error taxonomy., SQLErrorClassification, classify_sql_error(), fallback_classify_error(), SQL Error Taxonomy Classifier Module  Uses LLM-based structured diagnostics to c (+2 more)

### Community 58 - "Community 58"
Cohesion: 0.67
Nodes (3): DO, DO NOT, Important Development Rules

### Community 59 - "Community 59"
Cohesion: 0.18
Nodes (7): Verify that correct_sql handles a successful AST clause repair directly., Verify that correct_sql handles a successful AST clause repair directly., Verify that validate_sql_semantics correctly parses and validates a JSON respons, Verify that validate_sql_semantics correctly parses and validates a JSON respons, Verify that correct_sql falls back to LLM JSON parsing on AST repair failure., Verify that correct_sql falls back to LLM JSON parsing on AST repair failure., TestValidationAndCorrectionMock

### Community 60 - "Community 60"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 3 — Semantic Validation [COMPLETED], Status

### Community 64 - "Community 64"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 6 — Observability & Transparency [COMPLETED], Status

## Knowledge Gaps
- **134 isolated node(s):** `Project Overview`, `Architecture Philosophy`, `Current Architecture`, `Enterprise Architecture Vision`, `Core` (+129 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm()` connect `Community 3` to `Community 0`, `Community 45`, `Community 50`, `Community 23`, `Community 55`, `Community 56`, `Community 57`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `LLMProvider` connect `Community 50` to `Community 1`, `Community 3`, `Community 45`, `Community 47`, `Community 48`, `Community 52`, `Community 53`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `validate_sql_semantics()` connect `Community 23` to `Community 0`, `Community 3`, `Community 55`, `Community 59`, `Community 28`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LLMProvider` (e.g. with `AnthropicProvider` and `Any`) actually correct?**
  _`LLMProvider` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TestLLMProviders` (e.g. with `AnthropicProvider` and `LLMProvider`) actually correct?**
  _`TestLLMProviders` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `OllamaProvider` (e.g. with `LLMProviderFactory` and `Any`) actually correct?**
  _`OllamaProvider` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Project Overview`, `Architecture Philosophy`, `Current Architecture` to the rest of the system?**
  _312 weakly-connected nodes found - possible documentation gaps or missing edges._