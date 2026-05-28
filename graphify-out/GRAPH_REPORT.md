# Graph Report - SQLAgent-Mini-Project  (2026-05-28)

## Corpus Check
- 50 files · ~116,419 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 436 nodes · 659 edges · 42 communities (36 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad0a3d29`
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
- [[_COMMUNITY_Community 40|Community 40]]

## God Nodes (most connected - your core abstractions)
1. `init_metrics_state()` - 20 edges
2. `get_llm()` - 18 edges
3. `track_latency()` - 15 edges
4. `correct_sql()` - 14 edges
5. `validate_sql_semantics()` - 14 edges
6. `QueryPlan` - 14 edges
7. `SQLAgentState` - 12 edges
8. `run_benchmarks()` - 12 edges
9. `record_correction()` - 12 edges
10. `SchemaRetriever` - 12 edges

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

## Communities (42 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (47): decide_after_execution(), decide_after_semantic_validation(), decide_after_syntax_validation(), node_clarify_intent(), node_correct_sql(), node_execute_sql(), node_query_planning(), node_retrieve_schema() (+39 more)

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (6): str, TestASTRepairEngine, detect_failing_clause(), Parses the error message string to detect which clause is failing.     Returns:, Surgically repairs a specific failing clause in a SQL query using SQLGlot AST ma, repair_sql_clause()

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (20): ndarray, Retrieval Module Initialization, get_schema_retriever(), Any, bool, int, str, FAISS-Based Database Schema Retriever  Dynamically reflects database metadata us (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (33): ChatGoogleGenerativeAI, extract_text(), get_active_callbacks(), get_llm(), str, Returns the list of active callbacks for the current thread., Returns a configured ChatGoogleGenerativeAI instance.      Args:         model:, Safely extracts string content from an LLM response or AIMessage.     Handles st (+25 more)

### Community 4 - "Community 4"
Cohesion: 0.36
Nodes (8): Base, Category, Order, OrderItem, Product, Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema, Review, User

### Community 5 - "Community 5"
Cohesion: 0.22
Nodes (8): Architecture Philosophy, Current Architecture, DO, DO NOT, Final Vision, High Priority Roadmap, Important Development Rules, Recommended Future Architecture

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
Cohesion: 0.08
Nodes (31): bool, str, Any, str, Validation & Correction Pydantic Schemas  Defines structural models for SQL sema, Structured response representing the semantic correctness verification of a gene, Structured response representing the output of the query correction agent., SemanticValidationResult (+23 more)

### Community 24 - "Community 24"
Cohesion: 0.07
Nodes (41): ask_database(), QueryRequest, QueryResponse, FastAPI Routes  Defines endpoints for the SQLAgent application., Takes a natural language query, runs it through the SQLAgent graph,     and retu, Takes a natural language query, runs it through the SQLAgent graph,     and retu, BenchmarkResult, BenchmarkSummary (+33 more)

### Community 28 - "Community 28"
Cohesion: 0.10
Nodes (25): Any, BaseModel, bool, execute_sql_query(), get_db(), str, Database connection and utilities.  Handles PostgreSQL connection setup using SQ, Yields a database session. (+17 more)

### Community 29 - "Community 29"
Cohesion: 0.07
Nodes (26): columns, fk_columns, pk_columns, db_metadata, categories, order_items, orders, products (+18 more)

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (6): Objective, Objective, Objective, PRIORITY 3 — Semantic Validation, Status, Status

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (6): Backend, Core, Current Tech Stack, Frontend, LLM Providers, SQL Tooling

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (11): Architecture & System Design, Completed, Core Pipeline, Correction Workflow, In Progress, Infrastructure, Optimization, Project Overview (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.22
Nodes (9): Add, Metrics To Track, Metrics Tracked, Objective, Objective, PRIORITY 2 — Evaluation Framework, PRIORITY 2 — Evaluation Framework [COMPLETED], Required (+1 more)

### Community 34 - "Community 34"
Cohesion: 0.67
Nodes (3): Objective, PRIORITY 1 — Structured Outputs, Tasks

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (7): Objective, Objective, Objective, PRIORITY 4 — Clause-Level SQL Repair, Status, Status, Status

### Community 36 - "Community 36"
Cohesion: 0.25
Nodes (8): Dashboard Should Show, Objective, Objective, Objective, PRIORITY 6 — Observability & Transparency, PRIORITY 6 — Observability & Transparency [COMPLETED], Status, Status

### Community 37 - "Community 37"
Cohesion: 0.67
Nodes (3): Add, Objective, PRIORITY 5 — Schema Retrieval Layer

### Community 38 - "Community 38"
Cohesion: 0.67
Nodes (3): Current Maturity, Current Project Status, Main Focus Going Forward

### Community 40 - "Community 40"
Cohesion: 0.40
Nodes (5): Objective, Objective, PRIORITY 5 — Schema Retrieval Layer [COMPLETED], Status, Status

## Knowledge Gaps
- **103 isolated node(s):** `int`, `str`, `float`, `ChatGoogleGenerativeAI`, `bool` (+98 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_schema_retriever()` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `correct_sql()` connect `Community 23` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **What connects `int`, `str`, `Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema` to the rest of the system?**
  _204 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08392156862745098 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09247311827956989 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.06951219512195123 - nodes in this community are weakly interconnected._
- **Should `Community 9` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._