"""
Database Models

Define your declarative SQLAlchemy models here if needed for
an API or traditional backend functions. The NL2SQL AI primarily uses
dynamic metadata from db/database.py to construct raw queries, 
but models are useful for ORM mapping when saving history or interacting 
with standard routes.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Example History Model (Optional)
# from sqlalchemy import Column, Integer, String, Text, DateTime
# from datetime import datetime
# 
# class QueryHistory(Base):
#     __tablename__ = "query_history"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     user_query = Column(Text, nullable=False)
#     generated_sql = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
