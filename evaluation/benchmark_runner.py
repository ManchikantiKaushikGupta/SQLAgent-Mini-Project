"""
NL2SQL Evaluation Benchmark Runner

Compiles and executes the LangGraph SQLAgent pipeline against a set of 10 diverse,
gold-standard benchmark cases. Collects detailed performance metrics (accuracy,
latency, retries, and token usage) and generates reports and failure logs.
"""

import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# Ensure project root is in the Python path to run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("evaluation.benchmark_runner")
logger.setLevel(logging.INFO)

from langchain_core.callbacks import BaseCallbackHandler
from core.graph import build_workflow
from db.database import get_database_schema, execute_sql_query
from core.llm import register_thread_callbacks, clear_thread_callbacks
from evaluation.metrics import BenchmarkCase, BenchmarkResult, BenchmarkSummary
from evaluation.execution_accuracy import evaluate_execution_accuracy

# --- Benchmark Suite ---
BENCHMARK_CASES = [
    # --- SIMPLE DIFFICULTY ---
    BenchmarkCase(
        id="case_01",
        query="Show me all premium users",
        reference_sql="SELECT * FROM users WHERE is_premium = true",
        difficulty="simple",
        order_sensitive=False
    ),
    BenchmarkCase(
        id="case_02",
        query="Find all categories in the Electronics department",
        reference_sql="SELECT * FROM categories WHERE department = 'Electronics'",
        difficulty="simple",
        order_sensitive=False
    ),
    BenchmarkCase(
        id="case_03",
        query="Count the total number of products",
        reference_sql="SELECT COUNT(*) FROM products",
        difficulty="simple",
        order_sensitive=False
    ),
    BenchmarkCase(
        id="case_04",
        query="Find all products with an average rating greater than 4.5",
        reference_sql="SELECT name, average_rating FROM products WHERE average_rating > 4.5",
        difficulty="simple",
        order_sensitive=False
    ),
    # --- MEDIUM DIFFICULTY ---
    BenchmarkCase(
        id="case_05",
        query="List the top 5 most expensive products and their category name",
        reference_sql="SELECT p.name AS product_name, p.price, c.name AS category_name FROM products p JOIN categories c ON p.category_id = c.id ORDER BY p.price DESC LIMIT 5",
        difficulty="medium",
        order_sensitive=True
    ),
    BenchmarkCase(
        id="case_06",
        query="How many orders were placed by each user? Show top 5 users.",
        reference_sql="SELECT u.id, u.first_name, u.last_name, COUNT(o.id) AS order_count FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.first_name, u.last_name ORDER BY order_count DESC LIMIT 5",
        difficulty="medium",
        order_sensitive=True
    ),
    BenchmarkCase(
        id="case_07",
        query="Find categories that have products in stock with a total stock quantity of more than 1000 items",
        reference_sql="SELECT c.name, SUM(p.stock_quantity) AS total_stock FROM categories c JOIN products p ON c.id = p.category_id GROUP BY c.id, c.name HAVING SUM(p.stock_quantity) > 1000",
        difficulty="medium",
        order_sensitive=False
    ),
    BenchmarkCase(
        id="case_08",
        query="Find all reviews for products in the Apparel department",
        reference_sql="SELECT r.rating, r.review_text, p.name AS product_name FROM reviews r JOIN products p ON r.product_id = p.id JOIN categories c ON p.category_id = c.id WHERE c.department = 'Apparel'",
        difficulty="medium",
        order_sensitive=False
    ),
    # --- COMPLEX DIFFICULTY ---
    BenchmarkCase(
        id="case_09",
        query="Show the top 3 users by total order items amount, ordered descending",
        reference_sql="SELECT u.id, u.first_name, u.last_name, SUM(oi.quantity * oi.unit_price) AS total_spent FROM users u JOIN orders o ON u.id = o.user_id JOIN order_items oi ON o.id = oi.order_id GROUP BY u.id, u.first_name, u.last_name ORDER BY total_spent DESC LIMIT 3",
        difficulty="complex",
        order_sensitive=True
    ),
    BenchmarkCase(
        id="case_10",
        query="List the names of products that have at least 3 reviews with a rating of 5",
        reference_sql="SELECT p.name, COUNT(r.id) AS review_count FROM products p JOIN reviews r ON p.id = r.product_id WHERE r.rating = 5 GROUP BY p.id, p.name HAVING COUNT(r.id) >= 3",
        difficulty="complex",
        order_sensitive=False
    )
]

