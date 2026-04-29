from api.app import app

if __name__ == "__main__":
    import uvicorn
    # Make sure to run uvicorn on the application defined in api.app
    uvicorn.run("api.app:app", host="127.0.0.1", port=8000, reload=True)
    final_state = app.invoke(initial_state)
    
    print("\n--- Final Pipeline Output ---")
    print(f"Results: {final_state.get('results')}")
    print(f"Errors: {final_state.get('error')}")

if __name__ == "__main__":
    init_db()
    run_pipeline("Show me all the users who ordered recently.")
