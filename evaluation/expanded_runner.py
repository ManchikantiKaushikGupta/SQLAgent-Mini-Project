"""
Expanded NL2SQL Benchmark Runner

Orchestrates multi-dataset benchmark executions (Spider, Spider Realistic, Spider SYN).
Evaluates execution accuracy, correction success rate, latency, and token cost, and compiles
automated, detailed failure diagnostic analysis reports.
"""

import os
import sys
import json
import time
import uuid
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Ensure project root is in the Python path to run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("evaluation.expanded_runner")
logger.setLevel(logging.INFO)

from langchain_core.callbacks import BaseCallbackHandler
from core.graph import build_workflow
from db.database import get_database_schema
from core.llm import register_thread_callbacks, clear_thread_callbacks
from evaluation.metrics import BenchmarkCase, BenchmarkResult, BenchmarkSummary
from evaluation.execution_accuracy import evaluate_execution_accuracy
from evaluation.dataset_loaders import load_dataset


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


def run_dataset_benchmark(
    dataset_name: str,
    cases: List[BenchmarkCase],
    app: Any,
    schema: str
) -> Tuple[BenchmarkSummary, List[BenchmarkResult]]:
    """
    Executes the agent pipeline against a single loaded dataset's test cases.
    """
    run_id = f"run_{dataset_name}_{uuid.uuid4().hex[:6]}"
    start_timestamp = datetime.now().isoformat()
    
    results: List[BenchmarkResult] = []
    
    print(f"\n" + "=" * 65)
    print(f"[RUNNING] Dataset '{dataset_name}' ({len(cases)} cases) | Run ID: {run_id}")
    print("=" * 65 + "\n")
    
    for case in cases:
        print(f"Executing [{case.id}] ({case.difficulty}): '{case.query}'")
        
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
            "final_result": None
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
            needed_correction = retry_count > 0
            corrected_successfully = needed_correction and success
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
        if case != cases[-1]:
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
        case_diff = next(c.difficulty for c in cases if c.id == r.case_id)
        if case_diff not in diff_stats:
            diff_stats[case_diff] = {"passed": 0, "total": 0, "accuracy_pct": 0.0}
        diff_stats[case_diff]["total"] += 1
        if r.success:
            diff_stats[case_diff]["passed"] += 1
            
    for k, v in diff_stats.items():
        v["accuracy_pct"] = (v["passed"] / v["total"]) * 100
        
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
        difficulty_breakdown=diff_stats
    )
    
    return summary, results


def compile_failure_analysis(
    dataset_name: str,
    results: List[BenchmarkResult],
    summary: BenchmarkSummary
) -> str:
    """
    Analyzes failed queries and generates a rich, diagnostic Markdown report.
    """
    failed_results = [r for r in results if not r.success]
    
    report_lines = []
    report_lines.append(f"# Failure Diagnostic Report — Dataset: {dataset_name.upper()}")
    report_lines.append(f"**Run ID**: `{summary.run_id}` | **Timestamp**: `{summary.timestamp}`")
    report_lines.append(f"**Execution Accuracy**: `{summary.execution_accuracy_pct:.1f}%` ({summary.passed_cases}/{summary.total_cases} passed)")
    report_lines.append("")
    report_lines.append("## Executive Failure Breakdown")
    
    if not failed_results:
        report_lines.append("> [!NOTE]")
        report_lines.append("> **Zero Failures Encountered!** The SQLAgent pipeline executed perfectly across all test cases.")
        return "\n".join(report_lines)
        
    # Analyze error categories from the error messages
    error_patterns = {
        "SchemaError": ["column", "table", "relation", "alias", "schema"],
        "JoinError": ["join", "on clause", "ambiguous"],
        "AggregationError": ["group by", "aggregate", "non-aggregated"],
        "FilterError": ["where", "filter", "operator", "syntax for type", "invalid input syntax"],
        "LimitError": ["limit", "offset"],
        "SemanticError": ["row count mismatch", "data cells do not match", "semantic validation error", "semantic validation exception"]
    }
    
    classification_counts = {k: 0 for k in error_patterns.keys()}
    classification_counts["UnknownError"] = 0
    
    failed_analyses = []
    for r in failed_results:
        matched = False
        err_msg = (r.error_message or "").lower()
        
        # Try to identify category
        for cat, keywords in error_patterns.items():
            if any(kw in err_msg for kw in keywords):
                classification_counts[cat] += 1
                r_cat = cat
                matched = True
                break
        if not matched:
            classification_counts["UnknownError"] += 1
            r_cat = "UnknownError"
            
        failed_analyses.append((r, r_cat))
        
    # Render table of categories
    report_lines.append("| Error Category | Number of Failures | Percentage | Description |")
    report_lines.append("| :--- | :--- | :--- | :--- |")
    for cat, count in classification_counts.items():
        if count > 0:
            pct = (count / len(failed_results)) * 100
            desc = {
                "SchemaError": "Table or column names referenced that do not exist or mismatch.",
                "JoinError": "Missing join conditions or invalid table joining logic.",
                "AggregationError": "Invalid grouping or missing aggregated fields.",
                "FilterError": "Syntactically invalid filters or type coercion failures.",
                "LimitError": "Incorrect limit rows count parameter.",
                "SemanticError": "Logically valid SQL that failed execution comparison against golden reference query.",
                "UnknownError": "General crash or unclassified syntax error."
            }.get(cat, "")
            report_lines.append(f"| **{cat}** | {count} | {pct:.1f}% | {desc} |")
            
    report_lines.append("")
    report_lines.append("## Detailed Failure Diagnostics")
    report_lines.append("")
    
    for idx, (r, r_cat) in enumerate(failed_analyses):
        report_lines.append(f"### {idx+1}. Case: `{r.case_id}` (Category: **{r_cat}**)")
        report_lines.append(f"- **User Query**: *\"{r.query}\"*")
        report_lines.append(f"- **Golden Reference SQL**:")
        report_lines.append(f"  ```sql\n  {r.reference_sql}\n  ```")
        
        if r.generated_sql:
            report_lines.append(f"- **Generated SQL**:")
            report_lines.append(f"  ```sql\n  {r.generated_sql}\n  ```")
        else:
            report_lines.append("- **Generated SQL**: *None (Pipeline Crashed)*")
            
        report_lines.append(f"- **Diagnostics Failure Message**:")
        report_lines.append(f"  > [!WARNING]")
        report_lines.append(f"  > {r.error_message}")
        report_lines.append("")
        
    return "\n".join(report_lines)