class TokenUsageTracker(BaseCallbackHandler):
    """
    LangChain Callback handler to transparently capture token usage.
    """
    def __init__(self):
        super().__init__()
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def on_llm_end(self, response, **kwargs):
        # 1. Check direct llm_output metadata
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            if isinstance(usage, dict):
                self.prompt_tokens += usage.get("prompt_tokens", 0)
                self.completion_tokens += usage.get("completion_tokens", 0)
                self.total_tokens += usage.get("total_tokens", 0)
                return

        # 2. Inspect generations and message response_metadata (Google GenAI specific)
        for generation in response.generations:
            for gen in generation:
                msg = getattr(gen, "message", None)
                if msg and hasattr(msg, "response_metadata"):
                    meta = msg.response_metadata
                    usage = meta.get("token_usage")
                    if usage:
                        if isinstance(usage, dict):
                            self.prompt_tokens += usage.get("prompt_tokens", 0)
                            self.completion_tokens += usage.get("completion_tokens", 0)
                            self.total_tokens += usage.get("total_tokens", 0)
                        else:
                            self.prompt_tokens += getattr(usage, "prompt_tokens", 0)
                            self.completion_tokens += getattr(usage, "completion_tokens", 0)
                            self.total_tokens += getattr(usage, "total_tokens", 0)

