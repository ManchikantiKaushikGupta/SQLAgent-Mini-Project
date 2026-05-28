"""
FAISS-Based Database Schema Retriever

Dynamically reflects database metadata using SQLAlchemy, indexes tables and
columns into local FAISS vector stores using Google Generative AI embeddings,
and prunes the schema to only expose relevant context to the Query Planner agent.
"""

import os
import json
import logging
import faiss
import numpy as np
from typing import Dict, List, Any, Optional, Set
from sqlalchemy import inspect
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from db.database import engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

logger = logging.getLogger("SQLAgent.Retrieval")
logger.setLevel(logging.INFO)

# Setup basic logging handler if not configured
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class SchemaRetriever:
    """
    Reflects the database schema and performs embedding-based retrieval of 
    relevant tables and columns to minimize LLM context size and hallucination.
    """
    def __init__(
        self,
        embedding_model_name: str = "models/gemini-embedding-2",
        top_k_tables: int = 3,
        top_m_columns: int = 4,
        cache_dir: str = "retrieval/index_cache"
    ):
        self.top_k_tables = top_k_tables
        self.top_m_columns = top_m_columns
        self.cache_dir = os.path.abspath(cache_dir)
        
        # Initialize Google GenAI Embeddings
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please configure it in your .env file.")
            
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            google_api_key=api_key
        )
        
        # Core State
        self.db_metadata: Dict[str, Any] = {}
        self.table_names: List[str] = []
        self.table_index: Optional[faiss.IndexFlatIP] = None
        self.column_embeddings: Dict[str, Dict[str, List[float]]] = {} # Map: table_name -> column_name -> list[float]
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Try to load existing indices, otherwise build them
        if self._indices_exist():
            try:
                self.load_indices()
            except Exception as e:
                logger.warning(f"Failed to load cached FAISS indices: {e}. Rebuilding...")
                self.build_and_cache()
        else:
            logger.info("No cached FAISS indices found. Initializing and building indices...")
            self.build_and_cache()

    def _indices_exist(self) -> bool:
        """Checks if index files exist in the cache directory."""
        files = ["table_index.bin", "metadata.json", "column_embeddings.json"]
        return all(os.path.exists(os.path.join(self.cache_dir, f)) for f in files)

    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalizes vectors to unit length for Cosine Similarity inside IndexFlatIP."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0 # Prevent division by zero
        return vectors / norms

    def _extract_db_metadata(self) -> Dict[str, Any]:
        """
        Uses SQLAlchemy inspector to reflect tables, columns, primary keys, 
        and foreign keys from the database in a fully deterministic way.
        """
        logger.info("Reflecting database metadata via SQLAlchemy...")
        inspector = inspect(engine)
        db_metadata = {}
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_cols = set(pk_constraint.get("constrained_columns", []) or [])
            
            fk_info = inspector.get_foreign_keys(table_name)
            fk_cols = set()
            for fk in fk_info:
                for col in fk.get("constrained_columns", []):
                    fk_cols.add(col)
                    
            db_metadata[table_name] = {
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "is_pk": col["name"] in pk_cols,
                        "is_fk": col["name"] in fk_cols
                    }
                    for col in columns
                ],
                "pk_columns": list(pk_cols),
                "fk_columns": list(fk_cols)
            }
            
        logger.info(f"Reflected {len(db_metadata)} tables from database.")
        return db_metadata

    def build_and_cache(self) -> None:
        """
        Extracts DB metadata, generates semantic documents, computes embeddings, 
        builds FAISS indices, and saves everything to disk.
        """
        logger.info("Starting schema index build...")
        self.db_metadata = self._extract_db_metadata()
        self.table_names = list(self.db_metadata.keys())
        
        if not self.table_names:
            logger.warning("No tables found in the database. Vector indices will remain empty.")
            return

        # 1. Build Table Documents & Embeddings
        table_docs = []
        for table_name, details in self.db_metadata.items():
            col_list = ", ".join([f"{c['name']} ({c['type']})" for c in details["columns"]])
            doc = f"Table: {table_name}\nColumns: {col_list}"
            table_docs.append(doc)
            
        logger.info(f"Embedding {len(table_docs)} table schema descriptions...")
        raw_table_embs = np.array([self.embeddings_model.embed_query(doc) for doc in table_docs], dtype=np.float32)
        norm_table_embs = self._normalize_vectors(raw_table_embs)
        
        # Build Table FAISS Index
        dimension = norm_table_embs.shape[1]
        self.table_index = faiss.IndexFlatIP(dimension)
        self.table_index.add(norm_table_embs)

        # 2. Build Column Documents & Embeddings
        column_docs = []
        column_keys = [] # list of (table_name, col_name)
        
        for table_name, details in self.db_metadata.items():
            for col in details["columns"]:
                pk_flag = " [PRIMARY KEY]" if col["is_pk"] else ""
                fk_flag = " [FOREIGN KEY]" if col["is_fk"] else ""
                doc = f"Table: {table_name}, Column: {col['name']} ({col['type']}){pk_flag}{fk_flag}"
                column_docs.append(doc)
                column_keys.append((table_name, col["name"]))
                
        logger.info(f"Embedding {len(column_docs)} column descriptions...")
        raw_column_embs = np.array([self.embeddings_model.embed_query(doc) for doc in column_docs], dtype=np.float32)
        
        # Populate precomputed column embeddings map
        self.column_embeddings = {t: {} for t in self.table_names}
        for idx, (t_name, col_name) in enumerate(column_keys):
            self.column_embeddings[t_name][col_name] = raw_column_embs[idx].tolist()
            
        # Save indices to disk
        self.save_indices()
        logger.info("Schema indices successfully built and cached to disk.")

    def save_indices(self) -> None:
        """Saves current indices and reflected metadata to local cache directory."""
        if self.table_index is None:
            raise ValueError("Cannot save empty indices.")
            
        # Save FAISS Table Index
        table_index_path = os.path.join(self.cache_dir, "table_index.bin")
        faiss.write_index(self.table_index, table_index_path)
        
        # Save structural Metadata JSON
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        meta_payload = {
            "table_names": self.table_names,
            "db_metadata": self.db_metadata
        }
        with open(metadata_path, "w") as f:
            json.dump(meta_payload, f, indent=2)
            
        # Save Precomputed Column Embeddings JSON
        column_embs_path = os.path.join(self.cache_dir, "column_embeddings.json")
        with open(column_embs_path, "w") as f:
            json.dump(self.column_embeddings, f)
            
        logger.info("Indices and metadata successfully serialized to disk.")

    def load_indices(self) -> None:
        """Loads indices and metadata from the local cache directory."""
        logger.info(f"Loading schema retrieval cache from: {self.cache_dir}")
        
        # Load FAISS Table Index
        table_index_path = os.path.join(self.cache_dir, "table_index.bin")
        self.table_index = faiss.read_index(table_index_path)
        
        # Load Metadata JSON
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        with open(metadata_path, "r") as f:
            meta_payload = json.load(f)
            self.table_names = meta_payload["table_names"]
            self.db_metadata = meta_payload["db_metadata"]
            
        # Load Column Embeddings JSON
        column_embs_path = os.path.join(self.cache_dir, "column_embeddings.json")
        with open(column_embs_path, "r") as f:
            self.column_embeddings = json.load(f)
            
        logger.info(f"Indices loaded successfully. Total tables cached: {len(self.table_names)}.")

    def retrieve(self, query: str) -> str:
        """
        Executes embedding similarity query over table indices and filters column 
        relevance. Formats and returns a highly pruned schema block.
        
        Args:
            query: The user query (e.g. refined or original).
            
        Returns:
            A formatted schema string containing only relevant tables and columns.
        """
        if not self.table_names or self.table_index is None:
            logger.warning("Retrieval called with empty indexes.")
            return "No tables available in the database schema."
            
        logger.info(f"Retrieving relevant schema for query: '{query}'")
        
        # 1. Embed query
        query_emb = np.array(self.embeddings_model.embed_query(query), dtype=np.float32).reshape(1, -1)
        query_emb_norm = self._normalize_vectors(query_emb)[0]
        
        # 2. Find top K tables using FAISS L2/IP search
        k_tables = min(self.top_k_tables, len(self.table_names))
        D_tables, I_tables = self.table_index.search(self._normalize_vectors(query_emb), k_tables)
        
        retrieved_tables: List[str] = []
        for idx in I_tables[0]:
            if idx != -1 and idx < len(self.table_names):
                retrieved_tables.append(self.table_names[idx])
                
        logger.info(f"Retrieved top tables: {retrieved_tables}")
        
        # 3. For each retrieved table, rank columns in-memory using precomputed embeddings
        pruned_schema_lines: List[str] = []
        for table_name in retrieved_tables:
            table_details = self.db_metadata[table_name]
            all_cols = table_details["columns"]
            
            # Always keep Primary Keys and Foreign Keys for correct SQL JOINs
            kept_columns: List[Dict[str, Any]] = [c for c in all_cols if c["is_pk"] or c["is_fk"]]
            kept_names = {c["name"] for c in kept_columns}
            
            # Rank candidates (non-PK/FK columns)
            candidates = [c for c in all_cols if c["name"] not in kept_names]
            candidate_scores: List[tuple[float, Dict[str, Any]]] = []
            
            for col in candidates:
                col_name = col["name"]
                # Fetch precomputed embedding vector
                col_emb_list = self.column_embeddings.get(table_name, {}).get(col_name)
                
                if col_emb_list:
                    col_emb = np.array(col_emb_list, dtype=np.float32)
                    col_emb_norm = col_emb / (np.linalg.norm(col_emb) or 1.0)
                    
                    # Cosine similarity score
                    score = float(np.dot(query_emb_norm, col_emb_norm))
                    candidate_scores.append((score, col))
                else:
                    # Fallback to zero if embedding not found
                    candidate_scores.append((0.0, col))
                    
            # Sort by similarity score descending
            candidate_scores.sort(key=lambda x: x[0], reverse=True)
            
            # Take top M semantically matching columns
            top_m = min(self.top_m_columns, len(candidate_scores))
            for i in range(top_m):
                kept_columns.append(candidate_scores[i][1])
                
            # Maintain structural column ordering (as in original schema reflect)
            original_order = {col["name"]: idx for idx, col in enumerate(all_cols)}
            kept_columns.sort(key=lambda c: original_order[c["name"]])
            
            # Format table output
            pruned_schema_lines.append(f"Table: {table_name}")
            for col in kept_columns:
                pk_desc = " [PRIMARY KEY]" if col["is_pk"] else ""
                fk_desc = " [FOREIGN KEY]" if col["is_fk"] else ""
                pruned_schema_lines.append(f"  - {col['name']} ({col['type']}){pk_desc}{fk_desc}")
            pruned_schema_lines.append("")
            
        pruned_schema = "\n".join(pruned_schema_lines).strip()
        logger.info(f"Pruned schema constructed. Length: {len(pruned_schema)} characters.")
        return pruned_schema

# Singleton cache for loading SchemaRetriever dynamically in threads
_retriever_instance: Optional[SchemaRetriever] = None


def get_schema_retriever() -> SchemaRetriever:
    """Returns the global SchemaRetriever singleton instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = SchemaRetriever()
    return _retriever_instance
