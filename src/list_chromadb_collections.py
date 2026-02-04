"""
List all collections in a ChromaDB database.

This module provides functionality to discover and list all collections
in a ChromaDB database, showing the collection name and document count.

Usage:
    python src/list_chromadb_collections.py [options]
    
Examples:
    # Use default vectordb directory
    python src/list_chromadb_collections.py
    
    # Specify custom ChromaDB directory
    python src/list_chromadb_collections.py --db-path /path/to/chromadb
    
    # Show detailed information
    python src/list_chromadb_collections.py --verbose
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.api import ClientAPI


class ChromaDBCollectionLister:
    """List and inspect ChromaDB collections."""
    
    def __init__(self, persist_directory: str):
        """
        Initialize the collection lister.
        
        Args:
            persist_directory: Path to ChromaDB persistence directory
        """
        self.persist_directory = Path(persist_directory)
        self.client: ClientAPI | None = None
        
    def connect(self) -> bool:
        """
        Connect to the ChromaDB database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.persist_directory.exists():
                print(f"Error: Directory '{self.persist_directory}' does not exist.", file=sys.stderr)
                return False
            
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            return True
            
        except Exception as e:
            print(f"Error connecting to ChromaDB: {e}", file=sys.stderr)
            return False
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections with their document counts.
        
        Returns:
            List of dictionaries containing collection info
        """
        if not self.client:
            return []
        
        try:
            collections = self.client.list_collections()
            
            collection_info = []
            for collection in collections:
                # Get basic info
                total_count = collection.count()
                
                # Get content type breakdown
                content_type_counts = self._get_content_type_counts(collection)
                
                info = {
                    "name": collection.name,
                    "count": total_count,
                    "metadata": collection.metadata,
                    "content_types": content_type_counts
                }
                collection_info.append(info)
            
            return collection_info
            
        except Exception as e:
            print(f"Error listing collections: {e}", file=sys.stderr)
            return []
    
    def _get_content_type_counts(self, collection) -> Dict[str, int]:
        """
        Get count of documents by content_type.
        
        Args:
            collection: ChromaDB collection object
            
        Returns:
            Dictionary mapping content_type to count
        """
        try:
            # Get all documents with their metadata
            results = collection.get(
                include=["metadatas"]
            )
            
            # Count by content_type
            content_type_counts = {}
            for metadata in results["metadatas"]:
                if metadata and "content_type" in metadata:
                    content_type = metadata["content_type"]
                    content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
                else:
                    # Handle documents without content_type
                    content_type_counts["unknown"] = content_type_counts.get("unknown", 0) + 1
            
            return content_type_counts
            
        except Exception as e:
            print(f"Warning: Could not retrieve content types: {e}", file=sys.stderr)
            return {}
    
    def display_collections(self, verbose: bool = False):
        """
        Display collection information in a readable format.
        
        Args:
            verbose: If True, show additional metadata
        """
        collections = self.list_collections()
        
        if not collections:
            print("No collections found in the database.")
            return
        
        print(f"\nFound {len(collections)} collection(s) in '{self.persist_directory}':\n")
        print("-" * 80)
        
        for i, coll in enumerate(collections, 1):
            print(f"{i}. Collection: {coll['name']}")
            print(f"   Total Documents: {coll['count']:,}")
            
            # Show content type breakdown
            if coll['content_types']:
                print(f"   Document Types:")
                for content_type, count in sorted(coll['content_types'].items()):
                    print(f"      - {content_type}: {count:,}")
            
            if verbose and coll['metadata']:
                print(f"   Metadata: {coll['metadata']}")
            
            if i < len(collections):
                print()
        
        print("-" * 80)
        print(f"\nTotal documents across all collections: {sum(c['count'] for c in collections):,}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="List all collections in a ChromaDB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --db-path /path/to/chromadb
  %(prog)s --verbose
        """
    )
    
    parser.add_argument(
        "--db-path",
        type=str,
        default="./vectordb",
        help="Path to ChromaDB persistence directory (default: ./vectordb)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed information including metadata"
    )
    
    args = parser.parse_args()
    
    # Create lister and connect
    lister = ChromaDBCollectionLister(args.db_path)
    
    if not lister.connect():
        sys.exit(1)
    
    # Display collections
    lister.display_collections(verbose=args.verbose)


if __name__ == "__main__":
    main()
