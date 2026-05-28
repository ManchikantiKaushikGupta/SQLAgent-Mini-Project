# Graph Report - SQLAgent-Mini-Project  (2026-05-28)

## Corpus Check
- 51 files · ~116,423 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 395 nodes · 613 edges · 34 communities (27 shown, 7 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8569d5a1`
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
- [[_COMMUNITY_Community 32|Community 32]]

## God Nodes (most connected - your core abstractions)
1. `init_metrics_state()` - 20 edges
2. `get_llm()` - 18 edges
3. `track_latency()` - 15 edges
4. `correct_sql()` - 13 edges
5. `QueryPlan` - 13 edges
6. `SQLAgentState` - 12 edges
7. `run_benchmarks()` - 12 edges
8. `SchemaRetriever` - 12 edges
9. `SQLCorrectionResult` - 12 edges
10. `validate_sql_semantics()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `SQLAgentState` --uses--> `QueryPlan`  [INFERRED]
  core/state.py → schemas/planner.py
- `str` --uses--> `QueryPlan`  [INFERRED]
  features/sql_generation/agent.py → schemas/planner.py
- `QueryPlan` --uses--> `QueryPlan`  [INFERRED]
  features/sql_generation/agent.py → schemas/planner.py
- `bool` --uses--> `SQLCorrectionResult`  [INFERRED]
  features/validation_correction/agent.py → schemas/validation.py
- `SQLCorrectionResult` --uses--> `SQLCorrectionResult`  [INFERRED]
  features/validation_correction/agent.py → schemas/validation.py

## Communities (34 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (35): decide_after_execution(), decide_after_semantic_validation(), decide_after_syntax_validation(), node_clarify_intent(), node_correct_sql(), node_execute_sql(), node_query_planning(), node_retrieve_schema() (+27 more)

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (6): str, TestASTRepairEngine, detect_failing_clause(), Parses the error message string to detect which clause is failing.     Returns:, Surgically repairs a specific failing clause in a SQL query using SQLGlot AST ma, repair_sql_clause()

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (20): ndarray, Retrieval Module Initialization, get_schema_retriever(), Any, bool, int, str, FAISS-Based Database Schema Retriever  Dynamically reflects database metadata us (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (34): ChatGoogleGenerativeAI, extract_text(), get_active_callbacks(), get_llm(), str, Returns the list of active callbacks for the current thread., Returns a configured ChatGoogleGenerativeAI instance.      Args:         model:, Safely extracts string content from an LLM response or AIMessage.     Handles st (+26 more)

### Community 4 - "Community 4"
Cohesion: 0.36
Nodes (8): Base, Category, Order, OrderItem, Product, Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema, Review, User

### Community 5 - "Community 5"
Cohesion: 0.26
Nodes (8): Any, BaseModel, AggregationRequirement, FilterRequirement, JoinRequirement, OrderByRequirement, Any, TableRequirement

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
Cohesion: 0.09
Nodes (36): ask_database(), QueryRequest, QueryResponse, FastAPI Routes  Defines endpoints for the SQLAgent application., Takes a natural language query, runs it through the SQLAgent graph,     and retu, BenchmarkResult, BenchmarkSummary, build_workflow() (+28 more)

### Community 28 - "Community 28"
Cohesion: 0.17
Nodes (17): bool, execute_sql_query(), get_db(), str, Database connection and utilities.  Handles PostgreSQL connection setup using SQ, Yields a database session., Executes a raw SQL SELECT query against the PostgreSQL database safely., compare_results() (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.07
Nodes (26): columns, fk_columns, pk_columns, db_metadata, categories, order_items, orders, products (+18 more)

### Community 32 - "Community 32"
Cohesion: 0.04
Nodes (47): Architecture Philosophy, Architecture & System Design, Backend, Completed, Core, Core Pipeline, Correction Workflow, Current Architecture (+39 more)

## Knowledge Gaps
- **87 isolated node(s):** `liveServer.settings.port`, `Project Overview`, `Architecture Philosophy`, `Current Architecture`, `Core` (+82 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_schema_retriever()` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `correct_sql()` connect `Community 23` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **What connects `liveServer.settings.port`, `Project Overview`, `Architecture Philosophy` to the rest of the system?**
  _171 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.12550607287449392 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09247311827956989 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.07317073170731707 - nodes in this community are weakly interconnected._
- **Should `Community 9` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._