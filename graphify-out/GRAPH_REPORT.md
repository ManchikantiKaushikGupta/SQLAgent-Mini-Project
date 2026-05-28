# Graph Report - SQLAgent-Mini-Project  (2026-05-28)

## Corpus Check
- 33 files · ~7,943 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 219 nodes · 275 edges · 28 communities (22 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b270deb3`
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

## God Nodes (most connected - your core abstractions)
1. `get_llm()` - 15 edges
2. `QueryPlan` - 13 edges
3. `SQLAgentState` - 11 edges
4. `validate_sql_semantics()` - 8 edges
5. `clarify_intent()` - 8 edges
6. `generate_query_plan()` - 8 edges
7. `generate_sql()` - 8 edges
8. `get_database_schema()` - 7 edges
9. `Current Tech Stack` - 6 edges
10. `Completed` - 6 edges

## Surprising Connections (you probably didn't know these)
- `str` --uses--> `QueryPlan`  [INFERRED]
  features/query_planning/agent.py → schemas/planner.py
- `QueryPlan` --uses--> `QueryPlan`  [INFERRED]
  features/query_planning/agent.py → schemas/planner.py
- `str` --uses--> `QueryPlan`  [INFERRED]
  features/sql_generation/agent.py → schemas/planner.py
- `QueryPlan` --uses--> `QueryPlan`  [INFERRED]
  features/sql_generation/agent.py → schemas/planner.py
- `node_semantic_validate()` --calls--> `validate_sql_semantics()`  [EXTRACTED]
  core/graph.py → features/validation_correction/semantic_validator.py

## Communities (28 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (21): decide_after_execution(), decide_after_semantic_validation(), decide_after_syntax_validation(), node_correct_sql(), node_execute_sql(), node_semantic_validate(), node_validate_sql(), LangGraph Workflow Definition  Connects individual agents into a cohesive cycle, (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.16
Nodes (14): ask_database(), QueryRequest, QueryResponse, FastAPI Routes  Defines endpoints for the SQLAgent application., Takes a natural language query, runs it through the SQLAgent graph,     and retu, build_workflow(), Compiles and returns the LangGraph application., get_database_schema() (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (16): ChatGoogleGenerativeAI, node_sql_generation(), get_llm(), str, Returns a configured ChatGoogleGenerativeAI instance.      Args:         model:, QueryPlan, str, float (+8 more)

### Community 3 - "Community 3"
Cohesion: 0.23
Nodes (11): node_clarify_intent(), bool, str, clarify_intent(), get_matched_vague_terms(), is_ambiguous(), Intent Clarification Agent  Detects and resolves ambiguous natural language quer, Checks whether a user query contains vague or ambiguous terms     that need clar (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.36
Nodes (8): Base, Category, Order, OrderItem, Product, Complex Database Seeder for Presentation  Creates a realistic E-Commerce schema, Review, User

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (43): Add, Architecture Philosophy, Architecture & System Design, Backend, Completed, Core, Core Pipeline, Correction Workflow (+35 more)

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (6): 1. Intent Clarification Agent, 2. Query Planning Agent, 3. SQL Generation Agent, 4. Validation & Correction Agent, Multi-Agent System Design, System Flow

### Community 7 - "Community 7"
Cohesion: 0.43
Nodes (6): str, int, extract_offline(), label_communities(), load_detection(), main()

### Community 8 - "Community 8"
Cohesion: 0.25
Nodes (7): node_query_planning(), QueryPlan, str, generate_query_plan(), Query Planning Agent  Converts a refined natural language query into a structure, Generates a structured, step-by-step SQL query plan from a refined     natural l, Query Planning Agent package.

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (21): 1. Unstructured LLM Outputs, 2. Full SQL Regeneration During Correction, 3. Validation Is Mostly Syntax-Level, 4. No Real Schema Retrieval Layer, 5. Limited Observability, Critical Weaknesses To Address, Current Problem, Current Validation (+13 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (13): Any, BaseModel, LangGraph State Definition  Represents the memory passed between nodes during ex, SQLAgentState, AggregationRequirement, FilterRequirement, JoinRequirement, OrderByRequirement (+5 more)

### Community 24 - "Community 24"
Cohesion: 0.40
Nodes (5): Add, Metrics To Track, Objective, PRIORITY 2 — Evaluation Framework, Required

## Knowledge Gaps
- **63 isolated node(s):** `Project Overview`, `Architecture Philosophy`, `Current Architecture`, `Core`, `LLM Providers` (+58 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm()` connect `Community 2` to `Community 8`, `Community 0`, `Community 3`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `Critical Weaknesses To Address` connect `Community 9` to `Community 5`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `QueryPlan` connect `Community 23` to `Community 8`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `QueryPlan` (e.g. with `SQLAgentState` and `QueryPlan`) actually correct?**
  _`QueryPlan` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Project Overview`, `Architecture Philosophy`, `Current Architecture` to the rest of the system?**
  _95 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13043478260869565 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.12105263157894737 - nodes in this community are weakly interconnected._