def run_benchmarks(
    limit: Optional[int] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None
) -> Tuple[BenchmarkSummary, List[BenchmarkResult]]:
    """
    Orchestrates the execution of all benchmark cases, captures metrics,
    and logs failures.
    """
    if provider:
        os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model

    logger.info("Initializing SQLAgent pipeline...")
    app = build_workflow()
    
    logger.info("Retrieving database schema...")
    schema = get_database_schema()
    
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    start_timestamp = datetime.now().isoformat()
    
    results: List[BenchmarkResult] = []
    
    print(f"\n========================================================")
    print(f"[RUN] SQLAgent Benchmark Run {run_id}")
    print(f"========================================================\n")
    
    cases_to_run = BENCHMARK_CASES
    if limit is not None:
        cases_to_run = BENCHMARK_CASES[:limit]

    for case in cases_to_run:
        print(f"Running [{case.id}] ({case.difficulty}): '{case.query}'")
        
        # Initialize token tracker and register to current thread
        tracker = TokenUsageTracker()
        register_thread_callbacks([tracker])
        
        initial_state = {
            "original_query": case.query,
            "db_schema": schema,
            "refined_query": "",
            "query_plan": "",
            "sql_query": "",
            "error_message": None,
            "retry_count": 0,
            "final_result": None,
            "user_role": "admin"
        }
        
        # Time the execution
        start_time = time.time()
        
        try:
            # Execute with active rate-limiting retries
            max_attempts = 5
            attempt = 1
            final_state = None
            while attempt <= max_attempts:
                try:
                    final_state = app.invoke(initial_state)
                    break
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                        sleep_time = attempt * 12
                        print(f"   [RATE LIMIT] Quota exceeded. Sleeping for {sleep_time}s before retrying (Attempt {attempt}/{max_attempts})...")
                        time.sleep(sleep_time)
                        attempt += 1
                    else:
                        raise e
            
            if final_state is None:
                raise RuntimeError("Failed to execute graph after max rate-limit retries.")
                
            latency = time.time() - start_time
            
            generated_sql = final_state.get("sql_query")
            retry_count = final_state.get("retry_count", 0)
            
            # Evaluate execution accuracy against reference query
            success, explanation, gen_rows, ref_rows = evaluate_execution_accuracy(
                generated_sql=generated_sql,
                reference_sql=case.reference_sql,
                order_sensitive=case.order_sensitive
            )
            
            # Determine correction success metrics
            # It needed correction if retry_count > 0 or if there was a syntax/semantic correction loop
            needed_correction = retry_count > 0
            corrected_successfully = needed_correction and success
            
            # The initial generated SQL is considered valid if the correction loop never had to run
            initial_sql_valid = retry_count == 0
            
            err_msg = final_state.get("error_message") or (explanation if not success else None)
            
            result = BenchmarkResult(
                case_id=case.id,
                query=case.query,
                reference_sql=case.reference_sql,
                generated_sql=generated_sql,
                success=success,
                error_message=err_msg,
                latency_seconds=latency,
                prompt_tokens=tracker.prompt_tokens,
                completion_tokens=tracker.completion_tokens,
                total_tokens=tracker.total_tokens,
                retry_count=retry_count,
                corrected_successfully=corrected_successfully,
                initial_sql_valid=initial_sql_valid,
                expected_rows=len(ref_rows),
                returned_rows=len(gen_rows)
            )
            
        except Exception as e:
            latency = time.time() - start_time
            logger.exception(f"Pipeline crashed for query: {case.query}")
            result = BenchmarkResult(
                case_id=case.id,
                query=case.query,
                reference_sql=case.reference_sql,
                generated_sql=None,
                success=False,
                error_message=f"Pipeline Crash: {str(e)}",
                latency_seconds=latency,
                prompt_tokens=tracker.prompt_tokens,
                completion_tokens=tracker.completion_tokens,
                total_tokens=tracker.total_tokens,
                retry_count=0,
                corrected_successfully=False,
                initial_sql_valid=False,
                expected_rows=0,
                returned_rows=0
            )
            
        finally:
            # Clean up callbacks on this thread
            clear_thread_callbacks()
            
        results.append(result)
        status_symbol = "PASS" if result.success else "FAIL"
        print(f"   => {status_symbol} (Latency: {result.latency_seconds:.2f}s | Tokens: {result.total_tokens} | Retries: {result.retry_count})\n")
        
        # Proactive delay between cases to stay under rate limits
        if case != BENCHMARK_CASES[-1]:
            time.sleep(3)
        
    # --- Aggregate Summary Metrics ---
    total_cases = len(results)
    passed_cases = sum(1 for r in results if r.success)
    failed_cases = total_cases - passed_cases
    execution_accuracy = (passed_cases / total_cases) * 100 if total_cases > 0 else 0.0
    
    avg_latency = sum(r.latency_seconds for r in results) / total_cases if total_cases > 0 else 0.0
    total_tokens = sum(r.total_tokens for r in results)
    avg_tokens = total_tokens / total_cases if total_cases > 0 else 0.0
    
    total_retries = sum(r.retry_count for r in results)
    queries_needing_correction = sum(1 for r in results if r.retry_count > 0)
    queries_corrected_successfully = sum(1 for r in results if r.corrected_successfully)
    
    correction_success_rate = (
        (queries_corrected_successfully / queries_needing_correction) * 100
        if queries_needing_correction > 0
        else 100.0
    )
    
    # Difficulty Breakdown
    diff_stats: Dict[str, Dict[str, Any]] = {}
    for r in results:
        # Find case difficulty
        case_diff = next(c.difficulty for c in BENCHMARK_CASES if c.id == r.case_id)
        if case_diff not in diff_stats:
            diff_stats[case_diff] = {"passed": 0, "total": 0, "accuracy_pct": 0.0}
        diff_stats[case_diff]["total"] += 1
        if r.success:
            diff_stats[case_diff]["passed"] += 1
            
    for k, v in diff_stats.items():
        v["accuracy_pct"] = (v["passed"] / v["total"]) * 100
        
    # Retrieve active provider and model
    from llm.factory import load_config
    config = load_config()
    final_provider = config.get("provider", "gemini")
    final_model = config.get("model", "Unknown")

    summary = BenchmarkSummary(
        run_id=run_id,
        timestamp=start_timestamp,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        execution_accuracy_pct=execution_accuracy,
        average_latency_seconds=avg_latency,
        total_tokens=total_tokens,
        avg_tokens_per_query=avg_tokens,
        total_retries=total_retries,
        queries_needing_correction=queries_needing_correction,
        queries_corrected_successfully=queries_corrected_successfully,
        correction_success_rate_pct=correction_success_rate,
        difficulty_breakdown=diff_stats,
        provider=final_provider,
        model=final_model
    )
    
    return summary, results

