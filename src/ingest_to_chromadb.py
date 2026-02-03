"""
Ingest RAG-prepared JSON data into ChromaDB vector database.

This script loads chunks from a RAG JSON file and ingests them into
ChromaDB with proper embeddings and metadata for semantic search.

Usage:
    python src/ingest_to_chromadb.py <input.json> [options]
    
Examples:
    # Basic ingestion
    python src/ingest_to_chromadb.py data/10q_3q25_rag.json
    
    # Custom collection name
    python src/ingest_to_chromadb.py data/10q_3q25_rag.json --collection my_docs
    
    # Filter by content type
    python src/ingest_to_chromadb.py data/10q_3q25_rag.json --include-types table,text
    
    # Reset collection (clear existing data)
    python src/ingest_to_chromadb.py data/10q_3q25_rag.json --reset
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from tqdm import tqdm

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from chromadb_config import ChromaDBConfig


def load_rag_json(json_path: str) -> Dict[str, Any]:
    """
    Load RAG JSON file.
    
    Args:
        json_path: Path to the RAG JSON file
        
    Returns:
        Dictionary containing chunks and metadata
    """
    print(f"Loading RAG data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Loaded {data['total_chunks']} chunks")
    return data


def prepare_chunk_data(
    chunks: List[Dict[str, Any]], 
    include_types: Optional[Set[str]] = None,
    exclude_types: Optional[Set[str]] = None
) -> tuple[List[str], List[str], List[Dict[str, Any]]]:
    """
    Prepare chunk data for ChromaDB ingestion.
    
    Args:
        chunks: List of chunk dictionaries from RAG JSON
        include_types: If provided, only include these content types
        exclude_types: If provided, exclude these content types
        
    Returns:
        Tuple of (ids, documents, metadatas)
    """
    ids = []
    documents = []
    metadatas = []
    
    for chunk in chunks:
        content_type = chunk['metadata']['content_type']
        
        # Apply filters
        if include_types and content_type not in include_types:
            continue
        if exclude_types and content_type in exclude_types:
            continue
        
        # Use chunk_id as document ID (convert to string)
        chunk_id = f"chunk_{chunk['chunk_id']}"
        
        # Text content
        text = chunk['text']
        
        # Prepare metadata (ChromaDB requires flat dict with simple types)
        metadata = {
            'source': chunk['metadata']['source'],
            'content_type': content_type,
            'page': chunk['metadata'].get('page', 0) or 0,  # Handle None
            'chunk_index': chunk['metadata']['chunk_index'],
            'total_chunks': chunk['metadata']['total_chunks'],
            'is_partial': chunk['metadata']['is_partial'],
            # Computed fields
            'is_table': content_type in ChromaDBConfig.TABLE_CONTENT_TYPES,
            'char_count': len(text),
        }
        
        ids.append(chunk_id)
        documents.append(text)
        metadatas.append(metadata)
    
    return ids, documents, metadatas


def ingest_to_chromadb(
    json_path: str,
    collection_name: Optional[str] = None,
    reset: bool = False,
    include_types: Optional[Set[str]] = None,
    exclude_types: Optional[Set[str]] = None,
    batch_size: Optional[int] = None,
) -> None:
    """
    Ingest RAG chunks into ChromaDB.
    
    Args:
        json_path: Path to the RAG JSON file
        collection_name: Name of the ChromaDB collection (uses config default if None)
        reset: If True, delete existing collection before ingestion
        include_types: If provided, only include these content types
        exclude_types: If provided, exclude these content types
        batch_size: Batch size for ingestion (uses config default if None)
    """
    # Load configuration
    config = ChromaDBConfig()
    if collection_name:
        config.COLLECTION_NAME = collection_name
    if batch_size:
        config.BATCH_SIZE = batch_size
    
    # Ensure persistence directory exists
    config.ensure_persist_directory()
    
    # Load RAG data
    data = load_rag_json(json_path)
    chunks = data['chunks']
    
    # Initialize ChromaDB client
    print(f"\nInitializing ChromaDB client...")
    print(f"  Persistence directory: {config.get_persist_directory().absolute()}")
    print(f"  Collection name: {config.COLLECTION_NAME}")
    print(f"  Embedding model: {config.EMBEDDING_MODEL}")
    
    client = chromadb.PersistentClient(
        path=str(config.get_persist_directory())
    )
    
    # Setup embedding function
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL
    )
    
    # Get or create collection
    if reset:
        try:
            client.delete_collection(name=config.COLLECTION_NAME)
            print(f"✓ Deleted existing collection: {config.COLLECTION_NAME}")
        except Exception:
            pass  # Collection didn't exist
    
    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": f"RAG chunks from {Path(json_path).name}"}
    )
    
    print(f"✓ Collection ready: {config.COLLECTION_NAME}")
    print(f"  Existing documents: {collection.count()}")
    
    # Prepare data
    print(f"\nPreparing chunks for ingestion...")
    ids, documents, metadatas = prepare_chunk_data(
        chunks, 
        include_types=include_types,
        exclude_types=exclude_types
    )
    
    if not documents:
        print("⚠ No chunks to ingest after applying filters")
        return
    
    print(f"✓ Prepared {len(documents)} chunks")
    
    # Show content type distribution
    content_type_counts = {}
    for meta in metadatas:
        ctype = meta['content_type']
        content_type_counts[ctype] = content_type_counts.get(ctype, 0) + 1
    
    print(f"\nContent type distribution:")
    for ctype, count in sorted(content_type_counts.items()):
        print(f"  - {ctype}: {count}")
    
    # Batch ingestion with progress bar
    print(f"\nIngesting chunks (batch size: {config.BATCH_SIZE})...")
    
    total_batches = (len(documents) + config.BATCH_SIZE - 1) // config.BATCH_SIZE
    
    with tqdm(total=len(documents), desc="Ingesting", unit="chunk") as pbar:
        for i in range(0, len(documents), config.BATCH_SIZE):
            batch_end = min(i + config.BATCH_SIZE, len(documents))
            
            batch_ids = ids[i:batch_end]
            batch_documents = documents[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            
            try:
                collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
                pbar.update(len(batch_ids))
            except Exception as e:
                print(f"\n⚠ Error ingesting batch {i//config.BATCH_SIZE + 1}: {e}")
                # Continue with next batch
                continue
    
    # Final statistics
    final_count = collection.count()
    print(f"\n✓ Ingestion complete!")
    print(f"  Total documents in collection: {final_count}")
    print(f"  Collection name: {config.COLLECTION_NAME}")
    print(f"  Persistence directory: {config.get_persist_directory().absolute()}")
    
    # Show sample
    print(f"\nSample query test...")
    try:
        results = collection.query(
            query_texts=["financial results"],
            n_results=1
        )
        if results['documents'] and results['documents'][0]:
            sample_doc = results['documents'][0][0]
            sample_meta = results['metadatas'][0][0]
            print(f"  Query: 'financial results'")
            print(f"  Top result (page {sample_meta['page']}, {sample_meta['content_type']}):")
            print(f"    {sample_doc[:150]}...")
    except Exception as e:
        print(f"  Sample query failed: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest RAG JSON data into ChromaDB vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic ingestion
  python src/ingest_to_chromadb.py data/10q_3q25_rag.json
  
  # Custom collection name
  python src/ingest_to_chromadb.py data/10q_3q25_rag.json --collection my_docs
  
  # Ingest only tables
  python src/ingest_to_chromadb.py data/10q_3q25_rag.json --include-types table
  
  # Exclude pictures and captions
  python src/ingest_to_chromadb.py data/10q_3q25_rag.json --exclude-types picture,caption
  
  # Reset collection (clear existing data)
  python src/ingest_to_chromadb.py data/10q_3q25_rag.json --reset
        """
    )
    
    parser.add_argument(
        'json_path',
        help='Path to the RAG JSON file'
    )
    parser.add_argument(
        '--collection',
        help=f'Collection name (default: {ChromaDBConfig.COLLECTION_NAME})'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Delete existing collection before ingestion'
    )
    parser.add_argument(
        '--include-types',
        help='Comma-separated list of content types to include (e.g., table,text)'
    )
    parser.add_argument(
        '--exclude-types',
        help='Comma-separated list of content types to exclude'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        help=f'Batch size for ingestion (default: {ChromaDBConfig.BATCH_SIZE})'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.json_path).exists():
        print(f"Error: File not found: {args.json_path}")
        sys.exit(1)
    
    # Parse content type filters
    include_types = None
    if args.include_types:
        include_types = set(t.strip() for t in args.include_types.split(','))
    
    exclude_types = None
    if args.exclude_types:
        exclude_types = set(t.strip() for t in args.exclude_types.split(','))
    
    # Run ingestion
    try:
        ingest_to_chromadb(
            json_path=args.json_path,
            collection_name=args.collection,
            reset=args.reset,
            include_types=include_types,
            exclude_types=exclude_types,
            batch_size=args.batch_size
        )
    except KeyboardInterrupt:
        print("\n\nIngestion cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
