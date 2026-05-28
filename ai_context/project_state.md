# Project State

## Project Overview

SQLAgent-Mini-Project is a LangGraph-based modular NL2SQL orchestration framework that converts natural language questions into safe executable SQL queries using staged reasoning, validation, and iterative correction.

The system is designed as a modular reasoning pipeline rather than a fully autonomous AGI-style multi-agent system.

Primary goals:

* Safe SQL generation
* Explainable reasoning
* Structured orchestration
* Reliable correction workflow
* Evaluation-driven development

---

# Architecture Philosophy

The project should prioritize:

* Deterministic orchestration
* Structured reasoning
* Transparent SQL generation
* Modular components
* Minimal hallucination surfaces
* Reliability over unnecessary agent complexity

LLMs should primarily handle:

* reasoning
* ambiguity resolution
* query planning
* semantic understanding

Deterministic code should handle:

* validation
* retries
* schema checking
* SQL parsing
* AST manipulation
* logging
* metrics

---

# Current Architecture

User Query
↓
Intent Clarification
↓
Query Planning
↓
SQL Generation
↓
Validation
↓
SQL Execution
↓
Correction Loop (if needed)
↓
Final SQL Response

---

# Current Tech Stack

## Core

* Python
* LangGraph
* LangChain

## LLM Providers

* OpenAI
* Anthropic

## SQL Tooling

* SQLGlot
* PostgreSQL
* SQLite

## Backend

* FastAPI

## Frontend

* Streamlit

---

# Completed

## Architecture & System Design

* Architecture design finalized
* Tech stack finalized
* Project folder structure setup
* LangGraph workflow setup
* State-based orchestration implemented

## Core Pipeline

* Intent Clarification Agent implementation
* Query Planning Agent implementation
* SQL Generation Agent
* Validation & Correction Agent
* SQL execution workflow

## Validation & Safety

* SQLGlot integration
* SQL syntax validation
* SELECT-only SQL restriction
* Unsafe SQL prevention

## Infrastructure

* PostgreSQL connection setup
* FastAPI backend
* Streamlit UI

---

# In Progress

## Visualization & Transparency

* Query plan visualization
* SQL transparency improvements
* Debug pipeline visibility

## Correction Workflow

* Improved retry strategies
* Better correction logic
* Validation enhancements

## Optimization

* Performance optimization
* Better prompt tuning

---

# Critical Weaknesses To Address

## 1. Unstructured LLM Outputs

Current agents mostly return raw text responses.

### Problem

* difficult debugging
* inconsistent parsing
* unreliable orchestration
* weak evaluation support

### Goal

Move all agent outputs to structured formats using:

* Pydantic
* TypedDict
* JSON schemas

### Target Example

{
"tables": [],
"joins": [],
"filters": [],
"aggregations": [],
"order_by": []
}

---

## 2. Full SQL Regeneration During Correction

### Problem

Correction loop regenerates entire SQL queries instead of fixing specific clauses.

This causes:

* instability
* hallucination propagation
* inconsistent retries

### Goal

Implement clause-level SQL repair using SQL AST manipulation.

Repair only:

* GROUP BY
* WHERE
* JOIN
* LIMIT
* ORDER BY

instead of regenerating complete queries.

---

## 3. Validation Is Mostly Syntax-Level

### Current Validation

* syntax correctness
* SQL safety

### Missing

* semantic correctness
* intent verification
* logical validation

### Goal

Add multi-level validation:

#### Layer 1

Syntax validation

#### Layer 2

Schema validation

#### Layer 3

Semantic validation

Semantic validation should verify:
"Does the generated SQL actually answer the user's question correctly?"

---

## 4. No Real Schema Retrieval Layer

### Current Problem

Entire schema is passed as text.

This does not scale to larger databases.

### Goal

Implement embedding-based schema retrieval.

Suggested technologies:

* FAISS
* ChromaDB

Only relevant tables and columns should be retrieved before planning.

---

## 5. Limited Observability

### Missing Features

* structured logs
* stage-wise metrics
* token analytics
* latency tracking
* correction tracing

### Goal

Add full observability dashboard.

---

# High Priority Roadmap

# PRIORITY 1 — Structured Outputs

## Objective

Eliminate fragile free-text reasoning outputs.

## Tasks

* [x] Introduce Pydantic schemas (added `schemas/planner.py`)
* [x] Add structured planner outputs (refactored Query Planning Agent to return Pydantic `QueryPlan` with robust validation-first parsing)
* [x] Add structured validator outputs (centralized validation schemas under `schemas/validation.py` and refactored semantic validator agent)
* [x] Add typed correction outputs (refactored the SQL correction fallback loop to enforce structured JSON prompts parsed and validated via Pydantic)


---

# PRIORITY 2 — Evaluation Framework [COMPLETED]

## Objective

Move from demo-based validation to benchmark-driven evaluation.

