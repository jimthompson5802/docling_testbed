"""
Configuration settings for ChromaDB integration.

This module contains all configurable parameters for ChromaDB
ingestion and querying operations.
"""

from pathlib import Path
from typing import Optional


class ChromaDBConfig:
    """Configuration class for ChromaDB operations."""
    
    # Database settings
    PERSIST_DIRECTORY: str = "./vectordb"
    COLLECTION_NAME: str = "docling_rag_chunks"
    # PERSIST_DIRECTORY: str = "/Users/jim/Desktop/genai/open-webui/venv/lib/python3.11/site-packages/open_webui/data/vector_db"
    # COLLECTION_NAME: str = "knowledge-bases"
    
    # Embedding model settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    # Alternative models:
    # - "sentence-transformers/all-MiniLM-L6-v2" (faster, smaller)
    # - "sentence-transformers/all-mpnet-base-v2" (better quality, slower)
    
    # Ingestion settings
    BATCH_SIZE: int = 100  # Number of chunks to process at once
    SHOW_PROGRESS: bool = True
    
    # Query settings
    DEFAULT_N_RESULTS: int = 5  # Default number of results to return
    MAX_RESULTS: int = 50  # Maximum number of results allowed
    
    # Metadata field mappings for filtering
    METADATA_FIELDS = {
        "source": str,
        "content_type": str,
        "page": int,
        "chunk_index": int,
        "total_chunks": int,
        "is_partial": bool,
        # Computed fields
        "is_table": bool,
        "char_count": int,
    }
    
    # Content types that are considered tables
    TABLE_CONTENT_TYPES = {"table", "document_index"}
    
    @classmethod
    def get_persist_directory(cls) -> Path:
        """Get the persistence directory as a Path object."""
        return Path(cls.PERSIST_DIRECTORY)
    
    @classmethod
    def ensure_persist_directory(cls) -> None:
        """Create the persistence directory if it doesn't exist."""
        persist_dir = cls.get_persist_directory()
        persist_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Persistence directory ready: {persist_dir.absolute()}")


# Convenience function for custom configurations
def create_custom_config(
    persist_directory: Optional[str] = None,
    collection_name: Optional[str] = None,
    embedding_model: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> ChromaDBConfig:
    """
    Create a custom configuration instance.
    
    Args:
        persist_directory: Custom persistence directory path
        collection_name: Custom collection name
        embedding_model: Custom embedding model identifier
        batch_size: Custom batch size for ingestion
        
    Returns:
        ChromaDBConfig instance with custom settings
    """
    config = ChromaDBConfig()
    
    if persist_directory:
        config.PERSIST_DIRECTORY = persist_directory
    if collection_name:
        config.COLLECTION_NAME = collection_name
    if embedding_model:
        config.EMBEDDING_MODEL = embedding_model
    if batch_size:
        config.BATCH_SIZE = batch_size
    
    return config
