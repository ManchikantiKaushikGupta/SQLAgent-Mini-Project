import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv(override=True)

# Use SQLite for local development if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_schema_string() -> str:
    """Returns the database schema as a string format for the LLM."""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    schema_str = ""
    for table_name, table in metadata.tables.items():
        schema_str += f"Table: {table_name}\n"
        schema_str += "Columns:\n"
        for column in table.columns:
            schema_str += f" - {column.name} ({column.type})\n"
        schema_str += "\n"
    return schema_str