## Status
* [x] **Pydantic metrics schemas** (added `evaluation/metrics.py` defining standard schemas for `BenchmarkCase`, `BenchmarkResult`, and `BenchmarkSummary`)
* [x] **Semantic cell comparison engine** (added `evaluation/execution_accuracy.py` implementing robust, alias-independent result-set cell matching)
* [x] **Rate-limit resilient benchmark suite** (added `evaluation/benchmark_runner.py` defining 10 diverse e-commerce test cases with active proactive and reactive backoff retry mechanisms)
* [x] **Observability logs** (logs failures to `evaluation/failed_queries.json` and histories to `evaluation/run_history.json`)

## Metrics Tracked

* **Execution accuracy** (percentage of queries yielding semantically identical rows to ground-truth reference SQL)
* **Correction success rate** (efficiency of the correction loop when correcting initially invalid queries)
* **Retry count** (total correction loop iterations executed per query and in aggregate)
* **Latency** (latency from graph invocation to final result across stages)
* **Token usage** (transparent prompt, completion, and total token usage tracked via thread-local LangChain callbacks in `core/llm.py`)

---

# PRIORITY 3 — Semantic Validation

## Objective

Verify logical correctness, not just syntax correctness.

## Status

* [x] execution-aware validation (checks returned row data against original user intent)
* [x] intent alignment checking (compares generated query constraints with refined intent)
* [x] semantic validator stage (integrated `semantic_validate` node inside `core/graph.py` with correction loop routing)

---

# PRIORITY 4 — Clause-Level SQL Repair

## Objective

Repair failing SQL components individually.

## Status

* [x] SQLGlot AST parsing (parses original failed SQL into an AST object for precise manipulation)
* [x] AST patching (deterministically grafts corrected clauses into the original AST)
* [x] clause-specific correction logic (prompts LLM for only the failing clause e.g. WHERE, GROUP BY, JOIN, LIMIT, ORDER BY)

---

# PRIORITY 5 — Schema Retrieval Layer [COMPLETED]

## Objective

Scale efficiently to larger database schemas.

## Status

* [x] **FAISS vector indexing**: added `retrieval/` module leveraging `faiss-cpu` and `models/gemini-embedding-2` for dual-layer table and column vector indices.
* [x] **Structural preservation**: automatically retains all Primary Key and Foreign Key columns in retrieved tables to guarantee downstream JOIN capabilities.
* [x] **Dynamic column ranking**: uses Unit Inner-Product Cosine Similarity in-memory to select the top $M$ most relevant data columns per table.
* [x] **LangGraph integration**: added `retrieve_schema` node intercepts and overrides the `db_schema` state variable seamlessly, maintaining complete backward compatibility with all subsequent agents.
* [x] **Smart caching**: serializes FAISS index binaries and structural metadata to disk (`retrieval/index_cache/`) and holds retriever singleton in memory, avoiding redundant API costs.

---

# PRIORITY 6 — Observability & Transparency [COMPLETED]

## Objective

Make the entire reasoning pipeline inspectable.

## Status

* [x] **Reusable Telemetry Module**: added `observability/` package defining structured, clean context managers, callbacks, and diagnostic recorders.
* [x] **Stage-wise Latency Timeline**: measures step durations for all graph nodes and stores them in state telemetries.
* [x] **Thread-safe Token Accumulator**: thread-local callback aggregated prompt, completion, and total tokens safely.
* [x] **Diagnostic Audits**: records safety AST validations (SQLGlot) and execution-aware semantic intent validations.
* [x] **SQL Correction Trails**: chronological logging captures clause grafts and repair loops.
* [x] **Interactive Observability Dashboard**: Streamlit tabbed UI (`📊 Observability Dashboard`) displays latency bar charts, token lists, planner diagrams, validation audits, and correction histories.

---

# Recommended Future Architecture

User Query
↓
Schema Retriever
↓
Planner Agent (Structured JSON Output)
↓
SQL Generator
↓
SQL AST Validator
↓
Execution Engine
↓
Semantic Validator
↓
Clause-Level Repair Engine
↓
Final SQL

---

# Important Development Rules

## DO

* Prefer deterministic logic over prompt-heavy workflows
* Keep orchestration modular
* Track metrics and evaluation results
* Use structured outputs
* Minimize hallucination surfaces

## DO NOT

* Add unnecessary agents
* Create overly complex prompt chains
* Delegate deterministic tasks entirely to LLMs
* Oversell the project as AGI/autonomous intelligence

---

# Current Project Status

## Current Maturity

Advanced student-level AI systems project with strong architectural foundations.

## Main Focus Going Forward

The project should now focus on:

* structure
* evaluation
* semantic correctness
* observability
* reliability

instead of increasing agent count or orchestration complexity.

---

# Final Vision

The final system should become:

"A reliable, explainable, evaluation-driven NL2SQL orchestration framework combining structured reasoning, deterministic validation, semantic correctness checking, and iterative SQL repair."
