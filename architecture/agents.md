# Multi-Agent System Design

## 1. Intent Clarification Agent

Purpose:

* Handle ambiguous user queries

Input:

* Raw user query

Output:

* Refined query

Responsibilities:

* Detect vague terms (e.g., "top", "best")
* Ask clarification or refine automatically
* Pass clean query forward

---

## 2. Query Planning Agent

Purpose:

* Convert user intent into structured steps

Input:

* Refined query
* Database schema

Output:

* Step-by-step query plan (text)

Responsibilities:

* Identify tables
* Identify joins
* Identify filters
* Identify aggregation
* Create ordered execution steps

---

## 3. SQL Generation Agent

Purpose:

* Convert query plan into SQL

Input:

* Query plan
* Schema

Output:

* SQL query

Responsibilities:

* Generate correct SELECT statements
* Add joins and conditions
* Apply GROUP BY, ORDER BY, LIMIT

---

## 4. Validation & Correction Agent

Purpose:

* Ensure SQL is safe and correct

Input:

* SQL query

Output:

* Final executable SQL

Responsibilities:

* Validate SQL using SQLGlot
* Block unsafe queries (DROP, DELETE, ALTER)
* Execute query
* If error:

  * analyze error
  * regenerate SQL
  * retry (max 2–3 times)

---

# System Flow

User Query
→ Intent Clarification
→ Query Planning
→ SQL Generation
→ Validation & Correction
→ Database Execution
→ Result Output
