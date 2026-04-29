from db.database import engine, Base, get_schema_string
from db.models import User, Order
from core.graph import build_graph

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database schema:")
    print(get_schema_string())

def run_pipeline(query: str):
    app = build_graph()
    
    print(f"\n--- Running Pipeline for Query: '{query}' ---")
    initial_state = {
        "query": query,
        "retry_count": 0
    }
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    print("\n--- Final Pipeline Output ---")
    print(f"Results: {final_state.get('results')}")
    print(f"Errors: {final_state.get('error')}")

if __name__ == "__main__":
    init_db()
    run_pipeline("Show me all the users who ordered recently.")
