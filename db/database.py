"""
Database connection and utilities.

Handles PostgreSQL connection setup using SQLAlchemy, mapping raw SQL
queries, and fetching database schema context dynamically for the AI.
"""

import os
import threading
from typing import Optional
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

# Thread-safe in-memory cache for reflected database schema
_schema_cache: Optional[str] = None
_schema_cache_lock = threading.Lock()


def get_db():
    """Yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clear_schema_cache() -> None:
    """Clears the reflected database schema cache to force re-reflection on next access."""
    global _schema_cache
    with _schema_cache_lock:
        _schema_cache = None


def get_database_schema() -> str:
    """
    Extracts table names, columns, and data types from the connected PostgreSQL database.
    This string is used by the various AI agents to understand the domain.
    Utilizes a thread-safe in-memory cache to prevent redundant reflection calls.

    Returns:
        A formatted string describing the database schema.
    """
    global _schema_cache
    
    # Fast path without lock acquisition
    if _schema_cache is not None:
        return _schema_cache

    with _schema_cache_lock:
        # Double check lock pattern
        if _schema_cache is not None:
            return _schema_cache

        try:
            # Recreate or clear MetaData to reflect the latest state correctly if required
            metadata.clear()
            metadata.reflect(bind=engine)
            schema_lines = []
            for table_name, table in metadata.tables.items():
                schema_lines.append(f"Table: {table_name}")
                for column in table.columns:
                    schema_lines.append(f"  - {column.name} ({column.type})")
                schema_lines.append("")
            
            if not schema_lines:
                _schema_cache = "No tables found in the database."
            else:
                _schema_cache = "\n".join(schema_lines)
                
            return _schema_cache
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