def write_dataset_reports(
    dataset_name: str,
    summary: BenchmarkSummary,
    results: List[BenchmarkResult],
    failure_report_md: str
):
    """
    Persists evaluation runs to disk inside the /evaluation directory.
    """
    eval_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Save failed cases to failed_queries_<dataset>.json
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
            
    failed_path = os.path.join(eval_dir, f"failed_queries_{dataset_name}.json")
    with open(failed_path, "w", encoding="utf-8") as f:
        json.dump(failed_cases_data, f, indent=2, ensure_ascii=False)
        
    # 2. Append history to run_history_<dataset>.json
    history_path = os.path.join(eval_dir, f"run_history_{dataset_name}.json")
    history_data = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception:
            pass
            
    run_payload = {
        "summary": summary.model_dump(),
        "results": [r.model_dump() for r in results]
    }
    history_data.insert(0, run_payload)
    history_data = history_data[:20]
    
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)
        
    # 3. Write human-readable failure report
    report_path = os.path.join(eval_dir, f"failure_analysis_{dataset_name}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(failure_report_md)
        
    logger.info(f"Saved JSON metrics and Markdown reports to: {eval_dir}")


def print_summary_dashboard(summaries: Dict[str, BenchmarkSummary]):
    """
    Renders an aggregate summary dashboard of all evaluated datasets in the terminal.
    """
    print("\n" + "=" * 65)
    print("NL2SQL EXPANDED BENCHMARK AGGREGATE SUMMARY")
    print("=" * 65)
    
    reset_color = "\033[0m"
    
    print(f"{'Dataset':20} | {'Cases':5} | {'Passed':6} | {'Accuracy':10} | {'Retries':7} | {'Avg Latency':11}")
    print("-" * 75)
    
    for name, summary in summaries.items():
        accuracy_color = "\033[92m" if summary.execution_accuracy_pct >= 80.0 else "\033[93m" if summary.execution_accuracy_pct >= 50.0 else "\033[91m"
        print(
            f"{name:20} | "
            f"{summary.total_cases:5} | "
            f"{summary.passed_cases:6} | "
            f"{accuracy_color}{summary.execution_accuracy_pct:8.1f}%{reset_color} | "
            f"{summary.total_retries:7} | "
            f"{summary.average_latency_seconds:10.2f}s"
        )
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="NL2SQL Expanded Benchmark Suite Runner")
    parser.add_argument(
        "--dataset",
        choices=["spider", "spider_realistic", "spider_syn", "all"],
        default="spider",
        help="Select which benchmark dataset to execute against (default: spider)."
    )
    args = parser.parse_args()
    
    print("Initializing LLM pipelines and fetching schemas...")
    app = build_workflow()
    schema = get_database_schema()
    
    datasets_to_run = []
    if args.dataset == "all":
        datasets_to_run = ["spider", "spider_realistic", "spider_syn"]
    else:
        datasets_to_run = [args.dataset]
        
    summaries = {}
    
    for dataset in datasets_to_run:
        try:
            cases = load_dataset(dataset)
            summary, results = run_dataset_benchmark(dataset, cases, app, schema)
            
            # Compile failure diagnostics
            failure_md = compile_failure_analysis(dataset, results, summary)
            
            # Persist reports
            write_dataset_reports(dataset, summary, results, failure_md)
            
            summaries[dataset] = summary
            
            # Render a summary of the individual run
            print(f"Dataset '{dataset}' Run Complete. Accuracy: {summary.execution_accuracy_pct:.1f}%")
            
        except Exception as err:
            logger.exception(f"Failed to execute benchmark run for dataset: {dataset}. Err: {err}")
            
    # Print the aggregate leaderboard
    if summaries:
        print_summary_dashboard(summaries)


if __name__ == "__main__":
    main()
