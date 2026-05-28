import os
import sys
import logging

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_pipeline_e2e")

from core.graph import build_workflow
from db.database import get_database_schema
from schemas.planner import QueryPlan

def test_e2e_pipeline():
    logger.info("Initializing LangGraph workflow...")
    app = build_workflow()

    logger.info("Fetching database schema...")
    schema = get_database_schema()
    logger.info(f"Database schema fetched. Length: {len(schema)} characters.")

    # Test Query
    query = "Show the top 3 users by total order amount, ordered descending"
    logger.info(f"Original user query: '{query}'")

    initial_state = {
        "original_query": query,
        "db_schema": schema,
        "refined_query": "",
        "query_plan": "",
        "sql_query": "",
        "error_message": None,
        "retry_count": 0,
        "final_result": None
    }

    logger.info("Invoking LangGraph pipeline...")
    final_state = app.invoke(initial_state)

    logger.info("--- Execution Completed ---")
    logger.info(f"Refined Query: '{final_state.get('refined_query')}'")
    
    plan = final_state.get("query_plan")
    logger.info(f"Query Plan Type: {type(plan)}")
    
    if isinstance(plan, QueryPlan):
        logger.info("Success! Query plan is a structured Pydantic QueryPlan object.")
        logger.info(f"Thought Process: {plan.thought_process}")
        logger.info(f"Tables identified: {[t.table_name for t in plan.tables]}")
        logger.info(f"Joins: {plan.joins}")
        logger.info(f"Filters: {plan.filters}")
        logger.info(f"Aggregations: {plan.aggregations}")
        logger.info(f"Group By: {plan.group_by}")
        logger.info(f"Order By: {plan.order_by}")
        logger.info(f"Limit: {plan.limit}")
    else:
        logger.error(f"Failure: Query plan is not a QueryPlan object (got {type(plan)} instead).")
        assert False, "Query plan must be a QueryPlan model instance"

    logger.info(f"Generated SQL: '{final_state.get('sql_query')}'")
    logger.info(f"Pipeline Retry Count: {final_state.get('retry_count')}")
    logger.info(f"Final Execution Error: {final_state.get('error_message')}")
    logger.info(f"Final Execution Result: {final_state.get('final_result')}")

    # Verify if semantic validation was reached
    if final_state.get("error_message") and "Semantic Validation" in final_state["error_message"]:
        logger.info("Semantic validation triggered an error loop successfully!")
    elif not final_state.get("error_message"):
        logger.info("Semantic validation successfully passed and query executed!")

    logger.info("E2E Pipeline Test completed!")

if __name__ == "__main__":
    test_e2e_pipeline()