def write_reports(summary: BenchmarkSummary, results: List[BenchmarkResult]):
    """
    Saves full run logs to file system and updates failed_queries.json
    """
    eval_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(eval_dir, exist_ok=True)
    
    # 1. Update failed_queries.json
    failed_cases_data = []
    for r in results:
        if not r.success:
            failed_cases_data.append({
                "case_id": r.case_id,
                "query": r.query,
                "reference_sql": r.reference_sql,
                "generated_sql": r.generated_sql,
                "error_message": r.error_message,
                "latency_seconds": r.latency_seconds,
                "retry_count": r.retry_count,
                "tokens_used": r.total_tokens
            })
            
    failed_queries_path = os.path.join(eval_dir, "failed_queries.json")
    with open(failed_queries_path, "w", encoding="utf-8") as f:
        json.dump(failed_cases_data, f, indent=2, ensure_ascii=False)
        
    # 2. Append to general history
    history_path = os.path.join(eval_dir, "run_history.json")
    history_data = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception:
            pass
            
    # Structure full run payload
    run_payload = {
        "summary": summary.model_dump(),
        "results": [r.model_dump() for r in results]
    }
    
    history_data.insert(0, run_payload) # Keep latest runs first
    # Cap history at 20 runs to keep file size reasonable
    history_data = history_data[:20]
    
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Benchmark reports saved to {eval_dir}")

def render_dashboard(summary: BenchmarkSummary, results: List[BenchmarkResult]):
    """
    Prints a rich ANSI console dashboard summarizing the run.
    """
    print(f"\n========================================================")
    print(f"BENCHMARK RUN RESULTS: {summary.run_id}")
    print(f"========================================================")
    print(f"Timestamp:                 {summary.timestamp}")
    print(f"Total Test Cases:          {summary.total_cases}")
    
    accuracy_color = "\033[92m" if summary.execution_accuracy_pct >= 80.0 else "\033[93m" if summary.execution_accuracy_pct >= 50.0 else "\033[91m"
    reset_color = "\033[0m"
    
    print(f"Execution Accuracy:        {accuracy_color}{summary.execution_accuracy_pct:.1f}%{reset_color} ({summary.passed_cases}/{summary.total_cases})")
    print(f"Average Latency:           {summary.average_latency_seconds:.2f} seconds")
    print(f"Total Token Usage:         {summary.total_tokens} (Avg: {summary.avg_tokens_per_query:.0f}/query)")
    print(f"Total Retries Attempted:   {summary.total_retries}")
    print(f"Queries Needing Retry:     {summary.queries_needing_correction}")
    print(f"Correction Success Rate:   {summary.correction_success_rate_pct:.1f}% ({summary.queries_corrected_successfully}/{summary.queries_needing_correction})")
    
    print(f"\n--- Difficulty Breakdown ---")
    for diff, stats in summary.difficulty_breakdown.items():
        print(f"  * {diff.capitalize():10}: {stats['passed']}/{stats['total']} correct ({stats['accuracy_pct']:.1f}%)")
        
    print(f"\n========================================================")
    print(f"DETAILED RESULTS TABLE")
    print(f"========================================================")
    print(f"{'Case ID':8} | {'Difficulty':10} | {'Status':6} | {'Retries':7} | {'Latency':8} | {'NL Query'}")
    print(f"-" * 80)
    
    for r in results:
        status_str = "\033[92mPASS\033[0m" if r.success else "\033[91mFAIL\033[0m"
        # Find case difficulty
        case_diff = next(c.difficulty for c in BENCHMARK_CASES if c.id == r.case_id)
        print(f"{r.case_id:8} | {case_diff:10} | {status_str:6} | {r.retry_count:7} | {r.latency_seconds:6.2f}s | {r.query[:35]}")
    print(f"========================================================\n")

if __name__ == "__main__":
    import argparse
    from typing import Optional
    
    parser = argparse.ArgumentParser(description="NL2SQL Benchmark Suite Runner")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of benchmark cases run."
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Override active LLM provider."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override active LLM model name."
    )
    args = parser.parse_args()
    
    summary, results = run_benchmarks(
        limit=args.limit,
        provider=args.provider,
        model=args.model
    )
    write_reports(summary, results)
    render_dashboard(summary, results)
