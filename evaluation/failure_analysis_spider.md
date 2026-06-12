# Failure Diagnostic Report — Dataset: SPIDER
**Run ID**: `run_spider_1b3d2d` | **Timestamp**: `2026-06-11T22:19:35.151318`
**Execution Accuracy**: `60.0%` (3/5 passed)

## Executive Failure Breakdown
| Error Category | Number of Failures | Percentage | Description |
| :--- | :--- | :--- | :--- |
| **SchemaError** | 1 | 50.0% | Table or column names referenced that do not exist or mismatch. |
| **SemanticError** | 1 | 50.0% | Logically valid SQL that failed execution comparison against golden reference query. |

## Detailed Failure Diagnostics

### 1. Case: `spider_03` (Category: **SchemaError**)
- **User Query**: *"Find the average price of products in the Electronics department"*
- **Golden Reference SQL**:
  ```sql
  SELECT AVG(p.price) FROM products p JOIN categories c ON p.category_id = c.id WHERE c.department = 'Electronics'
  ```
- **Generated SQL**: *None (Pipeline Crashed)*
- **Diagnostics Failure Message**:
  > [!WARNING]
  > Pipeline Crash: 1 validation error for QueryPlan
filters.0.value
  Field required [type=missing, input_value={'column': 'category_id',...lectronics category ID'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing

### 2. Case: `spider_04` (Category: **SemanticError**)
- **User Query**: *"How many reviews were written for each product? Show product id and name."*
- **Golden Reference SQL**:
  ```sql
  SELECT p.id, p.name, COUNT(r.id) FROM products p LEFT JOIN reviews r ON p.id = r.product_id GROUP BY p.id, p.name
  ```
- **Generated SQL**:
  ```sql
  SELECT products.id, products.name, COUNT(reviews.id) AS review_count FROM products INNER JOIN reviews ON products.id = reviews.product_id GROUP BY products.id, products.name LIMIT 50
  ```
- **Diagnostics Failure Message**:
  > [!WARNING]
  > Row count mismatch: generated returned 40 rows, reference returned 60 rows.
