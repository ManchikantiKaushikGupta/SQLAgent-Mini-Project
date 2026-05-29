import os
import sys
import unittest
import tempfile
import json
from unittest.mock import MagicMock, patch

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.dataset_loaders import load_dataset
from evaluation.expanded_runner import compile_failure_analysis, write_dataset_reports
from evaluation.metrics import BenchmarkCase, BenchmarkResult, BenchmarkSummary


class TestBenchmarkExpansion(unittest.TestCase):

    def setUp(self):
        self.mock_results = [
            BenchmarkResult(
                case_id="spider_01",
                query="Show premium users",
                reference_sql="SELECT * FROM users WHERE is_premium = true",
                generated_sql="SELECT * FROM users WHERE premium = true",
                success=False,
                error_message="column 'premium' does not exist in relation 'users'",
                latency_seconds=1.2,
                prompt_tokens=150,
                completion_tokens=45,
                total_tokens=195,
                retry_count=1,
                corrected_successfully=False,
                initial_sql_valid=False,
                expected_rows=10,
                returned_rows=0
            ),
            BenchmarkResult(
                case_id="spider_02",
                query="Show categories",
                reference_sql="SELECT * FROM categories",
                generated_sql="SELECT * FROM categories",
                success=True,
                error_message=None,
                latency_seconds=0.8,
                prompt_tokens=100,
                completion_tokens=30,
                total_tokens=130,
                retry_count=0,
                corrected_successfully=False,
                initial_sql_valid=True,
                expected_rows=8,
                returned_rows=8
            )
        ]
        
        self.mock_summary = BenchmarkSummary(
            run_id="run_test_12345",
            timestamp="2026-05-29T22:58:35",
            total_cases=2,
            passed_cases=1,
            failed_cases=1,
            execution_accuracy_pct=50.0,
            average_latency_seconds=1.0,
            total_tokens=325,
            avg_tokens_per_query=162.5,
            total_retries=1,
            queries_needing_correction=1,
            queries_corrected_successfully=0,
            correction_success_rate_pct=0.0,
            difficulty_breakdown={"simple": {"passed": 1, "total": 2, "accuracy_pct": 50.0}}
        )

    def test_load_valid_datasets(self):
        """Verify that load_dataset successfully parses Spider, Spider Realistic, and Spider SYN."""
        for dataset_name in ["spider", "spider_realistic", "spider_syn"]:
            cases = load_dataset(dataset_name)
            self.assertIsInstance(cases, list)
            self.assertEqual(len(cases), 5)
            for case in cases:
                self.assertIsInstance(case, BenchmarkCase)
                self.assertTrue(case.id.startswith(f"{dataset_name.split('_')[0]}"))
                self.assertIsNotNone(case.query)
                self.assertIsNotNone(case.reference_sql)
                self.assertIn(case.difficulty, ["simple", "medium", "complex"])

    def test_load_invalid_dataset_raises_error(self):
        """Verify that load_dataset raises a ValueError for unknown dataset names."""
        with self.assertRaises(ValueError):
            load_dataset("unknown_dataset_name_123")

    def test_compile_failure_analysis_report(self):
        """Verify that compile_failure_analysis categorizes SQL failures and generates markdown diagnostics."""
        report = compile_failure_analysis("spider", self.mock_results, self.mock_summary)
        
        self.assertIn("# Failure Diagnostic Report — Dataset: SPIDER", report)
        self.assertIn("run_test_12345", report)
        self.assertIn("50.0%", report)
        self.assertIn("SchemaError", report) # 'column premium does not exist' should match SchemaError keywords
        self.assertIn("Show premium users", report)
        self.assertIn("column 'premium' does not exist in relation 'users'", report)

    @patch("evaluation.expanded_runner.os.path.dirname")
    def test_write_dataset_reports(self, mock_dirname):
        """Verify that write_dataset_reports successfully serializes JSON metrics and markdown report to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_dirname.return_value = tmpdir
            
            write_dataset_reports(
                dataset_name="spider_test",
                summary=self.mock_summary,
                results=self.mock_results,
                failure_report_md="# Mock Report Content"
            )
            
            # Check failed queries JSON
            failed_json_path = os.path.join(tmpdir, "failed_queries_spider_test.json")
            self.assertTrue(os.path.exists(failed_json_path))
            with open(failed_json_path, "r", encoding="utf-8") as f:
                failed_data = json.load(f)
            self.assertEqual(len(failed_data), 1)
            self.assertEqual(failed_data[0]["case_id"], "spider_01")
            
            # Check run history JSON
            history_json_path = os.path.join(tmpdir, "run_history_spider_test.json")
            self.assertTrue(os.path.exists(history_json_path))
            with open(history_json_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
            self.assertEqual(len(history_data), 1)
            self.assertEqual(history_data[0]["summary"]["run_id"], "run_test_12345")
            
            # Check failure analysis Markdown
            md_path = os.path.join(tmpdir, "failure_analysis_spider_test.md")
            self.assertTrue(os.path.exists(md_path))
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            self.assertEqual(md_content, "# Mock Report Content")


if __name__ == "__main__":
    unittest.main()
