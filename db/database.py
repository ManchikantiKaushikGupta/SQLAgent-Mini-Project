"""
Database connection and utilities.

Handles PostgreSQL connection setup using SQLAlchemy, mapping raw SQL
queries, and fetching database schema context dynamically for the AI.
"""

import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build the DB URL, fallback to local test DB or placeholder if unconfigured
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/sqlagent"
)

# Initialize engine and session
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()


def get_db():
    """Yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_database_schema() -> str:
    """
    Extracts table names, columns, and data types from the connected PostgreSQL database.
    This string is used by the various AI agents to understand the domain.

    Returns:
        A formatted string describing the database schema.
    """
    try:
        metadata.reflect(bind=engine)
        schema_lines = []
        for table_name, table in metadata.tables.items():
            schema_lines.append(f"Table: {table_name}")
            for column in table.columns:
                schema_lines.append(f"  - {column.name} ({column.type})")
            schema_lines.append("")
        
        if not schema_lines:
            return "No tables found in the database."
        
        return "\n".join(schema_lines)
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"


def execute_sql_query(query: str) -> list[dict]:
    """
    Executes a raw SQL SELECT query against the PostgreSQL database safely.
    
    Args:
        query: The raw SQL string (must be a SELECT statement).
        
    Returns:
        A list of dictionaries representing the fetched rows.
        
    Raises:
        Exception if the exact query syntax or execution fails on the database.
    """
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed for execution.")
        
    with engine.connect() as connection:
        result = connection.execute(text(query))
        
        # Convert row tuples into dictionaries
        keys = result.keys()
        rows = [dict(zip(keys, row)) for row in result.fetchall()]
        return rows
