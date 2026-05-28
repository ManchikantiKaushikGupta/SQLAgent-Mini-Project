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
* [ ] Add structured validator outputs
* [ ] Add typed correction outputs

---

# PRIORITY 2 — Evaluation Framework

## Objective

Move from demo-based validation to benchmark-driven evaluation.

## Required

evaluation/

### Add

* benchmark_runner.py
* metrics.py
* failed_queries.json
* execution_accuracy.py

### Metrics To Track

* execution accuracy
* correction success rate
* retry count
* latency
* token usage

---

# PRIORITY 3 — Semantic Validation

## Objective

Verify logical correctness, not just syntax correctness.

## Add

* execution-aware validation
* intent alignment checking
* semantic validator stage

---

# PRIORITY 4 — Clause-Level SQL Repair

## Objective

Repair failing SQL components individually.

## Technologies

* SQLGlot AST parsing
* AST patching
* clause-specific correction logic

---

# PRIORITY 5 — Schema Retrieval Layer

## Objective

Scale efficiently to larger schemas.

## Add

* embedding-based retrieval
* schema pruning
* relevant table ranking
* relevant column ranking

---

# PRIORITY 6 — Observability & Transparency

## Objective

Make the entire reasoning pipeline inspectable.

## Dashboard Should Show

* user query
* planner output
* generated SQL
* validation results
* correction attempts
* execution output
* latency
* token usage

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
