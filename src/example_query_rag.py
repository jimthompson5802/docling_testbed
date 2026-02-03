"""
Example demonstrating how to query the ChromaDB RAG collection.

This script shows practical examples of different query patterns
and how to integrate ChromaDB queries into a RAG application.

Usage:
    python src/example_query_rag.py
"""

from query_chromadb import ChromaDBQuerier


def example_basic_search():
    """Example 1: Basic similarity search."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Similarity Search")
    print("=" * 80)
    
    querier = ChromaDBQuerier()
    
    # Simple query
    query = "net interest income"
    print(f"\nQuery: '{query}'")
    
    results = querier.similarity_search(query, n_results=3)
    
    # Display results
    print(f"\nTop 3 results:")
    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 - dist
        print(f"\n{i}. Page {meta['page']} - {meta['content_type']} (similarity: {similarity:.3f})")
        print(f"   {doc[:150]}...")


def example_table_search():
    """Example 2: Search only tables for structured data."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Table-Only Search")
    print("=" * 80)
    
    querier = ChromaDBQuerier()
    
    # Query for financial data in tables
    query = "consolidated statements of income"
    print(f"\nQuery: '{query}' (tables only)")
    
    results = querier.search_tables_only(query, n_results=3)
    
    print(f"\nTop 3 table results:")
    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 - dist
        print(f"\n{i}. Page {meta['page']} (similarity: {similarity:.3f})")
        print(f"   Content type: {meta['content_type']}")
        # Show first few lines of table
        lines = doc.split('\n')[:5]
        for line in lines:
            print(f"   {line}")
        if len(doc.split('\n')) > 5:
            print("   ...")


def example_filtered_search():
    """Example 3: Search with metadata filters."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Filtered Search by Content Type")
    print("=" * 80)
    
    querier = ChromaDBQuerier()
    
    # Search for section headers about risk
    query = "risk management"
    content_type = "section_header"
    print(f"\nQuery: '{query}'")
    print(f"Filter: content_type = {content_type}")
    
    results = querier.search_by_content_type(query, content_type, n_results=5)
    
    print(f"\nSection headers related to risk management:")
    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 - dist
        print(f"{i}. Page {meta['page']}: \"{doc}\" (similarity: {similarity:.3f})")


def example_page_range_search():
    """Example 4: Search within a specific page range."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Page Range Search")
    print("=" * 80)
    
    querier = ChromaDBQuerier()
    
    # Search in first 10 pages
    query = "quarterly report"
    page_min = 1
    page_max = 10
    print(f"\nQuery: '{query}'")
    print(f"Filter: pages {page_min}-{page_max}")
    
    results = querier.search_by_page_range(
        query, 
        page_min=page_min, 
        page_max=page_max,
        n_results=5
    )
    
    print(f"\nResults from pages {page_min}-{page_max}:")
    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 - dist
        print(f"\n{i}. Page {meta['page']} - {meta['content_type']} (similarity: {similarity:.3f})")
        print(f"   {doc[:120]}...")


def example_multi_query_rag():
    """Example 5: Multi-query RAG pattern."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Multi-Query RAG Pattern")
    print("=" * 80)
    
    querier = ChromaDBQuerier()
    
    # User question that requires multiple perspectives
    user_question = "What were the changes in revenue and what factors influenced them?"
    print(f"\nUser Question: '{user_question}'")
    
    # Break down into multiple queries
    queries = [
        "revenue changes",
        "factors affecting revenue",
        "net interest income components"
    ]
    
    print(f"\nDecomposed into {len(queries)} sub-queries:")
    
    all_contexts = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Sub-query: '{query}'")
        results = querier.similarity_search(query, n_results=2)
        
        # Collect contexts
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            context = {
                'text': doc,
                'page': meta['page'],
                'type': meta['content_type']
            }
            all_contexts.append(context)
            print(f"   - Found: Page {meta['page']}, {meta['content_type']}")
    
    print(f"\n✓ Retrieved {len(all_contexts)} context chunks")
    print("These would be combined and sent to an LLM for answer generation.")


def example_hybrid_search():
    """Example 6: Combining text search with table extraction."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Hybrid Search (Text + Tables)")
    print("=" * 80)
    
    querier = ChromaDBQuerier()
    
    topic = "credit losses"
    print(f"\nTopic: '{topic}'")
    print("Searching both narrative text and tables...")
    
    # Search text content
    print("\n1. Text content:")
    text_results = querier.search_by_content_type(topic, "text", n_results=2)
    for i, (doc, meta) in enumerate(zip(
        text_results['documents'][0],
        text_results['metadatas'][0]
    ), 1):
        print(f"   {i}. Page {meta['page']}: {doc[:100]}...")
    
    # Search tables
    print("\n2. Tables:")
    table_results = querier.search_tables_only(topic, n_results=2)
    for i, (doc, meta) in enumerate(zip(
        table_results['documents'][0],
        table_results['metadatas'][0]
    ), 1):
        print(f"   {i}. Page {meta['page']} - Table preview:")
        lines = doc.split('\n')[:3]
        for line in lines:
            print(f"      {line}")
    
    print("\n✓ Combined text and structured data for comprehensive answer")


def example_collection_stats():
    """Example 7: Get collection statistics."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Collection Statistics")
    print("=" * 80)
    
    querier = ChromaDBQuerier()
    stats = querier.get_collection_stats()
    
    print(f"\nCollection: {stats['collection_name']}")
    print(f"Total documents: {stats['total_documents']}")
    print(f"\nContent distribution (based on {stats['sample_size']} samples):")
    
    for content_type, count in sorted(
        stats['content_type_distribution'].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        pct = (count / stats['sample_size']) * 100
        bar = "█" * int(pct / 2)
        print(f"  {content_type:20s} {count:4d} ({pct:5.1f}%) {bar}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" ChromaDB RAG Query Examples")
    print("=" * 80)
    print("\nThis script demonstrates various query patterns for RAG applications.")
    print("Make sure you've run ingest_to_chromadb.py first!")
    
    try:
        # Run all examples
        example_basic_search()
        example_table_search()
        example_filtered_search()
        example_page_range_search()
        example_multi_query_rag()
        example_hybrid_search()
        example_collection_stats()
        
        print("\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Integrate these patterns into your RAG application")
        print("  2. Combine retrieved contexts with an LLM for answer generation")
        print("  3. Experiment with different query strategies")
        print("  4. Add re-ranking for improved retrieval quality")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure to run the ingestion script first:")
        print("  python src/ingest_to_chromadb.py data/10q_3q25_rag.json")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
