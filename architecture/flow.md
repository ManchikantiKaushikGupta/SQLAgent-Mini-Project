# System Workflow

1. User submits natural language query
2. Intent Clarification Agent refines query
3. Query Planning Agent generates structured steps
4. SQL Generation Agent converts plan to SQL
5. Validation & Correction Agent:

   * Validates using SQLGlot
   * Ensures safety
   * Executes query
   * Retries if needed
6. Results are returned to user
