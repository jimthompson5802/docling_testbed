"""
Query utilities for ChromaDB vector database.

This module provides functions for querying the ChromaDB collection
with various search strategies and filters.

Usage:
    python src/query_chromadb.py "your query here" [options]
    
Examples:
    # Basic similarity search
    python src/query_chromadb.py "revenue growth"
    
    # Search with more results
    python src/query_chromadb.py "revenue growth" --n-results 10
    
    # Filter by content type
    python src/query_chromadb.py "financial data" --content-type table
    
    # Filter by page range
    python src/query_chromadb.py "risk factors" --page-min 10 --page-max 20
"""

import sys
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from chromadb_config import ChromaDBConfig


class ChromaDBQuerier:
    """Query interface for ChromaDB collections."""
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None
    ):
        """
        Initialize the querier.
        
        Args:
            collection_name: Name of the collection to query
            persist_directory: Path to ChromaDB persistence directory
        """
        self.config = ChromaDBConfig()
        print(f"Config '{self.config.PERSIST_DIRECTORY}, {self.config.COLLECTION_NAME}'")
        
        if collection_name:
            self.config.COLLECTION_NAME = collection_name
        if persist_directory:
            self.config.PERSIST_DIRECTORY = persist_directory
        
        # Initialize client
        self.client = chromadb.PersistentClient(
            path=str(self.config.get_persist_directory())
        )
        
        # Setup embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.config.EMBEDDING_MODEL
        )
        
        # Get collection
        try:
            self.collection = self.client.get_collection(
                name=self.config.COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            raise ValueError(
                f"Collection '{self.config.COLLECTION_NAME}' not found. "
                f"Please run ingest_to_chromadb.py first. Error: {e}"
            )
    
    def similarity_search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform similarity search.
        
        Args:
            query: Query text
            n_results: Number of results to return
            where: Metadata filter (e.g., {"content_type": "table"})
            where_document: Document content filter
            
        Returns:
            Dictionary with 'ids', 'documents', 'metadatas', 'distances'
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.config.MAX_RESULTS),
            where=where,
            where_document=where_document
        )
        
        return results
    
    def search_by_content_type(
        self,
        query: str,
        content_type: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search filtered by content type.
        
        Args:
            query: Query text
            content_type: Content type to filter by (e.g., 'table', 'text')
            n_results: Number of results to return
            
        Returns:
            Search results
        """
        where_filter = {"content_type": content_type}
        return self.similarity_search(query, n_results, where=where_filter)
    
    def search_tables_only(
        self,
        query: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search only table content.
        
        Args:
            query: Query text
            n_results: Number of results to return
            
        Returns:
            Search results
        """
        where_filter = {"is_table": True}
        return self.similarity_search(query, n_results, where=where_filter)
    
    def search_by_page_range(
        self,
        query: str,
        page_min: Optional[int] = None,
        page_max: Optional[int] = None,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search filtered by page range.
        
        Args:
            query: Query text
            page_min: Minimum page number (inclusive)
            page_max: Maximum page number (inclusive)
            n_results: Number of results to return
            
        Returns:
            Search results
        """
        where_filter = {}
        
        if page_min is not None and page_max is not None:
            where_filter = {
                "$and": [
                    {"page": {"$gte": page_min}},
                    {"page": {"$lte": page_max}}
                ]
            }
        elif page_min is not None:
            where_filter = {"page": {"$gte": page_min}}
        elif page_max is not None:
            where_filter = {"page": {"$lte": page_max}}
        
        return self.similarity_search(query, n_results, where=where_filter)
    
    def list_collections(self) -> List[str]:
        """
        List all collections in the ChromaDB database.
        
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        total_count = self.collection.count()
        
        # Get sample to analyze content types
        sample_size = min(1000, total_count)
        sample = self.collection.get(limit=sample_size)
        
        # Count content types
        content_type_counts = {}
        for meta in sample['metadatas']:
            ctype = meta['content_type']
            content_type_counts[ctype] = content_type_counts.get(ctype, 0) + 1
        
        return {
            'total_documents': total_count,
            'collection_name': self.config.COLLECTION_NAME,
            'content_type_distribution': content_type_counts,
            'sample_size': sample_size
        }


def format_results(results: Dict[str, Any], show_full: bool = False) -> None:
    """
    Format and print search results.
    
    Args:
        results: Results from ChromaDB query
        show_full: If True, show full text content
    """
    if not results['documents'] or not results['documents'][0]:
        print("No results found.")
        return
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    ids = results['ids'][0]
    
    print(f"\nFound {len(documents)} results:\n")
    print("=" * 80)
    
    for i, (doc_id, doc, meta, dist) in enumerate(zip(ids, documents, metadatas, distances), 1):
        print(f"\nResult {i} (similarity: {1 - dist:.4f})")
        print(f"ID: {doc_id}")
        print(f"Page: {meta.get('page', 'N/A')}")
        print(f"Content Type: {meta['content_type']}")
        print(f"Source: {meta['source']}")
        
        if meta.get('is_partial'):
            print(f"Chunk: {meta['chunk_index'] + 1}/{meta['total_chunks']} (partial)")
        
        print(f"\nContent:")
        if show_full:
            print(doc)
        else:
            # Show first 300 characters
            preview = doc[:300] + "..." if len(doc) > 300 else doc
            print(preview)
        
        print("<" * 40 + ">" * 40)


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Query ChromaDB vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all collections
  python src/query_chromadb.py --list
  
  # Basic search
  python src/query_chromadb.py "revenue growth"
  
  # Search with more results
  python src/query_chromadb.py "revenue growth" --n-results 10
  
  # Filter by content type
  python src/query_chromadb.py "financial data" --content-type table
  
  # Search only tables
  python src/query_chromadb.py "net interest income" --tables-only
  
  # Filter by page range
  python src/query_chromadb.py "risk factors" --page-min 10 --page-max 20
  
  # Show full content
  python src/query_chromadb.py "credit losses" --full
  
  # Collection statistics
  python src/query_chromadb.py --stats
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Query text (not needed for --stats)'
    )
    parser.add_argument(
        '--collection',
        help=f'Collection name (default: {ChromaDBConfig.COLLECTION_NAME})'
    )
    parser.add_argument(
        '--n-results',
        type=int,
        default=ChromaDBConfig.DEFAULT_N_RESULTS,
        help=f'Number of results to return (default: {ChromaDBConfig.DEFAULT_N_RESULTS})'
    )
    parser.add_argument(
        '--content-type',
        help='Filter by content type (e.g., table, text, section_header)'
    )
    parser.add_argument(
        '--tables-only',
        action='store_true',
        help='Search only table content'
    )
    parser.add_argument(
        '--page-min',
        type=int,
        help='Minimum page number (inclusive)'
    )
    parser.add_argument(
        '--page-max',
        type=int,
        help='Maximum page number (inclusive)'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Show full content (not truncated)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show collection statistics'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all collections in the database'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.stats and not args.list and not args.query:
        parser.error("Query text is required unless --stats or --list is specified")
    
    try:
        # Initialize querier
        querier = ChromaDBQuerier(collection_name=args.collection)
        
        if args.list:
            # List all collections
            print("Collections in ChromaDB:")
            print("=" * 80)
            try:
                collections = querier.list_collections()
                if collections:
                    for i, col_name in enumerate(collections, 1):
                        current = " (current)" if col_name == querier.config.COLLECTION_NAME else ""
                        print(f"{i}. {col_name}{current}")
                else:
                    print("No collections found.")
            except Exception as e:
                print(f"Error listing collections: {e}")
            return
        
        if args.stats:
            # Show statistics
            print(f"Collection Statistics")
            print("=" * 80)
            stats = querier.get_collection_stats()
            print(f"Collection: {stats['collection_name']}")
            print(f"Total documents: {stats['total_documents']}")
            print(f"\nContent type distribution (sample of {stats['sample_size']}):")
            for ctype, count in sorted(stats['content_type_distribution'].items()):
                pct = (count / stats['sample_size']) * 100
                print(f"  {ctype}: {count} ({pct:.1f}%)")
            return
        
        # Perform search
        print(f"Searching for: '{args.query}'")
        print(f"Collection: {querier.config.COLLECTION_NAME}")
        
        if args.tables_only:
            print("Filter: Tables only")
            results = querier.search_tables_only(args.query, args.n_results)
        elif args.content_type:
            print(f"Filter: Content type = {args.content_type}")
            results = querier.search_by_content_type(
                args.query, 
                args.content_type, 
                args.n_results
            )
        elif args.page_min is not None or args.page_max is not None:
            page_info = []
            if args.page_min:
                page_info.append(f"page >= {args.page_min}")
            if args.page_max:
                page_info.append(f"page <= {args.page_max}")
            print(f"Filter: {' AND '.join(page_info)}")
            results = querier.search_by_page_range(
                args.query,
                args.page_min,
                args.page_max,
                args.n_results
            )
        else:
            results = querier.similarity_search(args.query, args.n_results)
        
        # Format and display results
        format_results(results, show_full=args.full)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
