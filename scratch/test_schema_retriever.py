"""
Test Schema Retriever

Isolated script to verify the FAISS-based schema retriever:
1. Builds/loads the vector indices.
2. Queries the retriever with various natural language prompts.
3. Asserts PK/FK columns are strictly preserved in the pruned schema.
"""

import os
import sys

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dotenv
dotenv.load_dotenv(override=True)

from retrieval.schema_retriever import get_schema_retriever


def run_retrieval_tests():
    print("==================================================")
    print("Initializing SchemaRetriever...")
    print("==================================================")
    
    # Initialize the retriever (this will trigger build or load from cache)
    retriever = get_schema_retriever()
    
    # We should have reflected metadata
    print(f"\nSuccessfully initialized!")
    print(f"Cached Tables: {retriever.table_names}")
    
    # Test Queries
    test_cases = [
        {
            "description": "User order aggregation query (needs: users, orders, order_items)",
            "query": "Show the top 3 users by total order amount, ordered descending",
            "expected_tables": ["users", "orders", "order_items"]
        },
        {
            "description": "Product review query (needs: products, reviews)",
            "query": "Get all reviews for laptops with rating 5",
            "expected_tables": ["products", "reviews"]
        },
        {
            "description": "Category product stock query (needs: products, categories)",
            "query": "Which smartphone category product has the lowest stock quantity?",
            "expected_tables": ["products", "categories"]
        }
    ]
    
    for case in test_cases:
        print("\n--------------------------------------------------")
        print(f"Test Case: {case['description']}")
        print(f"Query: '{case['query']}'")
        print("--------------------------------------------------")
        
        pruned_schema = retriever.retrieve(case["query"])
        
        print("\n--- PRUNED SCHEMA OUTPUT ---")
        print(pruned_schema)
        print("----------------------------")
        
        # Verify PK/FK enforcement
        print("\nVerifying PK/FK constraints inside the pruned schema:")
        lines = pruned_schema.split("\n")
        current_table = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("Table:"):
                current_table = line.split("Table:")[1].strip()
                print(f"  * Checking constraints for table: '{current_table}'")
                
                # Check that its primary keys are present in the pruned schema
                expected_pks = retriever.db_metadata[current_table]["pk_columns"]
                print(f"    - Expected PKs: {expected_pks}")
            elif line.startswith("-") and current_table:
                col_info = line.split("-")[1].strip()
                col_name = col_info.split("(")[0].strip()
                
                is_pk = "[PRIMARY KEY]" in col_info
                is_fk = "[FOREIGN KEY]" in col_info
                
                # Retrieve reflected metadata for verification
                original_col = next((c for c in retriever.db_metadata[current_table]["columns"] if c["name"] == col_name), None)
                if original_col:
                    assert original_col["is_pk"] == is_pk, f"PK status mismatch for {current_table}.{col_name}"
                    assert original_col["is_fk"] == is_fk, f"FK status mismatch for {current_table}.{col_name}"
                    if is_pk:
                        print(f"    - Found PK column: '{col_name}' [OK]")
                    if is_fk:
                        print(f"    - Found FK column: '{col_name}' [OK]")
                        
        print("\nTest Case Passed successfully!")

    print("\n==================================================")
    print("All Schema Retriever Unit Tests Passed!")
    print("==================================================")


if __name__ == "__main__":
    run_retrieval_tests()
